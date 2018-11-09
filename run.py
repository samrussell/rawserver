from rawserver.rawserver import Rawserver

interface_name = "eth0"
ethertype = 0x0800

def handle_message(data):
    print("Got data %s" % data)

server = Rawserver(interface_name, ethertype, handle_message)

server.serve_forever()
