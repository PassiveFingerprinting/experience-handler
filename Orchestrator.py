import logging
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4
import signal

from Collector import Collector
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

    def __init__(self, images, pcap_dir="pcaps"):
        self.images = images
        self.server = Server("127.0.0.1", 5573)
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

    # def send_agent(self):
         

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
        self.stop()

    def stop(self):
        self.server.stop()
        self.collector.stop()
        if self.vm:
            if self.vm.is_running():
                self.vm.stop_vm()

