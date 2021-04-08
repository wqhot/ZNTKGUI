import socket
import time
import struct
import threading

run = True

def recv_thread():
    recv_port = 9002
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_socket.bind(("0.0.0.0", recv_port))
    while run:
        data = []
        while (len(data) < 10) and run:
            buff = b''
            buff = recv_socket.recv(10)
            # print(buff)
            buffArray = bytearray(buff)
            buffList = list(buffArray)
            index = buffArray.find(bytearray(b'\x55\xaa'))
            if index != -1:
                data = []
                buffList = buffList[index:]
            data.extend(buffList)
        stamp = struct.unpack('d', bytes(
                    data[2:]))[0]
        now_stamp = time.time() #/ (10 ** 9)
        print("delay: " + str(now_stamp - stamp))
        

def main():
    send_port = 9002
    send_address = ("192.168.0.211", send_port)
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    th = threading.Thread(target=recv_thread)
    th.start()

    while True:
        now_stamp = time.time() #/ (10 ** 9)
        buffer = struct.pack('d', now_stamp)
        buffer = b'\x55\xaa' + buffer
        # print('send: '+str(buffer))
        send_socket.sendto(buffer, send_address)
        time.sleep(0.01)
    



if __name__ == '__main__':
    main()
