import sys, os, json
import paramiko
from sshtunnel import SSHTunnelForwarder

from remote_kernel import parse_endpoint, log, KERNELS_DIR

def list_kernels(show_all=False):
    """List all registered kernels."""
    if not os.path.exists(KERNELS_DIR):
        print("[remote_kernel] No kernels installed.")
        return []

    results = []
    for slug in os.listdir(KERNELS_DIR):
        kjson = os.path.join(KERNELS_DIR, slug, "kernel.json")
        if not os.path.isfile(kjson):
            continue
        try:
            with open(kjson) as f:
                data = json.load(f)
            name = data.get("display_name", slug)
            argv = data.get("argv", [])
            endpoint = argv[argv.index("--endpoint") + 1] if "--endpoint" in argv else None
            jump = argv[argv.index("-J") + 1] if "-J" in argv else None
            if endpoint:
                results.append((slug, name, endpoint, jump))
                if show_all:
                    print(f" - {slug}:\t{endpoint}{' via ' + jump if jump else ''}")
        except Exception:
            continue
    return results


def connect_kernel(target_slug=None):
    """Connect interactively to a remote host using Paramiko (instead of `ssh`)."""
    kernels = list_kernels(show_all=False)
    if not kernels:
        print("[remote_kernel] No kernels registered.")
        return

    if not target_slug:
        print("[remote_kernel] Available kernels:")
        for slug, name, endpoint, jump in kernels:
            print(f"  {slug:20} {endpoint}{' via ' + jump if jump else ''}")
        print("\nUse: remote_kernel connect <slug-or-display-name>")
        return

    # Normalize target slug
    target_slug = target_slug.lower().replace(" ", "_")
    for slug, name, endpoint, jump in kernels:
        if target_slug in (slug, name.lower().replace(" ", "_")):
            host, port = parse_endpoint(endpoint)
            user, hostaddr = host.split("@")

            # Set up optional jump host
            jump_client = None
            sock = None
            if jump:
                j_user, j_hostport = jump.split("@")
                j_host, j_port = (j_hostport.split(":") + ["22"])[:2]
                j_port = int(j_port)

                jump_client = paramiko.SSHClient()
                jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                jump_client.connect(j_host, port=j_port, username=j_user)

                sock = jump_client.get_transport().open_channel(
                    "direct-tcpip", (hostaddr, port or 22), ("127.0.0.1", 0)
                )

            # Connect to the actual target
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostaddr, port=port or 22, username=user, sock=sock)

            # Start an interactive shell
            chan = ssh.invoke_shell()
            print(f"[remote_kernel] Connected to {endpoint} {'via ' + jump if jump else ''}.")
            print("Press Ctrl+D to exit.")
            try:
                import sys, select, termios, tty
                old_tty = termios.tcgetattr(sys.stdin)
                tty.setraw(sys.stdin.fileno())
                tty.setcbreak(sys.stdin.fileno())
                while True:
                    r, w, e = select.select([chan, sys.stdin], [], [])
                    if chan in r:
                        data = chan.recv(1024)
                        if not data:
                            break
                        sys.stdout.write(data.decode())
                        sys.stdout.flush()
                    if sys.stdin in r:
                        x = sys.stdin.read(1)
                        if not x:
                            break
                        chan.send(x)
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
                chan.close()
                ssh.close()
                if jump_client:
                    jump_client.close()
            return

    print(f"[remote_kernel] Kernel '{target_slug}' not found.")


def add_kernel(endpoint, name, jump):
    import subprocess
    try:
        abs_path = subprocess.check_output(["which", "remote_kernel"], text=True).strip()
    except subprocess.CalledProcessError:
        print("[remote_kernel] ERROR: 'remote_kernel' not in PATH.")
        sys.exit(1)

    slug = name.lower().replace(" ", "_")
    kernel_dir = os.path.join(KERNELS_DIR, slug)
    os.makedirs(kernel_dir, exist_ok=True)

    argv = [abs_path, "--endpoint", endpoint]
    if jump:
        argv += ["-J", jump]
    argv += ["-f", "{connection_file}"]

    kernel_json = {
        "argv": argv,
        "display_name": name,
        "language": "python"
    }

    with open(os.path.join(kernel_dir, "kernel.json"), "w") as f:
        json.dump(kernel_json, f, indent=2)
    print(f"[remote_kernel] Added kernel: {name} ({endpoint})")
    print(f"  Location: {kernel_dir}")

def delete_kernel(name_or_slug):
    slug = name_or_slug.lower().replace(" ", "_")
    kernel_dir = os.path.join(KERNELS_DIR, slug)
    if not os.path.exists(kernel_dir):
        print(f"[remote_kernel] Kernel '{name_or_slug}' not found.")
        return
    shutil.rmtree(kernel_dir)
    print(f"[remote_kernel] Deleted kernel '{name_or_slug}'.")
