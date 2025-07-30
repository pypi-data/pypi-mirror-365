from paramiko import SSHClient, AutoAddPolicy
from sshtunnel import SSHTunnelForwarder
import socket, time, sys, select, termios, tty
from pydantic import BaseModel, root_validator
from typing import Optional, List, Tuple


class SSHConfig(BaseModel):
    """Holds connection parameters for SSH."""
    username: str = "root"
    host: str = "localhost"
    port: int = 22
    jump: Optional[str] = None
    endpoint: str  # Original endpoint for reference

    @root_validator(pre=True)
    def parse_endpoint(cls, values):
        endpoint = values.get("endpoint")
        if not isinstance(endpoint, str) or "@" not in endpoint:
            raise ValueError("endpoint must be in format user@host[:port]")

        username, host_part = endpoint.split("@", 1)
        if ":" in host_part:
            host, port_str = host_part.split(":", 1)
            port = int(port_str)
        else:
            host, port = host_part, 22

        values["username"] = username
        values["host"] = host
        values["port"] = port
        return values

    def __str__(self):
        return f"SSHConfig(username={self.username}, host={self.host}, port={self.port}, jump={self.jump})"


class SSHWrapper:
    """Stateless SSH wrapper for commands, file copy, tunneling, and interactive shell."""

    def __init__(self, ssh_config: SSHConfig):
        if not isinstance(ssh_config, SSHConfig):
            raise TypeError("ssh_config must be an SSHConfig instance")
        self.cfg = ssh_config

    def _build_jump_channel(self) -> Tuple[Optional[SSHClient], Optional[socket.socket]]:
        """If a jump host is specified, return (jump_client, channel) for proxying."""
        if not self.cfg.jump:
            return None, None

        j_user, j_hostport = self.cfg.jump.split("@")
        j_host, j_port = (j_hostport.split(":") + ["22"])[:2]
        j_port = int(j_port)

        jump_client = SSHClient()
        jump_client.set_missing_host_key_policy(AutoAddPolicy())
        jump_client.connect(j_host, port=j_port, username=j_user)

        sock = jump_client.get_transport().open_channel(
            "direct-tcpip",
            (self.cfg.host, self.cfg.port),
            ("127.0.0.1", 0)
        )
        return jump_client, sock

    def exec(self, cmd: str) -> Tuple[str, str]:
        """Execute a command remotely (non-interactive)."""
        return self.exec_with_tunnels(cmd, None)

    def exec_with_tunnels(self, cmd: str = None, tunnels: Optional[List[int]] = None) -> Tuple[str, str]:
        """
        Executes a command on the remote host with optional SSH tunnels.
        Properly separates tunnel transport and SSH exec connection.
        """
        out, err = "", ""
        retries = 0
        ssh = None
        jump_client = None
        tunnel_jump = None
        server = None

        while retries < 5:
            try:
                jump_client, sock = self._build_jump_channel()
                ssh = SSHClient()
                ssh.set_missing_host_key_policy(AutoAddPolicy())
                ssh.connect(self.cfg.host, port=self.cfg.port, username=self.cfg.username, sock=sock)
                print(f"[ssh_wrapper] Connected to {self.cfg.host}:{self.cfg.port} as {self.cfg.username}")
                # If tunnels are needed, open them first (via jump)
                if tunnels and len(tunnels) > 0:
                    tunnel_jump, tunnel_sock = self._build_jump_channel()
                    server = SSHTunnelForwarder(
                        ssh_address_or_host=(self.cfg.host, self.cfg.port),
                        ssh_username=self.cfg.username,
                        remote_bind_addresses=[("127.0.0.1", p) for p in tunnels],
                        local_bind_addresses=[("127.0.0.1", p) for p in tunnels],
                        ssh_proxy=tunnel_sock,
                        set_keepalive=5
                    )
                    server.start()
                    print(f"[ssh_wrapper] Tunnel open for ports {tunnels}.")

                if cmd:
                    print(f"[ssh_wrapper] Connected to {self.cfg.host}:{self.cfg.port} as {self.cfg.username}")
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    out = stdout.read().decode().strip()
                    err = stderr.read().decode().strip()
                    print(f"[ssh_wrapper] Executed on {self.cfg.host}: {cmd}")
                    if out:
                        print(f"[ssh_wrapper] Output: {out}")
                elif server:
                    # Only tunnels, block until interrupted
                    try:
                        while True:
                            time.sleep(5)
                    except KeyboardInterrupt:
                        print("[ssh_wrapper] Tunnel interrupted.")
                break

            except KeyboardInterrupt:
                print("[ssh_wrapper] Interrupted. Closing tunnel and SSH session.")
                break
            except Exception as e:
                print(f"[ssh_wrapper] Retry {retries+1}: Failed to run '{cmd}' on {self.cfg.host}: {e}")
                time.sleep(5)
                retries += 1
            finally:
                if ssh:
                    ssh.close()
                if jump_client:
                    jump_client.close()
                if server:
                    server.stop()
                if tunnel_jump:
                    tunnel_jump.close()

        return out, err

    def tunnel(self, tunnels: Optional[List[int]] = None) -> bool:
        """Open SSH tunnels for given ports (blocks until interrupted)."""
        self.exec_with_tunnels(cmd=None, tunnels=tunnels)
        return True

    def copy(self, src_file: str, dest_file: str) -> bool:
        """Copy a local file to the remote host using SFTP."""
        jump_client, sock = self._build_jump_channel()
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        try:
            ssh.connect(self.cfg.host, port=self.cfg.port, username=self.cfg.username, sock=sock)
            sftp = ssh.open_sftp()
            sftp.put(src_file, dest_file)
            sftp.close()
            print(f"[ssh_wrapper] Copied {src_file} -> {self.cfg.host}:{dest_file}")
            return True
        except Exception as e:
            print(f"[ssh_wrapper] File copy failed: {e}")
            return False
        finally:
            ssh.close()
            if jump_client:
                jump_client.close()

    def connect(self):
        """Start an interactive SSH session (like `ssh user@host -p port [-J jump]`)."""
        jump_client, sock = self._build_jump_channel()

        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(self.cfg.host, port=self.cfg.port, username=self.cfg.username, sock=sock)

        chan = ssh.invoke_shell()
        print(f"[ssh_wrapper] Connected to {self.cfg.username}@{self.cfg.host}:{self.cfg.port}"
              f"{' -J ' + self.cfg.jump if self.cfg.jump else ''}")
        print("Press Ctrl+D to exit.")

        old_tty = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            while True:
                r, _, _ = select.select([chan, sys.stdin], [], [])
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