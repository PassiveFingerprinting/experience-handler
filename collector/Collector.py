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

    # has to be run with sudo privilege

    PROCESS_CHECK_TIMEOUT = 1 # seconds

    def __init__(self, output_path=None, interface="tap0", pcap_setting="erase"):
        """Collector constructor.

        Args:
            output_path (str | Bool): path to the result output pcap file.
            interface (str): target network interface.
            pcap_setting (str): output pcap file writing mode. Available settings are ["erase", "append"]. 
                                The setting "erase" will erase previous pcap content, "append" will append new result to existing pcap.

        Returns:
            none

        Raises:
            ValueError: pcap_setting are not supported.
        """
        self.output_path = output_path
        self.interface = interface
        self.running = False
        self.sniffer = None
        self.tcpdump = None
        if pcap_setting not in PcapSetting.__members__:
            logger.error('[Collector]: PcapSetting not recognized')
            raise ValueError(pcap_setting)
        self.pcap_setting = pcap_setting

    def set_output(self, output_path):
        """Function used to set the pcap output path.

        Args:
            output_path (str): path to the new result output pcap file.

        Returns:
            none

        Raises:
            none
        """
        if self.running:
            logger.info('[Collector]: Output path changed, update will apply when sniffer is restarted')
        self.output_path = output_path

    def is_running(self):
        """Function used to check if collector is running.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        return self.running

    def handle_pcap_setting(self):
        """Function used to apply pcap_setting.

        Args:
            none

        Returns:
            none

        Raises:
            OSError: could not remove previous pcap file
        """
        if self.pcap_setting == "erase" and os.path.exists(self.output_path):
            try:
                os.remove(self.output_path)
            except OSError as e:
                logger.error(e)
                logger.error(f'[Collector]: could not remove {self.output_path} file')
                raise e
            logger.info(f'[Collector]: old {self.output_path} file removed')

    # TODO: make the call to stderr stream non blocking to suspend function call in case of timeout
    def start(self):
        """Function used to start the collector.

        Args:
            none

        Returns:
            Bool: True if started successfully.

        Raises:
            SubprocessError: If the `tcpdump` command failed.
        """
        logger.info('[Collector]: Starting collector')
        self.handle_pcap_setting()
        logger.info("[Collector]: Capturing tap0 with tcpdump")
        logger.info(f"[Collector]: Output path at: {self.output_path}")
        try:
            self.tcpdump = subprocess.Popen([
                "sudo",
                "/usr/bin/tcpdump",
                "-n",
                "-i", 
                "tap0", 
                "-w",
                self.output_path
                ]
                , stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        except subprocess.SubprocessError as err:
            logger.error('could not start tcpdump process')
            raise SubprocessError               
        logger.info('[Collector]: Successfully started collector')
        self.running = True
        return True

    def stop(self):
        """Function used to stop the collector.

        Args:
            none

        Returns:
            none

        Raises:
            none
        """
        logger.info('[Collector]: Stopping collector')
        if self.tcpdump is not None:
            self.tcpdump.terminate()
        logger.info('[Collector]: Collector stopped')
