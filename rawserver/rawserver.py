from eventlet import sleep, GreenPool
from eventlet.queue import Queue
from fcntl import ioctl
import socket
import select
import struct

class Rawserver:
    SIOCGIFHWADDR = 0x8927
    SIOCGIFINDEX = 0x8933
    PACKET_MR_PROMISC = 1
    SOL_PACKET = 263
    PACKET_ADD_MEMBERSHIP = 1
    DUMMY_ADDRESS = b"\x00\x00\x00\x00\x00\x00"

    def __init__(self, interface_name, ethertype, handler):
        self.interface_name = interface_name
        self.ethertype = ethertype
        self.handler = handler
        self.greenlets = set()
        self.queue = Queue()

    def get_interface_index(self):
        # http://man7.org/linux/man-pages/man7/netdevice.7.html
        ifreq = struct.pack('16sI', self.interface_name.encode("utf-8"), 0)
        response = ioctl(self.socket, self.SIOCGIFINDEX, ifreq)
        _ifname, self.interface_index = struct.unpack('16sI', response)

    def set_socket_promiscuous(self):
        mreq = struct.pack("IHH8s", self.interface_index, self.PACKET_MR_PROMISC, len(self.DUMMY_ADDRESS), self.DUMMY_ADDRESS)
        self.socket.setsockopt(self.SOL_PACKET, self.PACKET_ADD_MEMBERSHIP, mreq)

    def serve_forever(self):
        self.running = True
        self.socket = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(self.ethertype))
        self.socket.bind((self.interface_name, 0))
        self.get_interface_index()
        self.set_socket_promiscuous()
        self.poller = select.poll()
        self.poller.register(self.socket,
                          select.POLLIN |
                          select.POLLPRI |
                          select.POLLERR |
                          select.POLLHUP |
                          select.POLLNVAL)
        pool = GreenPool()
        self.greenlets.add(pool.spawn(self.server))
        self.greenlets.add(pool.spawn(self.dispatcher))
        pool.waitall()

    def server(self):
        try:
            while self.running:
                sleep(1)
                events = self.poller.poll(10)
                if events:
                    while events:
                        if len(events) > 1:
                            raise Exception("Too many events returned from poller")
                        fd, event = events[0]
                        if event == select.POLLERR or event == select.POLLHUP or event == select.POLLNVAL:
                            break
                        if event == select.POLLIN:
                            data = self.socket.recv(4096)
                            self.queue.put(data)
                        events = self.poller.poll(10)
        except OSError:
            pass

    def dispatcher(self):
        try:
            while self.running:
                data = self.queue.get()
                self.handler(data)
        except OSError:
            pass

    def call_handler(self, socket, address):
        self.greenlets.add(greenthread.getcurrent())
        self.handler(socket, address)
        self.greenlets.remove(greenthread.getcurrent())

    def stop(self):
        self.running = False
        for greenlet in self.greenlets:
            greenlet.kill()
        self.server.shutdown(socket.SHUT_RDWR)
