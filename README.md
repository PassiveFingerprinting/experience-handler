# experience-handler

The experience-handler repository is part of a bigger project called PassiveFingerprinting. 
This bigger project aims at creating tools to enhance OS passive fingerprinting strategies.

The experience-handler tool is used to retrieve pcap files from different OS for further analysis. To do so, the experience.py script load prebuild image of the desired OS into virtualbox, an ssh agent is then sent to the VM and run a playbook of commands from inside it. 
The result pcap file is then save to a result folder.

## Installing dependecies

***DISCLAIMER: This project was only used and tested on debian.***

### Installing vboxmanage

The VM emulation software binary used by this project is vboxmanage. For more information about vboxmanage please read [vboxmanage documentation](https://www.virtualbox.org/manual/ch08.html#vboxmanage-common).

To install the vboxmanage binary, install the virtualbox debian package via apt:

`bash
sudo apt install virtualbox
`

*The vboxmanage version used by this project is 7.2.4_Debianr170995.*

### Installing sshpass

This project use sshpass to avoid storing the user root password.

To install it, install sshpass via apt:

`
sudo apt install sshpass
`

### Installing tcpdump

This project use tcpdump to save packets to pcap files.

To install it, install tcpdump via apt:

`
sudo apt install tcpdump
`

***Make sure that the tcpdump binary has sudo right when called by experience.py. You can do so by using the sudoers file, for more information please read [sudoers man](https://manpages.debian.org/buster/sudo/sudoers.5.en.html).***

## Running this project

To run this project you need a prebuilt virtual image. To work, your image should respect these conditions:
- Your image has the extension vdi or vmdk.
- The ssh service is enabled.
- experience.py can connect to your vm by ssh using the login `osboxes` and the password `osboxes.org`

Now that you have a valid prebuilt virtual image, run the script link.sh to create the right network interfaces to interact with the vm:

`
./link.sh
`

And finaly run the experience by passing the path to your virtual image to experience.py as so:

`
python3 experience.py <path to your virtual image.vdi>
`

## The result archive

When the experience run is successfull, it will create a result archive.

The experience archive contains these two elements:
1. info.json
2. \<UUIDV4\>.pcap

Here is an exemple info.json file:

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

The file info.json contains all the informations about the successfull experience when the \<UUIDV4\>.pcap file contains the host/vm exchanged packets.
