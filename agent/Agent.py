import logging
import platform
from network.client.Client import Client
from cmds import CommandType


logger = logging.getLogger(__name__)


class Agent:

    def __init__(self, host, port):
        self.client = Client(host, int(port))
        self.cmds = {
            str(CommandType.DONE): self.cmd_done,
            str(CommandType.SYSTEM_INFO): self.cmd_info,
        }

    def cmd_done(self, _):
        self.client.send_message({
            "cmd": str(CommandType.DONE),
            "result": {}
        })

    def cmd_info(self, _):
        logger.info(f'cmd info received')
        system_info = platform.uname()
        self.client.send_message({
            "cmd": str(CommandType.SYSTEM_INFO),
            "result": {
                "release": system_info.release,
                "version": system_info.version,
                "machine": system_info.machine
            }
        })

    def handle_cmds(self, cmd):
        if 'cmd' in cmd:
            if cmd["cmd"] in self.cmds:
                self.cmds[cmd["cmd"]](cmd["data"])
            else:
                logger.info(f'CommandType {cmd["cmd"]} not recognized')

    def start(self):
        logger.info(f'Agent starting')
        self.client.start(self.handle_cmds)

    def stop(self):
        logger.info(f'Agent stopping')
        self.client.stop()