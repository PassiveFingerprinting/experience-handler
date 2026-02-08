from enum import Enum
import logging
import os
import threading
from scapy.all import sniff, wrpcap

logger = logging.getLogger(__name__)


class PcapSetting(Enum):
    erase = "erase"
    append = "append"


class Collector:

    def __init__(self, output_path, interface="tap0", pcap_setting="erase"):
        self.output_path = output_path
        self.interface = interface
        self.running = False
        self.sniffer = None
        self.thread = None
        self.ask_to_stop = False
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

    def _capture(self):
        packets = sniff(iface=self.interface, count=0, stop_filter=lambda x: self.ask_to_stop)
        logger.info(f'[_capture]: writing packets to pcap file {self.output_path}')
        wrpcap(self.output_path, packets)

    def start(self):
        logger.info('[Collector]: Starting collector')
        self.handle_pcap_setting()
        self.ask_to_stop = False
        self.thread = threading.Thread(target=self._capture, daemon=True)
        self.thread.start()
        self.running = True
        logger.info('[Collector]: Collector started')

    def stop(self):
        logger.info('[Collector]: Stopping collector')
        self.ask_to_stop = True
        self.thread.join()
        logger.info('[Collector]: Collector stopped')
