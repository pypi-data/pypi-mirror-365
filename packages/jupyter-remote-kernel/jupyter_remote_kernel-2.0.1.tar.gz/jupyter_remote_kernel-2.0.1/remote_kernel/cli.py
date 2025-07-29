import sys, os, json, time, signal, threading
import subprocess, shutil
from sshtunnel import SSHTunnelForwarder
from paramiko import SSHClient, AutoAddPolicy

from remote_kernel import PYTHON_BIN, REMOTE_CONN_DIR, PID_FILE, KERNELS_DIR, LOG_FILE
from remote_kernel import log, parse_endpoint, usage, __version__
from remote_kernel.connect import connect_kernel, add_kernel, list_kernels, delete_kernel


def copy_file_paramiko(conn_file, endpoint, port, k=None):
    """Copy connection file to remote via Paramiko SFTP."""
    user, hostaddr = endpoint.split("@")
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(hostaddr, port=port or 22, username=user)
    sftp = ssh.open_sftp()
    remote_conn_file = f"{REMOTE_CONN_DIR}/{os.path.basename(conn_file)}"
    log(f"Copying {os.path.basename(conn_file)} -> {hostaddr}:{remote_conn_file}", k)
    sftp.put(conn_file, remote_conn_file)
    sftp.close()
    ssh.close()
    return remote_conn_file


def ensure_ipykernel(endpoint, port, k=None):
    """Ensure ipykernel is installed on remote host."""
    user, hostaddr = endpoint.split("@")
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(hostaddr, port=port or 22, username=user)
    cmd = f"{PYTHON_BIN} -m ipykernel --version || {PYTHON_BIN} -m pip install --quiet ipykernel"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()
    log(f"Ensured ipykernel on {hostaddr}", k)
    ssh.close()


def start_ipykernel(endpoint, port, remote_conn_file, k=None):
    """Launch ipykernel remotely via Paramiko."""
    user, hostaddr = endpoint.split("@")
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(hostaddr, port=port or 22, username=user)
    cmd = f"{PYTHON_BIN} -m ipykernel_launcher -f {remote_conn_file}"
    log(f"Launching ipykernel on {hostaddr}", k)
    transport = ssh.get_transport()
    channel = transport.open_session()
    channel.exec_command(cmd)
    return ssh, channel


def tunnel_thread(server, kernel_short):
    """Keep SSHTunnelForwarder alive."""
    log(f"Tunnel thread running for {kernel_short}")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        log(f"Tunnel interrupted for {kernel_short}")
    finally:
        server.stop()
        log(f"Tunnel stopped for {kernel_short}")


def ipykernel_thread(endpoint, port, remote_conn_file, kernel_short):
    """Run and monitor ipykernel."""
    ssh, channel = start_ipykernel(endpoint, port, remote_conn_file, kernel_short)
    try:
        while True:
            if channel.exit_status_ready():
                log(f"Kernel on {endpoint} exited", kernel_short)
                break
            time.sleep(2)
    except KeyboardInterrupt:
        log(f"Kernel interrupted on {endpoint}", kernel_short)
    finally:
        channel.close()
        ssh.close()
        log(f"Closed ipykernel for {endpoint}", kernel_short)


def start_kernel(endpoint, conn_file, jump=None):
    if not os.path.exists(conn_file):
        log(f"ERROR: Connection file not found: {conn_file}")
        sys.exit(1)

    conn_file_base = os.path.basename(conn_file)
    kernel_short = conn_file_base.split("kernel-")[1].split("-")[0]

    host, port = parse_endpoint(endpoint)
    with open(conn_file) as f:
        cfg = json.load(f)
    ports = [cfg[k] for k in ("shell_port", "iopub_port", "stdin_port", "control_port", "hb_port")]

    # Step 1: Copy connection file
    remote_conn_file = copy_file_paramiko(conn_file, endpoint, port, kernel_short)

    # Step 2: Ensure ipykernel
    ensure_ipykernel(endpoint, port, kernel_short)

    # Step 3: Start SSH tunnel (forward all ports)
    user, hostaddr = endpoint.split("@")
    server = SSHTunnelForwarder(
        (hostaddr, port or 22),
        ssh_username=user,
        remote_bind_addresses=[("127.0.0.1", p) for p in ports],
        local_bind_addresses=[("127.0.0.1", p) for p in ports],
        set_keepalive=5
    )
    server.start()
    log(f"SSH tunnel ready (ports: {ports})", kernel_short)

    # Step 4: Start threads for tunnel and ipykernel
    t_tunnel = threading.Thread(target=tunnel_thread, args=(server, kernel_short))
    t_kernel = threading.Thread(target=ipykernel_thread, args=(endpoint, port, remote_conn_file, kernel_short))
    t_tunnel.start()
    t_kernel.start()

    # Record thread IDs (not PIDs)
    with open(PID_FILE, "w") as pf:
        pf.write(f"{t_tunnel.ident},{t_kernel.ident}")

    try:
        t_tunnel.join()
        t_kernel.join()
    except KeyboardInterrupt:
        log(f"Interrupted. Cleaning up {kernel_short}")
        server.stop()


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
        jump = sys.argv[sys.argv.index("-J") + 1] if "-J" in sys.argv else None
        add_kernel(endpoint, name, jump)
        return

    if "list" in sys.argv:
        list_kernels()
        return

    if "delete" in sys.argv:
        if len(sys.argv) < 3:
            print("Usage: remote_kernel delete <slug-or-display-name>")
            sys.exit(1)
        delete_kernel(sys.argv[2])
        return

    if "connect" in sys.argv:
        connect_kernel(sys.argv[2] if len(sys.argv) > 2 else None)
        return

    if "--kill" in sys.argv:
        kill_kernel()
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

