# experience-handler

The **experience-handler** repository is part of a larger project called **PassiveFingerprinting**. This project aims to provide tools for improving passive operating system fingerprinting strategies.

The **experience-handler** tool is used to automatically retrieve PCAP files from different operating systems for further analysis.

To achieve this, the `experience.py` script loads a prebuilt OS virtual machine image into VirtualBox. An SSH agent is then used to connect to the virtual machine and execute a predefined playbook of commands from inside the guest system.

The resulting PCAP file is then stored in the results directory along with metadata describing the generated capture.

## Installing dependencies

***DISCLAIMER: This project has only been tested on Debian-based systems.***

### Installing VirtualBox

The virtualization software used by this project is **VirtualBox**. The main binary used to control virtual machines is `vboxmanage`.

For more information about `vboxmanage`, please refer to the [VirtualBox documentation](https://www.virtualbox.org/manual/ch08.html#vboxmanage-common).

To install VirtualBox on Debian:

```bash
sudo apt install virtualbox
```

The VirtualBox version used during development was:

```
7.2.4_Debianr170995
```

### Installing sshpass

This project uses `sshpass` to provide SSH authentication without requiring the user password to be stored in configuration files.

Install it with:

```bash
sudo apt install sshpass
```

### Installing tcpdump

This project uses `tcpdump` to capture network traffic and generate PCAP files.

Install it with:

```bash
sudo apt install tcpdump
```

***Make sure that the `tcpdump` binary can be executed with sudo privileges by `experience.py`. This can be configured using the sudoers file. For more information, please refer to the [sudoers documentation](https://manpages.debian.org/buster/sudo/sudoers.5.en.html).***

## Building the SSH agent

The `agent/` directory contains the SSH agent code used by the project to execute commands inside the virtual machine.

Before running the experience, the agent must be compiled using the provided `Makefile`.

To build the agent, run:

```bash
cd agent
make
```

## Running this project

To run this project, you need a prebuilt virtual machine image.

The image must satisfy the following requirements:

* The image format must be either `.vdi` or `.vmdk`.
* The SSH agent must be build, [Building the SSH agent](#building-the-ssh-agent) 
* The SSH service must be enabled.
* The virtual machine must be accessible through SSH using:

  * Username: `osboxes`
  * Password: `osboxes.org`

Once a valid virtual machine image is available, run the `link.sh` script to create the required network interfaces:

```bash
./link.sh
```

Then start the experience by providing the path to the virtual machine image:

```bash
python3 experience.py <path-to-your-virtual-image.vdi>
```

## Result archive

When an experience completes successfully, a result archive is created.

The archive contains two files:

1. `info.json`
2. `<UUIDV4>.pcap`

Example `info.json` file:

```json
{
    "creation_time": "2026-04-15 08:24:33",
    "kernel_name": "Linux",
    "kernel_version": "#1 SMP PREEMPT_DYNAMIC Kali 6.18.5-1kali1 (2026-01-19)",
    "kernel_release": "6.18.5+kali-amd64",
    "pcap_filename": "461e79b33abd4ee2be39761595c626dc.pcap",
    "pcap_sha256_checksum": "c86f2a84b4ca7a9d223329d8562b0379cf210c76d81ad1ac5e74381cb124a3e2"
}
```

The `info.json` file contains metadata about the generated experience, including information about the operating system and the generated PCAP file.

The `<UUIDV4>.pcap` file contains the network traffic exchanged between the host machine and the virtual machine during the experiment.

## Workflow overview

The typical workflow is:

1. Select an operating system virtual machine image.
2. Start the experience using `experience.py`.
3. Execute the predefined commands inside the guest system.
4. Capture the generated network traffic.
5. Store the PCAP file and associated metadata.
6. Use the generated data for further passive fingerprinting analysis.
