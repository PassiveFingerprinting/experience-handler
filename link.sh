sudo ip link add name virtbr0 type bridge
sudo ip addr add 192.168.100.1/24 dev virtbr0
sudo ip link set virtbr0 up
sudo ip tuntap add dev tap0 mode tap user $USER
sudo ip link set tap0 master virtbr0
sudo ip link set tap0 up