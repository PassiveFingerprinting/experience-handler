import logging
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4
import signal
import subprocess
import socket
import time

from collector import Collector
from network import Server
from cmds import CommandType
from vbox import VBoxManage

logger = logging.getLogger(__name__)

@dataclass
class Experience:
    local_exp_id: str
    pcap_exp_path: str
    univ_exp_id: str | None = None


class Orchestrator:

    SSH_PASS = "osboxes.org"
    SSH_USER = "osboxes"
    REMOTE_AGENT_FOLDER = "/home/osboxes/agent"
    VM_IP = "192.168.100.2"
    SERVER_ADDRESS = "192.168.100.1"
    SERVER_PORT = 5573
    SSH_WAKEUP_TIMEOUT = 120 # in seconds

    def __init__(self, images, pcap_dir="pcaps"):
        self.images = images
        self.server = Server(Orchestrator.SERVER_ADDRESS, Orchestrator.SERVER_PORT)
        self.collector = Collector()
        self.vm = None
        self.running_exp = None
        self.pcap_dir = Path(pcap_dir)
        if self.pcap_dir.exists():
            if not self.pcap_dir.is_dir():
                raise FileExistsError(f"{self.pcap_dir} is not a directory")
        else:
            logger.info(f"creating pcap directory at {self.pcap_dir}")
            self.pcap_dir.mkdir(parents=True, exist_ok=True)
        signal.signal(signal.SIGINT, self.sigint_handler)

    def sigint_handler(self, _, __):
        logger.info("received SIGINT signal")
        self.stop()

    def on_connect(self, _):
        logger.debug(self.server.send_message({"cmd": str(CommandType.SYSTEM_INFO), "data": {}}))

    def cmd_handler(self, data):
        logger.debug(data)

    def _ssh_is_up(self, timeout=120):
        """Checks if the SSH port is open and accepting connections."""
        logger.info("[Orchestrator]: checking if ssh port is open")
        start_time = time.perf_counter()
        while True:
            try:
                with socket.create_connection((Orchestrator.VM_IP, 22), timeout=1):
                    return True
            except (OSError, ConnectionRefusedError):
                if time.perf_counter() - start_time > timeout:
                    raise TimeoutError(f"Port {port} on {host} did not open within {timeout}s")
                time.sleep(1)

    def send_agent(self):
        logger.debug("[Orchestrator]: sending agent")
        if self._ssh_is_up() is False:
            logger.error("[Orchestrator]: could not access vm ssh service")
            return False
        logger.info("[Orchestrator]: remote ssh service is online")
        cmd = [
            "sshpass",
            "-p",
            f"{Orchestrator.SSH_PASS}",
            "rsync",
            "--progress",
            "-av", 
            "--files-from=agent_files.txt",
            ".", 
            f"{Orchestrator.SSH_USER}@{Orchestrator.VM_IP}:{Orchestrator.REMOTE_AGENT_FOLDER}"
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            logger.error(f"could not rsync agent sources files to vm")
            raise subprocess.SubprocessError(result.stderr)
        logger.info('[Orchestrator]: agent source files successfully sent')
        return True

    def run_agent(self):
        cmd = [
            "sshpass",
            "-p",
            f"{Orchestrator.SSH_PASS}",
            "ssh",
            f"{Orchestrator.SSH_USER}@{Orchestrator.VM_IP}",
            f"cd {Orchestrator.REMOTE_AGENT_FOLDER}; python3 agent.py {Orchestrator.SERVER_ADDRESS} {Orchestrator.SERVER_PORT}"
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            logger.error(f"[Orchestrator]: could not run agent in vm")
            raise subprocess.SubprocessError(result.stderr)
        logger.info('[Orchestrator]: successfully ran agent')
        return True

    def start(self):
        self.server.start(self.cmd_handler, on_connection=self.on_connect)
        for image in self.images:
            local_exp_id = uuid4().hex
            pcap_path = str(self.pcap_dir.with_name(f"{local_exp_id}.pcap"))
            self.running_exp = Experience(
                local_exp_id=local_exp_id,
                pcap_exp_path=pcap_path
            )
            self.collector.set_output(pcap_path)
            self.vm = VBoxManage(image)
            self.vm.create_vm()
            self.vm.start_vm()
            if self.collector.start() is False:
                break
            if self.send_agent() is False:
                break
            self.run_agent()
        self.stop()

    def stop(self):
        self.server.stop()
        self.collector.stop()
        if self.vm:
            if self.vm.is_running():
                self.vm.stop_vm()

