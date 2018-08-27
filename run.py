import socket
import select
from eventlet import sleep, GreenPool
from eventlet.queue import Queue
import eventlet.greenthread as greenthread

def get_interface_address(self):
    # http://man7.org/linux/man-pages/man7/netdevice.7.html
    ifreq = struct.pack('16sH6s', self.interface_name.encode("utf-8"), 0, b"")
    response = ioctl(self.socket, self.SIOCGIFHWADDR, ifreq)
    _interface_name, _address_family, interface_address = struct.unpack('16sH6s', response)
    self.interface_address = MacAddress(interface_address)

def get_interface_index(self):
    # http://man7.org/linux/man-pages/man7/netdevice.7.html
    ifreq = struct.pack('16sI', self.interface_name.encode("utf-8"), 0)
    response = ioctl(self.socket, self.SIOCGIFINDEX, ifreq)
    _ifname, self.interface_index = struct.unpack('16sI', response)

def join_multicast_group(self):
    mreq = struct.pack("IHH8s", self.interface_index, self.PACKET_MR_PROMISC, len(self.EAP_ADDRESS.address), self.EAP_ADDRESS.address)
    self.socket.setsockopt(self.SOL_PACKET, self.PACKET_ADD_MEMBERSHIP, mreq)

interface_name = "eth0"

#mysocket = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x888e))
mysocket = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0800))
mysocket.bind((interface_name, 0))

print("created raw socket")
mypoller = select.poll()
mypoller.register(mysocket,
                  select.POLLIN |
                  select.POLLPRI |
                  select.POLLERR |
                  select.POLLHUP |
                  select.POLLNVAL)
print("Set poll options")

pool = GreenPool()
eventlets = []

def socket_listen(mysocket, mypoller):
    while True:
        print("socket sleeping")
        sleep(1)
        print("socket waking up")
        events = mypoller.poll(10)
        if not events:
            print("poll timed out")
        else:
            while events:
                if len(events) > 1:
                    raise Exception("Too many events returned from poller")
                fd, event = events[0]
                if event == select.POLLERR or event == select.POLLHUP or event == select.POLLNVAL:
                    print("socket error, giving up")
                    break
                if event == select.POLLIN:
                    print("Data to receive")
                    data = mysocket.recv(4096)
                    print("Received data: %s" % data)
                events = mypoller.poll(10)

def not_blocking():
    while True:
        print("Not blocking!")
        print("printer sleeping")
        sleep(1)
        print("printer waking up")


eventlets.append(pool.spawn(socket_listen, *(mysocket, mypoller)))
eventlets.append(pool.spawn(not_blocking))

pool.waitall()