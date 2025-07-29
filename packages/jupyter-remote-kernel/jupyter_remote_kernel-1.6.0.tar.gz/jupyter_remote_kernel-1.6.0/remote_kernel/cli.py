import sys, os, json, subprocess, signal, shutil, time
from remote_kernel import (
    PYTHON_BIN, REMOTE_CONN_DIR, PID_FILE, KERNELS_DIR, LOG_FILE,
    log, parse_endpoint, __version__, usage,
    connect_kernel, add_kernel, list_kernels, delete_kernel
)

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

    # SSH tunnels for ports
    forwards = []
    for p in ports:
        forwards += ["-L", f"{p}:localhost:{p}"]

    tunnel_cmd = ["ssh", "-N", "-o", "ExitOnForwardFailure=yes", "-o", "ServerAliveInterval=5"]
    if jump:
        tunnel_cmd += ["-J", str(jump)]
    if port:
        tunnel_cmd += ["-p", str(port)]
    tunnel_cmd += forwards + [host]

    kernel_cmd = ["ssh"]
    if jump:
        kernel_cmd += ["-J", str(jump)]
    if port:
        kernel_cmd += ["-p", str(port)]
    kernel_cmd += [host, f"{PYTHON_BIN} -m ipykernel_launcher -f {remote_conn_file}"]

    # Logs
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

def main():
    jump = None
    if "-h" in sys.argv:
        usage()
        return

    if "-v" in sys.argv or "--version" in sys.argv:
        print(f"version: {__version__}")
        return

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

    if "connect" in sys.argv:
        target = sys.argv[2] if len(sys.argv) > 2 else None
        connect_kernel(target)
        return

    if "--kill" in sys.argv:
        kill_kernel()
        return

    if "--endpoint" not in sys.argv or "-f" not in sys.argv:
        usage()
        return

    if "-J" in sys.argv:
        jump = sys.argv[sys.argv.index("-J") + 1]

    log("Starting kernel launcher")
    endpoint = sys.argv[sys.argv.index("--endpoint") + 1]
    conn_file = sys.argv[sys.argv.index("-f") + 1]
    start_kernel(endpoint, conn_file, jump)

if __name__ == "__main__":
    main()
