import socket
import sys
import netifaces
from threading import Thread
import uuid
import math
import json




# get interfaces
CONFIG = json.loads(sys.stdin.read())
HOST_IF = CONFIG['host']
HOST_MACS = {x['addr'] for x in netifaces.ifaddresses(HOST_IF)[netifaces.AF_LINK]}
NETWORK_IF = CONFIG['network']
NETWORK_MACS = {x['addr'] for x in netifaces.ifaddresses(NETWORK_IF)[netifaces.AF_LINK]}
ID = CONFIG['id']
PROTOCOLS = {ether_id: name for name, ether_id in CONFIG['protocols'].items()}
print(f"{ID=}")
print(f"{HOST_IF=}")
print(f"{HOST_MACS=}")
print(f"{NETWORK_IF=}")
print(f"{NETWORK_MACS=}")
print(f"{PROTOCOLS=}")


def parse_ether_addr(addr):
  return [
    int(byte_str,16)
    for byte_str in addr.split(':')
  ]

def serialize_ether_addr(addr):
  return ':'.join(
    hex(b)[2:].rjust(2,'0')
    for b in addr
  )

def ether_header(dst_iface):
  src_ether_addr = netifaces.ifaddresses(dst_iface)[netifaces.AF_LINK][0]['addr']
  src_bytes = parse_ether_addr(src_ether_addr)
  dst_bytes = [0xff]*6
  return bytes(dst_bytes + src_bytes)





# create the socket server
def virtualize():

  # setup socket server
  in_sock = socket.socket(
    socket.AF_PACKET,
    socket.SOCK_RAW,
    socket.ntohs(3) # socket.ntohs(3)
  )
  out_sock = socket.socket(
    socket.AF_PACKET,
    socket.SOCK_RAW,
    socket.ntohs(3)
  )
  with in_sock, out_sock:
    in_sock.bind((HOST_IF,0))
    out_sock.bind((NETWORK_IF,0))
    while True:
      raw_in_data_bytes, _ = in_sock.recvfrom(65565)
      in_protocol = int.from_bytes(raw_in_data_bytes[12:14],'big')
      if in_protocol not in PROTOCOLS: continue # filter for accepted protocols
      print()
      print(f'HOST > NETWORK ({PROTOCOLS[in_protocol]})')
      raw_in_data_list = list(raw_in_data_bytes)
      print(f"{len(raw_in_data_list)=}")
      print(f"{raw_in_data_list=}")

      # send the packet
      data_size = len(raw_in_data_list)
      raw_out_data_list = raw_in_data_list[12:]
      print(f"{raw_out_data_list=}")
      payload = ether_header(NETWORK_IF) + bytes(raw_out_data_list)
      out_sock.send(payload)
      print()




def devirtualize():
  in_sock = socket.socket(
    socket.AF_PACKET,
    socket.SOCK_RAW,
    socket.ntohs(3) # socket.ntohs(3)
  )
  out_sock = socket.socket(
    socket.AF_PACKET,
    socket.SOCK_RAW,
    socket.ntohs(3)
  )
  with in_sock, out_sock:
    in_sock.bind((NETWORK_IF,0))
    out_sock.bind((HOST_IF,0))
    while True:
      print()
      raw_in_data_bytes, _ = in_sock.recvfrom(65565)
      src_ether_addr = serialize_ether_addr(raw_in_data_bytes[6:12])
      if src_ether_addr in NETWORK_MACS: continue # skip duplicated traffic
      print("NETWORK > HOST")
      raw_in_data_list = list(raw_in_data_bytes)
      print(f"{raw_in_data_list=}")
      raw_out_data_list = raw_in_data_list[12:]
      print(f"{raw_out_data_list=}")
      payload = ether_header(HOST_IF, ethertype=0x0800) + bytes(raw_out_data_list)
      out_sock.send(payload)
      print()



def main():

  # start virtualizations
  threads = [
    Thread(target=virtualize),
    Thread(target=devirtualize)
  ]
  for thread in threads:
    thread.start()
  for thread in threads:
    thread.join()



if __name__ == "__main__":
  main()