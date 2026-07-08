import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from uuid import uuid4
import signal
import subprocess
import socket
import time
from threading import Event
import json
import zipfile
from datetime import datetime
import hashlib

from collector import Collector
from network import Server
from cmds import CommandType
from vbox import VBoxManage

logger = logging.getLogger(__name__)

@dataclass
class Experience:
    exp_id: str
    creation_time: str | None
    pcap_filename: str
    pcap_sha256_checksum: str | None = None
    kernel_version: str | None = None
    kernel_name: str | None = None
    kernel_release: str | None = None
    machine: str | None = None


class Orchestrator:

    SSH_PASS = "osboxes.org"
    SSH_USER = "osboxes"
    REMOTE_AGENT_FOLDER = "/home/osboxes/agent_bin"
    VM_IP = "192.168.100.2"
    SERVER_ADDRESS = "192.168.100.1"
    SERVER_PORT = 5573
    SSH_WAKEUP_TIMEOUT = 120 # in seconds
    PLAYBOOK_TIMEOUT = 720 # in seconds
    INFO_JSON_FILENAME = "info.json"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, images, results_dir="results"):
        """Orchestrator constructor.

        Args:
            images (list[str]): list of path to prebuilt images to be tested.
            results_dir (str): path to the results directory

        Returns:
            none

        Raises:
            NotADirectoryError: If results_dir is not a directory
        """
        self.images = images
        self.server = Server(Orchestrator.SERVER_ADDRESS, Orchestrator.SERVER_PORT)
        # events declaration
        self.on_connect = Event()
        self.playbook_done = Event()
        self.collector = Collector()
        self.vm = None
        self.agent_running = False
        self.agent = None
        self.agent_connected = False
        self.running = False
        # running experience dataclass 
        self.running_exp = None
        self.results_dir = Path(results_dir)
        # making sure pcap and results dir exist
        if self.results_dir.exists():
            if not self.results_dir.is_dir():
                raise NotADirectoryError(f"{self.results_dir} is not a directory")
        else:
            logger.info(f"creating results directory at {self.results_dir}")
            self.results_dir.mkdir(parents=True, exist_ok=True)
        signal.signal(signal.SIGINT, self.sigint_handler)

    def sigint_handler(self, _, __):
        """Function used to catch SIGINT signal and stop the experience.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        logger.info("received SIGINT signal")
        self.stop()

    def cmd_handler(self, data):
        """Handle commands received via network.

        Args:
            data (dict): The data received from a client.

        Returns:
            none

        Raises:
            none
        """
        logger.info(f"received command: {data}")
        if data["cmd"] == "DONE":
            self.playbook_done.set()
        if data["cmd"] == "SYSTEM_INFO":
            self.running_exp.kernel_name = data["result"]["name"]
            self.running_exp.kernel_version = data["result"]["version"]
            self.running_exp.kernel_release = data["result"]["release"]
            self.running_exp.machine = data["result"]["machine"]

    def _ssh_is_up(self, timeout=120):
        """Checks if the SSH port is open and accepting connections.

        Args:
            timeout (int): The maximum time in seconds to wait for the remote host port to open.

        Returns:
            none

        Raises:
            none
        """
        logger.info("[Orchestrator]: checking if ssh port is open")
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and self.running:
            try:
                with socket.create_connection((Orchestrator.VM_IP, 22), timeout=2) as sock:
                    sock.settimeout(2)
                    banner = sock.recv(256).decode("ascii", errors="ignore")
                    if banner.startswith("SSH-"):
                        logger.info("[Orchestrator]: ssh service up and running")
                        return True
            except (OSError, ConnectionRefusedError):
                pass
            time.sleep(0.5)
        return False

    def send_agent(self):
        """Send the agent to the vm via ssh.

        Args:
            none

        Returns:
            Bool: True if the agent has been successfully sent, False otherwise.

        Raises:
            SubprocessError: If the subprocess failed
        """
        logger.debug("[Orchestrator]: sending agent")
        if self._ssh_is_up() is False:
            logger.error("[Orchestrator]: could not access vm ssh service")
            return False
        subprocess.run([
            "sshpass", 
            "-p", 
            Orchestrator.SSH_PASS,
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            f"{Orchestrator.SSH_USER}@{Orchestrator.VM_IP}",
            "mkdir", 
            "-p", 
            Orchestrator.REMOTE_AGENT_FOLDER
        ], check=True)
        subprocess.run([
            "sshpass", 
            "-p", 
            Orchestrator.SSH_PASS,
            "rsync",
            "-avz",
            "-e", 
            "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null",
            "agent/agent",
            f"{Orchestrator.SSH_USER}@{Orchestrator.VM_IP}:{Orchestrator.REMOTE_AGENT_FOLDER}/agent"
        ], check=True)
        logger.info('[Orchestrator]: agent source files successfully sent')
        return True

    def run_agent(self):
        """Run the agent from within the vm via ssh.

        Args:
            none

        Returns:
            Bool: Returns True if the agent is successfully running, False otherwise.

        Raises:
            SubprocessError: If the subprocess failed
        """
        cmd = [
            "sshpass",
            "-p",
            f"{Orchestrator.SSH_PASS}",
            "ssh",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            f"{Orchestrator.SSH_USER}@{Orchestrator.VM_IP}",
            f"cd {Orchestrator.REMOTE_AGENT_FOLDER}; chmod +x agent; ./agent {Orchestrator.SERVER_ADDRESS} {Orchestrator.SERVER_PORT} > agent_debug.logs 2>&1"
        ]
        try:
            self.agent = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except subprocess.SubprocessError as err:
            logger.error(f'could not run cmd: {cmd}')
            raise err
        logger.info("Waiting 1s to catch immediate failure")
        time.sleep(1)
        if (ret := self.agent.poll()) is not None:
            stdout, stderr = self.agent.communicate()
            raise RuntimeError(
                f"SSH failed ({ret})\nstdout:\n{stdout}\nstderr:\n{stderr}"
            )
        self.agent_running = True
        logger.info('[Orchestrator]: successfully ran agent')
        return True

    def run_playbook(self):
        """Run the playbook from within the vm. The playbook is defined in this function.

        Args:
            none

        Returns:
            Bool: Returns True if the playbook has been runne successfully, False otherwise.

        Raises:
            none
        """
        logger.info('running playbook')
        if self.on_connect.wait(timeout=Orchestrator.PLAYBOOK_TIMEOUT) is False:
            logger.error("could run playbook because agent did not connect to server")
            return False
        # definition of the playbook
        self.server.send_message({"cmd": "SYSTEM_INFO", "data": {}})
        self.server.send_message({"cmd": "DONE", "data": {}})
        # end of the playbook definition
        if not self.playbook_done.is_set():
            if self.playbook_done.wait(timeout=Orchestrator.PLAYBOOK_TIMEOUT) is False:
                logger.warn('agent did not respond with the done command before timeout')
                return False
            else:
                logger.info('playbook done')
        self.playbook_done.clear()
        return True

    def save_experience(self):
        """Save gathered information and results of the experience to zip archive.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        logger.info("saving experience")
        with open(str(self.results_dir / self.running_exp.pcap_filename), "rb") as pcap_file:
            self.running_exp.pcap_sha256_checksum = hashlib.file_digest(pcap_file, "sha256").hexdigest()
        with open(self.results_dir / Orchestrator.INFO_JSON_FILENAME, "w") as info_file:
            json.dump(asdict(self.running_exp), info_file, indent=4)
        json_path = self.results_dir / Orchestrator.INFO_JSON_FILENAME
        pcap_path = self.results_dir / self.running_exp.pcap_filename
        with zipfile.ZipFile(str(self.results_dir / f"{self.running_exp.exp_id}.zip"), "w") as res_archive:
            res_archive.write(str(json_path), arcname=Orchestrator.INFO_JSON_FILENAME)
            res_archive.write(str(pcap_path), arcname=self.running_exp.pcap_filename)
        logger.info("removing pcap and info.json")
        json_path.unlink(missing_ok=True)
        pcap_path.unlink(missing_ok=True)
        logger.info("successfully saved experience")

    def start(self):
        """Function used to start the experience.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        self.running = True
        self.server.start(self.cmd_handler, on_connection=self.on_connect)
        for image in self.images:
            exp_id = uuid4().hex
            pcap_filename = f"{exp_id}.pcap"
            pcap_path = str(self.results_dir / pcap_filename)
            self.running_exp = Experience(
                exp_id=exp_id,
                pcap_filename=pcap_filename,
                creation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            if self.run_playbook():
                self.save_experience()
            self.vm.stop_vm()
            self.collector.stop()
        self.stop()

    def stop(self):
        """Function used to stop the experience.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        self.running = False
        self.server.stop()
        self.collector.stop()
        if self.agent_running:
            self.agent.terminate()
            self.agent_running = False
        if self.vm:
            if self.vm.is_running():
                self.vm.stop_vm()

