# https://www.virtualbox.org/manual/ch08.html#vboxmanage-controlvm

import uuid
import subprocess
import os
from pathlib import Path
import re
import logging
from subprocess import SubprocessError
from time import sleep

logger = logging.getLogger(__name__)


class VBoxManage:

    supported_extensions = ["vdi", "vmdk"]
    vm_name = "exciting_sugar"
    vm_memory_size = 2048
    vm_cpu = 1
    bridge_host_interface = "tap0"
    storage_controller_name = "SATA"
    stop_cooldown = 3

    def __init__(self, disk_image_path, vboxm_binary_path="/usr/bin/vboxmanage", base_folder="vm"):
        # attributes declaration
        self.disk_image = Path(disk_image_path)
        self.vboxm_binary_path = vboxm_binary_path
        self.base_folder = Path(base_folder)
        self.vm_uuid = None
        # check vm base folder path
        if self.base_folder.exists():
            logger.info(f"base folder exists at {self.base_folder.absolute()}")
            if not self.base_folder.is_dir():
                raise NotADirectoryError(f"base_folder: {self.base_folder}")
        else:
            logger.info(f"creating base folder at {self.base_folder}")
            os.mkdir(self.base_folder)
        # check vm image file
        if self.disk_image.exists():
            if not self.disk_image.is_file():
                raise FileNotFoundError(f"{self.disk_image} is not a file")
            print(self.disk_image.suffix)
            if self.disk_image.suffix[1:] not in self.supported_extensions:
                raise ValueError(f"{self.disk_image} extension is not supported, supported extensions are {self.supported_extensions}")
        else:
            raise FileNotFoundError(f"{self.disk_image} does not exist")
        self._test_vbox()

    def _test_vbox(self):
        if not os.path.isfile(self.vboxm_binary_path):
            raise FileNotFoundError(f"{self.vboxm_binary_path} binary does not exist")
        result = subprocess.run([self.vboxm_binary_path, "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            raise SubprocessError(result.stderr)
        logger.info(f"vboxm version: {result.stdout}")

    def list_vms(self):
        result = subprocess.run([self.vboxm_binary_path, "list", "vms"], stdout=subprocess.PIPE)
        print(result.stdout)

    def vm_exist(self):
        result = subprocess.run([self.vboxm_binary_path, "list", "vms"], stdout=subprocess.PIPE)
        if result.returncode != 0:
            logger.error(f"coudl not verify if vm {VBoxManage.vm_name} exists")
            raise SubprocessError(result.stdout)
        match = re.search(r'"exciting_sugar" \{([a-z0-9\-]+)\}', result.stdout.decode("utf-8"))
        if match is None:
            return False
        return match.group(1)

    def storage_exist(self):
        if self.vm_uuid is None:
            raise ValueError("vm_uuid is not defined")
        cmd = [
            self.vboxm_binary_path,
            "showvminfo",
            self.vm_uuid,
            "--machinereadable"
        ]
        logger.debug(f"showvminfo command: {cmd}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        if result.returncode != 0:
            logger.error(f"could not showvminfo {self.disk_image.stem}")
            raise SubprocessError(result.stderr)
        if result.stdout.decode("utf-8").find(f"{VBoxManage.storage_controller_name}-0-0") != -1:
            return True
        return False

    def register_vm(self):
        self.vm_uuid = str(uuid.uuid4())
        cmd = [
            self.vboxm_binary_path,
            "createvm",
            f"--name={VBoxManage.vm_name}",
            f"--basefolder={str(self.base_folder.absolute())}",
            f"--uuid={self.vm_uuid}",
            f"--os-types=Linux_64",
            "--register"
        ]
        logger.debug(f"create vm command: {cmd}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        if result.returncode != 0:
            logger.error(f"could not createvm {self.disk_image.stem}")
            raise SubprocessError(result.stderr)
        logger.info(f"registered vm {self.disk_image.stem}")

    def create_storage(self):
        if self.vm_uuid is None:
            raise ValueError("vm_uuid is not defined")
        if self.storage_exist():
            logger.info('storage controller already exists')
            return
        cmd = [
            self.vboxm_binary_path,
            "storagectl",
            self.vm_uuid,
            "--name=SATA",
            "--add=sata",
            "--controller=IntelAHCI",
            "--portcount=1",
            "--hostiocache=off",
            "--bootable=on"
        ]
        logger.debug(f"storagectl command: {cmd}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        print(result.stdout)
        if result.returncode != 0:
            logger.error(f"could not storagectl {self.disk_image.stem}")
            raise SubprocessError(result.stderr)
        logger.info(f"storage created for vm {self.disk_image.stem}")

    def attach_storage(self):
        if self.vm_uuid is None:
            raise ValueError("vm_uuid is not defined")
        cmd = [
            self.vboxm_binary_path,
            "storageattach",
            self.vm_uuid,
            "--type=hdd",
            f"--medium={str(self.disk_image.absolute())}",
            f"--storagectl={VBoxManage.storage_controller_name}",
            "--port=0",
            "--device=0"
        ]
        logger.debug(f"storageattach command: {cmd}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        if result.returncode != 0:
            logger.error(f"could not storageattach {self.disk_image.stem}")
            raise SubprocessError(result.stderr)
        logger.info(f"storage attached to vm {self.disk_image.stem}")

    def create_vm(self):
        # check if vm exist
        vm_uuid = self.vm_exist()
        if vm_uuid:
            self.vm_uuid = vm_uuid
        else:
            self.register_vm()
        cmd = [
            self.vboxm_binary_path,
            "modifyvm",
            self.vm_uuid,
            f"--os-type=Linux_64",
            f"--memory={VBoxManage.vm_memory_size}",
            f"--cpus={VBoxManage.vm_cpu}",
            "--cpu-profile=host",
            "--boot1=disk",
            "--nic1=bridged",
            f"--bridge-adapter1={VBoxManage.bridge_host_interface}",
            "--audio-enabled=off",
            "--audio-in=off",
            "--vram=16",
            "--graphicscontroller=vmsvga",
            "--usb-ehci=on",
            "--mouse=usb"
        ]
        logger.debug(f"create vm command: {cmd}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        if result.returncode != 0:
            logger.error(f"could not modifyvm {self.disk_image.stem}")
            raise SubprocessError(result.stderr)
        self.create_storage()
        self.attach_storage()
        logger.info(f"successfully created vm {self.disk_image.stem} {self.vm_uuid}")

    def is_running(self):
        if self.vm_uuid is None:
            raise ValueError("vm_uuid is not defined")
        cmd = [
            self.vboxm_binary_path,
            "list",
            "runningvms"
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        if result.returncode != 0:
            logger.error(f"could not startvm {self.disk_image.stem}")
            raise SubprocessError(result.stderr)
        logger.info(f"successfully query vm status {self.disk_image.stem}")
        if self.vm_uuid in result.stdout:
            return True
        return False
        logger.info(f"successfully started vm {self.disk_image.stem}")
    
    def start_vm(self):
        if self.vm_uuid is None:
            raise ValueError("vm_uuid is not defined")
        cmd = [
            self.vboxm_binary_path,
            "startvm",
            self.vm_uuid,
            "--type=gui"
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        if result.returncode != 0:
            logger.error(f"could not startvm {self.disk_image.stem}")
            raise SubprocessError(result.stderr)
        logger.info(f"successfully started vm {self.disk_image.stem}")

    def stop_vm(self):
        if self.vm_uuid is None:
            raise ValueError("vm_uuid is not defined")
        cmd = [
            self.vboxm_binary_path,
            "controlvm",
            self.vm_uuid,
            "poweroff"
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        if result.returncode != 0:
            logger.error(f"could not controlvm {self.disk_image.stem}")
            raise SubprocessError(result.stderr)
        logger.info(f"waiting for vm status update, sleeping for {VBoxManage.stop_cooldown}s")
        sleep(VBoxManage.stop_cooldown)
        logger.info(f"successfully stopped vm {self.disk_image.stem}")