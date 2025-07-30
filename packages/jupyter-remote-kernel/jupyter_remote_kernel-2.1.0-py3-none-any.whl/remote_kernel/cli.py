#!/usr/bin/env python3
import sys, os, json, shutil, time
from remote_kernel import REMOTE_CONN_DIR, KERNELS_DIR, log, usage, version, __version__
from remote_kernel.ssh_wrapper import SSHConfig, SSHWrapper

def start_kernel(endpoint, conn_file, jump=None):
    if not os.path.exists(conn_file):
        log(f"ERROR: Connection file not found {conn_file}")
        return

    with open(conn_file) as f:
        cfg = json.load(f)

    ports = [cfg[k] for k in ("shell_port", "iopub_port", "stdin_port", "control_port", "hb_port")]
    print(f"Starting remote kernel with ports: {ports}")

    ssh_cfg = SSHConfig(endpoint=endpoint, jump=jump)
    sshw = SSHWrapper(ssh_cfg)

    remote_conn_file = f"{REMOTE_CONN_DIR}/{os.path.basename(conn_file)}"
    if not sshw.copy(conn_file, remote_conn_file):
        log("Failed to copy connection file to remote host")
        return

    cmd = f"python -m ipykernel_launcher -f {remote_conn_file}"
    print(f"Starting remote kernel with command: {cmd}")

    retries = 0
    while retries < 3:
        try:
            out, err = sshw.exec_with_tunnels(cmd, ports)

            # If no output and no error, treat as transient failure and retry
            if not out and not err:
                retries += 1
                log(f"Kernel did not respond, retry {retries}/3...")
                time.sleep(5)
                continue

            # If error or still no output after retry, cleanup connection file
            if err or not out:
                log(f"Kernel failed, cleaning up remote file {remote_conn_file}")
                try:
                    sshw.exec(f"rm -f {remote_conn_file}")
                except Exception:
                    pass
            break

        except Exception as e:
            log(f"Failed to start remote kernel: {e}")
            retries += 1
            time.sleep(5)
            if retries == 3:
                try:
                    sshw.exec(f"rm -f {remote_conn_file}")
                except Exception:
                    pass
            continue

def add_kernel(endpoint, name, jump=None):
    abs_path = sys.argv[0]
    slug = name.lower().replace(" ", "_")
    kernel_dir = os.path.join(KERNELS_DIR, slug)
    os.makedirs(kernel_dir, exist_ok=True)
    argv = [abs_path, "--endpoint", endpoint, "-f", "{connection_file}"]
    if jump:
        argv += ["-J", jump]
    kernel_json = {
        "argv": argv,
        "display_name": name,
        "language": "python"
    }
    with open(os.path.join(kernel_dir, "kernel.json"), "w") as f:
        json.dump(kernel_json, f, indent=2)
    log(f"Added kernel {name} ({endpoint})")
    log(f"Location: {kernel_dir}")

def list_kernels():
    """List only kernels that have an endpoint, formatted as a clean table."""
    if not os.path.exists(KERNELS_DIR):
        log("No kernels installed")
        return

    print(f"{'slug':<10}| {'name':<15}| endpoint")
    print("-" * 60)
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
            if not endpoint:
                continue
            jump = argv[argv.index("-J") + 1] if "-J" in argv else None
            details = f"{endpoint}{f' -J {jump}' if jump else ''}"
            print(f"{slug:<10}| {name:<15}| {details}")
        except Exception as e:
            log(f"Failed to read kernel spec {kjson}: {e}")
    print("---")

def delete_kernel(name_or_slug):
    slug = name_or_slug.lower().replace(" ", "_")
    kernel_dir = os.path.join(KERNELS_DIR, slug)
    if not os.path.exists(kernel_dir):
        log(f"Kernel '{name_or_slug}' not found")
        return
    try:
        shutil.rmtree(kernel_dir)
        log(f"Deleted kernel '{name_or_slug}'")
    except Exception as e:
        log(f"Failed to delete kernel '{name_or_slug}': {e}")

def connect_kernel(name_or_slug=None):
    """Connect interactively to a kernel via SSHWrapper."""
    if not name_or_slug:
        list_kernels()
        log("Use: remote_kernel connect <slug-or-name>")
        return

    target_slug = name_or_slug.lower().replace(" ", "_")
    kernel_dir = os.path.join(KERNELS_DIR, target_slug)
    kernel_json = os.path.join(kernel_dir, "kernel.json")

    if not os.path.exists(kernel_json):
        log(f"Kernel '{name_or_slug}' not found")
        return

    try:
        with open(kernel_json) as f:
            data = json.load(f)
        argv = data.get("argv", [])
        endpoint = argv[argv.index("--endpoint") + 1] if "--endpoint" in argv else None
        jump = argv[argv.index("-J") + 1] if "-J" in argv else None
    except Exception as e:
        log(f"Failed to load kernel spec: {e}")
        return

    if not endpoint:
        log(f"Kernel '{name_or_slug}' has no valid endpoint")
        return

    ssh_cfg = SSHConfig(endpoint=endpoint, jump=jump)
    sshw = SSHWrapper(ssh_cfg)
    log(f"Connecting to {endpoint}{f' -J {jump}' if jump else ''}...")
    sshw.connect()

def main():
    if len(sys.argv) < 2:
        usage()
        return
    if "-v" in sys.argv or "--version" in sys.argv:
        version()
        return
    if "add" in sys.argv:
        if "--endpoint" not in sys.argv or "--name" not in sys.argv:
            usage()
            return
        endpoint = sys.argv[sys.argv.index("--endpoint") + 1]
        name = sys.argv[sys.argv.index("--name") + 1]
        jump = sys.argv[sys.argv.index("-J") + 1] if "-J" in sys.argv else None
        add_kernel(endpoint, name, jump)
        return
    if "list" in sys.argv:
        list_kernels()
        return
    if "delete" in sys.argv:
        if len(sys.argv) < 3:
            usage()
            return
        delete_kernel(sys.argv[2])
        return
    if "connect" in sys.argv:
        target = sys.argv[2] if len(sys.argv) > 2 else None
        connect_kernel(target)
        return
    if "--endpoint" not in sys.argv or "-f" not in sys.argv:
        usage()
        return
    endpoint = sys.argv[sys.argv.index("--endpoint") + 1]
    conn_file = sys.argv[sys.argv.index("-f") + 1]
    jump = sys.argv[sys.argv.index("-J") + 1] if "-J" in sys.argv else None
    start_kernel(endpoint, conn_file, jump)

if __name__ == "__main__":
    main()