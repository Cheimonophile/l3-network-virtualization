import socket
import sys
import netifaces
from threading import Thread





def ether_header(iface):
  src_ether_addr = netifaces.ifaddresses(iface)[netifaces.AF_LINK][0]['addr']
  src_bytes = [
    int(byte_str,16)
    for byte_str in src_ether_addr.split(':')
  ]
  dst_bytes = [0xff]*6
  ethertype_bytes = [0x55, 0x55]
  return bytes(dst_bytes + src_bytes + ethertype_bytes)





# create the socket server
def virtualize(plain_if, virtual_if, id):

  # setup socket server
  in_sock = socket.socket(
    socket.AF_PACKET,
    socket.SOCK_DGRAM,
    socket.ntohs(0x0800) # socket.ntohs(3)
  )
  out_sock = socket.socket(
    socket.AF_PACKET,
    socket.SOCK_RAW,
    socket.ntohs(3)
  )
  with in_sock, out_sock:
    in_sock.bind((plain_if,0))
    out_sock.bind((virtual_if,0))
    while(True):
      raw_in_data_bytes, _ = in_sock.recvfrom(65565)
      raw_in_data_list = list(raw_in_data_bytes)
      print(f"{raw_in_data_list=}")
      raw_out_data_list = [id] + raw_in_data_list
      print(f"{raw_out_data_list=}")
      payload = ether_header(virtual_if) + bytes(raw_out_data_list)
      print(*[hex(b) for b in list(payload)])
      out_sock.send(payload)



def main(*argv):

  # get sockets
  plain_if, virtual_if, id = argv
  id = int(id)
  print(f"{plain_if=}")
  print(f"{virtual_if=}")
  print(f"{id=}")

  # start virtualizations
  threads = [
    Thread(target=virtualize, args=[plain_if,virtual_if,id])
  ]
  for thread in threads:
    thread.start()
  for thread in threads:
    thread.join()



if __name__ == "__main__":
  print(f"{sys.argv=}")
  main(*sys.argv[1:])