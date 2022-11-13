import socket
import sys
from threading import Thread



# create the socket server
def virtualize(plain_if, virtual_if, id):

  # setup socket server
  in_sock = socket.socket(
    socket.AF_PACKET,
    socket.SOCK_DGRAM,
    socket.ntohs(3)
  )
  in_sock.bind((plain_if,0))
  while(True):
    raw_data, addr = in_sock.recvfrom(65565)
    print(f"{addr=}")
    print(raw_data)
    ip = list(raw_data)
    print(f"{ip=}")



def main(*argv):

  # get sockets
  plain_if, virtual_if, id = argv
  print(f"{plain_if=}")
  print(f"{virtual_if=}")
  print(f"{id=}")

  # start virtualization
  virtualize(plain_if, virtual_if, id)



if __name__ == "__main__":
  print(f"{sys.argv=}")
  main(*sys.argv[1:])