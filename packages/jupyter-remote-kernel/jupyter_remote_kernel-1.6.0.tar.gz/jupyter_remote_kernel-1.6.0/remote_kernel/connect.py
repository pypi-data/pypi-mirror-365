import sys, os, json, subprocess, shutil
from remote_kernel import KERNELS_DIR, parse_endpoint, log

def connect_kernel(name_or_none=None):
    if not os.path.exists(KERNELS_DIR):
        print("[remote_kernel] No kernels installed.")
        return

    if not name_or_none:
        print("[remote_kernel] Available kernels:")
        for slug in os.listdir(KERNELS_DIR):
            kjson = os.path.join(KERNELS_DIR, slug, "kernel.json")
            if not os.path.isfile(kjson):
                continue
            with open(kjson) as f:
                data = json.load(f)
            name = data.get("display_name", slug)
            argv = data.get("argv", [])
            endpoint = argv[argv.index("--endpoint") + 1] if "--endpoint" in argv else None
            if endpoint:
                jump = argv[argv.index("-J") + 1] if "-J" in argv else None
                print(f"  {slug:20}  {endpoint}{' via ' + jump if jump else ''}")
        print("\nUse: remote_kernel connect <slug name>")
        return

    target_slug = name_or_none.lower().replace(" ", "_")
    for slug in os.listdir(KERNELS_DIR):
        kjson = os.path.join(KERNELS_DIR, slug, "kernel.json")
        if not os.path.isfile(kjson):
            continue
        with open(kjson) as f:
            data = json.load(f)
        name = data.get("display_name", slug)
        if target_slug in (slug, name.lower().replace(" ", "_")):
            argv = data.get("argv", [])
            endpoint = argv[argv.index("--endpoint") + 1] if "--endpoint" in argv else None
            jump = argv[argv.index("-J") + 1] if "-J" in argv else None
            if not endpoint:
                print(f"[remote_kernel] ERROR: No endpoint for {slug}")
                return
            host, port = parse_endpoint(endpoint)

            ssh_cmd = ["ssh"]
            if jump:
                ssh_cmd += ["-J", jump]
            if port:
                ssh_cmd += ["-p", str(port)]
            ssh_cmd += [host]
            print(f"[remote_kernel] Connecting to {endpoint}{' via ' + jump if jump else ''}...")
            subprocess.call(ssh_cmd)
            return

    print(f"[remote_kernel] Kernel '{name_or_none}' not found.")

def add_kernel(endpoint, name, jump):
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

def list_kernels():
    if not os.path.exists(KERNELS_DIR):
        print("[remote_kernel] No kernels installed.")
        return
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
            if endpoint:
                jump = argv[argv.index("-J") + 1] if "-J" in argv else None
                print(f"  {slug:20}  {name:20}  ({endpoint}){' via ' + jump if jump else ''}")
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
