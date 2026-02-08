import argparse
import logging
import sys
import signal
from time import sleep

from server.Server import Server
from cmds.Commands import Command
from Collector import Collector
from VBox import IVBoxManage


logger = logging.getLogger(__name__)

SHOULD_STOP = False

def signal_handler(sig, frame):
    global SHOULD_STOP
    SHOULD_STOP = True

def handler(data):
    logger.info(f"cmd: {data}")

def on_connection(server):
    logger.debug(server.send_message({"cmd": str(Command.SYSTEM_INFO), "data": {}}))

def main(images):
    # collector = Collector("test.pcap", interface="wlan0")
    # collector.start()
    # sleep(5)
    # collector.stop()
    # for image in images:
    #     vbox = IVBoxManage(image)
    #     vbox.create_vm()
    #     vbox.start_vm()
    server = Server("127.0.0.1", 5574)
    server.start(handler, on_connection=on_connection)
    while not SHOULD_STOP:
        pass
    server.stop()

if __name__=='__main__':
    parser = argparse.ArgumentParser(
    description="Python script to parse https://www.osboxes.org website to download and prepare vm images directories"
    )
    parser.add_argument("images",
                        help="Path to vm images.",
                        nargs="+"
                        )
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(level=logging.DEBUG)
    signal.signal(signal.SIGINT, signal_handler)
    main(args.images)