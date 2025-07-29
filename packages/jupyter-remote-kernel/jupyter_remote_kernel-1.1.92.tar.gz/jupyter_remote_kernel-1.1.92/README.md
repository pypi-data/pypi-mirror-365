# Jupyter Remote Kernel

A CLI tool for launching and managing remote Jupyter kernels over SSH with rsync and port forwarding.

## Features

- **SSH tunneling** for all five Jupyter ZMQ channels (`shell`, `iopub`, `stdin`, `control`, `hb`)
- **Rsync** for fast, incremental transfer of Jupyter connection files
- **Kernel spec management**: add, list, and delete remote kernels for seamless integration with Jupyter and VS Code
- **Custom remote Python**: use any Python interpreter on the remote host
- **Graceful tunnel management**: start and stop SSH tunnels as needed

---

## Installation

```bash
pip install jupyter_remote_kernel
```

---

## Usage

## Kernel Spec Management

### Add a remote kernel

Registers a new kernel spec so it appears in Jupyter and VS Code:

```bash
remote_kernel add --endpoint ubuntu@11.0.0.10:22 --name "Remote CUDA"
```

This creates a kernel spec at `~/.local/share/jupyter/kernels/remote_cuda/kernel.json`:

```json
{
  "argv": [
    "remote_kernel",
    "--endpoint", "ubuntu@11.0.0.10:22",
    "-f", "{connection_file}"
  ],
  "display_name": "Remote CUDA",
  "language": "python"
}
```

### List all registered kernels

```bash
remote_kernel list
```

Example output:
```
slug: remote_cuda
  name: Remote CUDA
  endpoint: ubuntu@11.0.0.10:22
---
slug: gpu_lab
  name: GPU Lab
  endpoint: dev@10.0.0.5:2222
---
```

### Delete a kernel

Delete by slug (preferred):

```bash
remote_kernel delete remote_cuda
```

Or by display name:

```bash
remote_kernel delete "Remote CUDA"
```

Both remove the kernel spec from `~/.local/share/jupyter/kernels/<slug>`.

---

## Notes

- To use a different Python on the remote server, set the environment variable:
  ```bash
  export REMOTE_KERNEL_PYTHON=/path/to/python
  ```
- Remote connection files are stored at `/tmp/<connection.json>` on the remote host.
- Slug names are lowercased from the display name, with spaces and dashes converted to underscores.
- **SSH jump host (bastion) support:**
  If your remote server is only accessible via a jump host (bastion), simply configure your `~/.ssh/config` with a `ProxyJump` or `ProxyCommand` entry. The tool will automatically use your SSH config for connections.

---

## Example Workflow

```bash
remote_kernel add --endpoint ubuntu@11.0.0.10:22 --name "Remote CUDA"
remote_kernel list
remote_kernel delete remote_cuda
remote_kernel --kill
```

---

## Integration with JupyterLab and VS Code

Once a remote kernel is registered, it will appear in the JupyterLab and VS Code kernel selector.  
Select it as you would any local kernel to launch a remote session.

---

## License

MIT License
