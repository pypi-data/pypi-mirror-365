__version__ = '2.0.2'

import os, time

# Default remote Python (can be overridden by env var)
PYTHON_BIN = os.environ.get("REMOTE_KERNEL_PYTHON", "python")

# Remote and local paths
REMOTE_CONN_DIR = "/tmp"
PID_FILE = "/tmp/remote_kernel.pid"
LOG_FILE = "/tmp/remote_kernel.log"

# Kernel spec directory (for Jupyter)
KERNELS_DIR = os.path.expanduser("~/.local/share/jupyter/kernels")

def usage():
    print("Usage: remote_kernel --endpoint <user@host[:port]> [-J user@ip:port] -f <connection_file>")
    print("       remote_kernel add --endpoint <user@host[:port]> [-J user@ip:port] --name <Kernel Name>")
    print("       remote_kernel list")
    print("       remote_kernel delete <slug name>")
    print("       remote_kernel connect <slug name>")
    print("       remote_kernel --kill")
    print("       remote_kernel -v")

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

# Import kernel management utilities into the package namespace
from remote_kernel.connect import connect_kernel, add_kernel, list_kernels, delete_kernel
