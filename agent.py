import argparse
import logging
import sys
import signal

from agent import Agent


logger = logging.getLogger(__name__)


def main(host, port):
    agent = Agent(host, port)
    agent.start()


if __name__=='__main__':
    parser = argparse.ArgumentParser(
    description="A python agent to connect to experience server"
    )
    parser.add_argument("host",
                        help="Experience server address to connect to",
                        default="192.168.100.1"
                        )
    parser.add_argument("port",
                        help="Experience server port",
                        default=5573
                        )
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(level=logging.DEBUG)
    main(args.host, args.port)