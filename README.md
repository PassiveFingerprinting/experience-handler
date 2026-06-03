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