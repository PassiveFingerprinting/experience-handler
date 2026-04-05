from enum import Enum
import logging
import os
import threading
import subprocess
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PcapSetting(Enum):
    erase = "erase"
    append = "append"


class Collector:

    PKEXEC_TIMEOUT = 20 # in seconds

    def __init__(self, output_path=None, interface="tap0", pcap_setting="erase"):
        self.output_path = output_path
        self.interface = interface
        self.running = False
        self.sniffer = None
        # self.thread = None
        # self.ask_to_stop = False
        self.tcpdump = None
        if pcap_setting not in PcapSetting.__members__:
            logger.error('[Collector]: PcapSetting not recognized')
            raise ValueError(pcap_setting)
        self.pcap_setting = pcap_setting

    def set_output(self, output_path):
        if self.running:
            logger.info('[Collector]: Output path changed, update will apply when sniffer is restarted')
        self.output_path = output_path

    def is_running(self):
        return self.running

    def handle_pcap_setting(self):
        if self.pcap_setting == "erase" and os.path.exists(self.output_path):
            try:
                os.remove(self.output_path)
            except OSError as e:
                logger.error(e)
                logger.error(f'[Collector]: could not remove {self.output_path} file')
                raise e
            logger.info(f'[Collector]: old {self.output_path} file removed')

    # TODO: make the call to stderr stream non blocking to suspend function call in case of tiemout
    def start(self):
        logger.info('[Collector]: Starting collector')
        self.handle_pcap_setting()
        logger.info("[Collector]: Capturing tap0 with tcpdump")
        self.tcpdump = subprocess.Popen(["pkexec", "tcpdump", "-i", "tap0", "-w", self.output_path], stderr=subprocess.PIPE, text=True)
        start_time = datetime.now()
        while datetime.now() < start_time + timedelta(seconds=Collector.PKEXEC_TIMEOUT):
            for line in self.tcpdump.stderr:
                if "tcpdump:" in line:
                    logger.info('[Collector]: Successfully started collector')
                    self.running = True
                    return True
        logger.error('[Collector]: pkexec timeout expired')
        return False

    def stop(self):
        logger.info('[Collector]: Stopping collector')
        if self.tcpdump is not None:
            self.tcpdump = subprocess.Popen(["pkexec", "kill", str(self.tcpdump.pid)], stderr=subprocess.PIPE, text=True)
        logger.info('[Collector]: Collector stopped')
