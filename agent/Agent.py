import logging
import platform
from client.Client import Client
from cmds.Commands import Command


logger = logging.getLogger(__name__)


class Agent:

    def __init__(self, host, port):
        self.client = Client(host, port)
        self.cmds = {
            str(Command.SYSTEM_INFO): self.cmd_info,
        }

    def cmd_info(self, _):
        logger.info(f'cmd info received')
        system_info = platform.uname()
        self.client.send_message({
            "cmd": str(Command.SYSTEM_INFO),
            "result": {
                "release": system_info.release,
                "version": system_info.version,
                "machine": system_info.machine
            }
        })

    def handle_commands(self, cmd):
        if 'cmd' in cmd:
            if cmd["cmd"] in self.cmds:
                self.cmds[cmd["cmd"]](cmd["data"])
            else:
                logger.info(f'Command {cmd["cmd"]} not recognized')

    def start(self):
        logger.info(f'Agent starting')
        self.client.start(self.handle_commands)

    def stop(self):
        logger.info(f'Agent stopping')
        self.client.stop()