#!/home/ubuntu/conda3/bin/python
import sys, os, json, subprocess, signal, shutil, time

PYTHON_BIN = os.environ.get("REMOTE_KERNEL_PYTHON", "python")
REMOTE_CONN_DIR = "/tmp"
PID_FILE = "/tmp/remote_kernel.pid"
KERNELS_DIR = os.path.expanduser("~/.local/share/jupyter/kernels")
LOG_FILE = "/tmp/remote_kernel.log"

def log(msg, k=None):
    """Write timestamped logs, optionally tagged with kernel short ID."""
    prefix = f"[{k}] " if k else ""
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {prefix}{msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def parse_endpoint(endpoint):
    if ":" in endpoint:
        host, port = endpoint.split(":", 1)
        return host, int(port)
    return endpoint, None

def copy_file_scp(src, endpoint, port, jump, dest, k=None):
    src_base = os.path.basename(src)
    log(f"Copying {src_base} -> {endpoint}", k)
    cmd = ["scp"]
    if jump:
        cmd += ["-J", str(jump)]        
    if port:
        cmd += ["-P", str(port)]
    cmd += [src, f"{endpoint}:{dest}"]
    subprocess.run(cmd, check=True)

def ensure_ipykernel(host, port, python_bin, k=None):
    cmd = f"{python_bin} -m ipykernel --version || {python_bin} -m pip install --quiet ipykernel"
    ssh_cmd = ["ssh"]
    if port:
        ssh_cmd += ["-p", str(port)]
    ssh_cmd += [host, cmd]
    log(f"Ensuring ipykernel on {host}", k)
    subprocess.run(ssh_cmd, check=True)

def start_kernel(endpoint, conn_file, jump):
    if not os.path.exists(conn_file):
        log(f"ERROR: Connection file not found: {conn_file}")
        sys.exit(1)

    # Derive short kernel ID
    conn_file_base = os.path.basename(conn_file)
    kernel_short = conn_file_base.split("kernel-")[1].split("-")[0]

    host, port = parse_endpoint(endpoint)
    with open(conn_file) as f:
        cfg = json.load(f)
    ports = [cfg[k] for k in ("shell_port", "iopub_port", "stdin_port", "control_port", "hb_port")]

    log(f"Starting kernel for {endpoint}", kernel_short)

    remote_conn_file = f"{REMOTE_CONN_DIR}/{os.path.basename(conn_file)}"
    copy_file_scp(conn_file, host, port, jump, remote_conn_file, kernel_short)
    ensure_ipykernel(host, port, PYTHON_BIN, kernel_short)

    # Prepare SSH tunnels
    forwards = []
    for p in ports:
        forwards += ["-L", f"{p}:localhost:{p}"]

    tunnel_cmd = ["ssh", "-N", "-o", "ExitOnForwardFailure=yes", "-o", "ServerAliveInterval=5"]

    if jump:
        tunnel_cmd +=  ["-J", str(jump)]
    if port:
        tunnel_cmd +=  ["-p", str(port)]
    tunnel_cmd += forwards + [host]

    kernel_cmd = ["ssh"]
    if jump:
        kernel_cmd +=  ["-J", str(jump)]
    if port:
        kernel_cmd += ["-p", str(port)]
    kernel_cmd += [host, f"{PYTHON_BIN} -m ipykernel_launcher -f {remote_conn_file}"]

    # Logs per kernel
    tunnel_log = open(f"/tmp/remote_kernel_tunnel-{kernel_short}.log", "ab")
    kernel_log = open(f"/tmp/remote_kernel_session-{kernel_short}.log", "ab")

    log(f"Starting SSH tunnel (ports: {ports})", kernel_short)
    tunnel_proc = subprocess.Popen(tunnel_cmd, stdout=tunnel_log, stderr=tunnel_log)

    log(f"Starting ipykernel on {host} using {PYTHON_BIN}", kernel_short)
    kernel_proc = subprocess.Popen(kernel_cmd, stdout=kernel_log, stderr=kernel_log)

    with open(PID_FILE, "w") as pf:
        pf.write(f"{tunnel_proc.pid},{kernel_proc.pid}")

    log(f"Kernel running. Tunnel PID={tunnel_proc.pid}, Kernel PID={kernel_proc.pid}", kernel_short)

    try:
        kernel_proc.wait()
    except KeyboardInterrupt:
        log("Interrupted. Shutting down kernel and tunnel.", kernel_short)
    finally:
        cleanup_processes([tunnel_proc, kernel_proc], kernel_short)
    log(f"Kernel for {endpoint} exits", kernel_short)

def cleanup_processes(procs, k=None):
    for p in procs:
        try:
            p.terminate()
            p.wait(timeout=5)
        except Exception:
            pass
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
    log("All processes terminated.", k)

def kill_kernel():
    if not os.path.exists(PID_FILE):
        print("[remote_kernel] No running tunnel found.")
        return
    with open(PID_FILE) as pf:
        pid_line = pf.read().strip()
    for pid_str in pid_line.split(","):
        try:
            pid = int(pid_str)
            os.kill(pid, signal.SIGTERM)
            print(f"[remote_kernel] Terminated process PID {pid}")
        except ProcessLookupError:
            print(f"[remote_kernel] Process PID {pid_str} already stopped")
    os.remove(PID_FILE)

def add_kernel(endpoint, name, jump):
    try:
        abs_path = subprocess.check_output(["which", "remote_kernel"], text=True).strip()
    except subprocess.CalledProcessError:
        print("[remote_kernel] ERROR: 'remote_kernel' not in PATH.")
        sys.exit(1)

    slug = name.lower().replace(" ", "_")
    kernel_dir = os.path.join(KERNELS_DIR, slug)
    os.makedirs(kernel_dir, exist_ok=True)

    argv = None
    if jump:
        argv = [abs_path, "--endpoint", endpoint, "-J", jump , "-f", "{connection_file}"]
    else:
        argv = [abs_path, "--endpoint", endpoint, "-f", "{connection_file}"]
    
    kernel_json = {
        "argv": argv,
        "display_name": name,
        "language": "python"
    }

    with open(os.path.join(kernel_dir, "kernel.json"), "w") as f:
        json.dump(kernel_json, f, indent=2)
    print(f"[remote_kernel] Added kernel: {name} ({endpoint})")
    print(f"  Location: {kernel_dir}")

def list_kernels():
    if not os.path.exists(KERNELS_DIR):
        print("[remote_kernel] No kernels installed.")
        return
    for slug in os.listdir(KERNELS_DIR):
        kdir = os.path.join(KERNELS_DIR, slug)
        kjson = os.path.join(kdir, "kernel.json")
        if not os.path.isfile(kjson):
            continue
        try:
            with open(kjson) as f:
                data = json.load(f)
            name = data.get("display_name", slug)
            argv = data.get("argv", [])
            endpoint = argv[argv.index("--endpoint") + 1] if "--endpoint" in argv else None
            print(f"slug: {slug}\n  name: {name}\n  endpoint: {endpoint or 'N/A'}\n---")
        except Exception:
            continue

def delete_kernel(name_or_slug):
    slug = name_or_slug.lower().replace(" ", "_")
    kernel_dir = os.path.join(KERNELS_DIR, slug)
    if not os.path.exists(kernel_dir):
        print(f"[remote_kernel] Kernel '{name_or_slug}' not found.")
        return
    shutil.rmtree(kernel_dir)
    print(f"[remote_kernel] Deleted kernel '{name_or_slug}'.")

def main():
    jump = None
    if "add" in sys.argv:
        if "--endpoint" not in sys.argv or "--name" not in sys.argv:
            print("Usage: remote_kernel add --endpoint <user@host[:port]> [-J user@ip:port] --name <Display Name>")
            sys.exit(1)
        endpoint = sys.argv[sys.argv.index("--endpoint") + 1]
        name = sys.argv[sys.argv.index("--name") + 1]
        if "-J" in sys.argv:
            jump = sys.argv[sys.argv.index("-J") + 1]
        add_kernel(endpoint, name, jump)
        return

    if "list" in sys.argv:
        list_kernels()
        return

    if "delete" in sys.argv:
        if len(sys.argv) < 3:
            print("Usage: remote_kernel delete <slug-or-display-name>")
            sys.exit(1)
        target = sys.argv[2]
        delete_kernel(target)
        return

    if "--kill" in sys.argv:
        kill_kernel()
        return

    if "--endpoint" not in sys.argv or "-f" not in sys.argv:
        print("Usage: remote_kernel --endpoint <user@host[:port]> [-J user@ip:port] -f <connection_file>")
        sys.exit(1)

    if "-J" in sys.argv:
        jump = sys.argv[sys.argv.index("-J") + 1]
    
    endpoint = sys.argv[sys.argv.index("--endpoint") + 1]
    conn_file = sys.argv[sys.argv.index("-f") + 1]
    start_kernel(endpoint, conn_file, jump)

if __name__ == "__main__":
    main()
