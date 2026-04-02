import argparse
import logging
import sys

from Orchestrator import Orchestrator


logger = logging.getLogger(__name__)

def main(images):
    orch = Orchestrator(images)
    orch.start()


if __name__=='__main__':
    parser = argparse.ArgumentParser(
    description="Experience handler script"
    )
    parser.add_argument("images",
                        help="Path to vm images.",
                        nargs="+"
                        )
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(level=logging.DEBUG)
    main(args.images)