import socket
import sys
import netifaces
from threading import Thread
import uuid
import math


SWITCH_ID = list(uuid.uuid4().bytes)
SWITCH_ID_LEN = len(SWITCH_ID)
MTU = 700



def ether_header(dst_iface, ethertype=0x5555):
  src_ether_addr = netifaces.ifaddresses(dst_iface)[netifaces.AF_LINK][0]['addr']
  src_bytes = [
    int(byte_str,16)
    for byte_str in src_ether_addr.split(':')
  ]
  dst_bytes = [0xff]*6
  ethertype_bytes = list(ethertype.to_bytes(2,'big'))
  return bytes(dst_bytes + src_bytes + ethertype_bytes)





# create the socket server
def virtualize(plain_if, virtual_if, prot_id):

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
    while True:
      raw_in_data_bytes, _ = in_sock.recvfrom(65565)
      print('\nIN')
      raw_in_data_list = list(raw_in_data_bytes)
      print(f"{len(raw_in_data_list)=}")
      print(f"{raw_in_data_list=}")

      # send the packet
      data_size = len(raw_in_data_list)
      for i in range(0,data_size,MTU):
        packet_id = list(uuid.uuid4().bytes)
        raw_out_data_list = [prot_id] + SWITCH_ID + packet_id + [int(i/MTU), math.ceil(data_size/MTU)]  + raw_in_data_list[i:i+MTU]
        print(f"{raw_out_data_list=}")
        payload = ether_header(virtual_if) + bytes(raw_out_data_list)
        # print(*[hex(b) for b in list(payload)])
        out_sock.send(payload)
      print()




def devirtualize(virtual_if, plain_if, id):
  in_sock = socket.socket(
    socket.AF_PACKET,
    socket.SOCK_DGRAM,
    socket.ntohs(3) # socket.ntohs(3)
  )
  out_sock = socket.socket(
    socket.AF_PACKET,
    socket.SOCK_RAW,
    socket.ntohs(3)
  )
  with in_sock, out_sock:
    in_sock.bind((virtual_if,0))
    out_sock.bind((plain_if,0))
    while True:
      raw_in_data_bytes, _ = in_sock.recvfrom(65565)
      print("\nOUT")
      raw_in_data_list = list(raw_in_data_bytes)
      print(f"{raw_in_data_list=}")
      raw_out_data_list = raw_in_data_list[1:]
      print(f"{raw_out_data_list=}")
      payload = ether_header(plain_if, ethertype=0x0800) + bytes(raw_out_data_list)
      print(*[hex(b) for b in list(payload)])
      out_sock.send(payload)
      print()



def main(*argv):

  # get sockets
  plain_if, virtual_if, id = argv
  id = int(id)
  print(f"{plain_if=}")
  print(f"{virtual_if=}")
  print(f"{id=}")

  # start virtualizations
  threads = [
    Thread(target=virtualize, args=[plain_if,virtual_if,id]),
    # Thread(target=devirtualize, args=[virtual_if,plain_if,id])
  ]
  for thread in threads:
    thread.start()
  for thread in threads:
    thread.join()



if __name__ == "__main__":
  print(f"{sys.argv=}")
  main(*sys.argv[1:])