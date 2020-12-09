# -*- coding: utf-8 -*-

import serial
import serial.tools.list_ports
import time
import math
import threading

__BUF_LENGTH = 40

def main():
    event = threading.Event()
    event.set()    

    port_list = list(serial.tools.list_ports.comports())
    for port,i in zip(port_list,range(len(port_list))):
        print('[' + str(i) + ']: ' + port.device)

    port_idx =  int(input("select port: "))
    # port_idx = 0

    port = port_list[port_idx]

    ser = serial.Serial(port=port.device, baudrate=921600, timeout=0.5)

    th = threading.Thread(target=wait_kay, args=(event,))
    th.start()

    th_recv = threading.Thread(target=recv_thread, args=(ser, event,))
    th_recv.start()

    count = 0

    ser.write(bytes(b'\xab'))

    while event.isSet():
        # count = count + 1
        # ser.write(bytes(b'\xab'))
        # if count % 100 == 0:
        #     print(str(2 * count) + ' bytes have been sent.')
        time.sleep(0.01)

def decode_imu(buffList):
    imu_num = 2
    omega_scale = [1.0 / 40.0, 1.0 / 160.0]
    ga = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
          0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    check_pass = True
    for i in range(imu_num):
        # 帧头
        sum = buffList[0] + buffList[1] - 0xea -0x90 - i

        # graw 6 bytes
        scale_g = omega_scale[i] * math.pi / 180.0
        for j in range(3):
            k_h = (i * 20) + 2 + (j * 2)
            k_l = (i * 20) + 3 + (j * 2)
            ga[j + 8 * i] = ((buffList[k_h] * 0x100 +  buffList[k_l]) if buffList[k_h] < 0x7f else (buffList[k_h] * 0x100 + buffList[k_l] - 0x10000))
            ga[j + 8 * i] = ga[j + 8 * i] * scale_g
            sum = sum + buffList[k_h] + buffList[k_l]
        # araw 6 bytes
        scale_a = 0.25 * 9.815 * 0.001
        for j in range(3):
            k_h = (i * 20) + 8 + (j * 2)
            k_l = (i * 20) + 9 + (j * 2)
            ga[j + 3 + 8 * i] = ((buffList[k_h] * 0x100 +  buffList[k_l]) if buffList[k_h] < 0x7f else (buffList[k_h] * 0x100 + buffList[k_l] - 0x10000))
            ga[j + 3 + 8 * i] = ga[j + 3 + 8 * i] * scale_a
            sum = sum + buffList[k_h] + buffList[k_l]

        # traw 2 bytes
        scale_t = 0.1
        k_h = (i * 20) + 14
        k_l = (i * 20) + 15
        ga[6 + 8 * i] = ((buffList[k_h] * 0x100 +  buffList[k_l]) if buffList[k_h] < 0x7f else (buffList[k_h] * 0x100 + buffList[k_l] - 0x10000))
        ga[6 + 8 * i] = ga[6 + 8 * i] * scale_t
        sum = sum + buffList[k_h] + buffList[k_l]

        # count 2 bytes
        scale_c = 49.07 / 1000.0
        k_h = (i * 20) + 16
        k_l = (i * 20) + 17
        ga[7 + 8 * i] = (buffList[k_h] * 0x100 +  buffList[k_l])
        ga[7 + 8 * i] = ga[7 + 8 * i] * scale_c
        sum = sum + buffList[k_h] + buffList[k_l]

        # sumcheck 2 bytes
        k_h = (i * 20) + 18
        k_l = (i * 20) + 19
        if sum & 0xff != buffList[k_l] or sum & 0xff00 != buffList[k_h]:
            check_pass = False

    return ga


def wait_kay(evt):
    key = input('[any key to quit]')
    evt.clear()

def recv_thread(ser, evt):
    fps = 0
    last_time = time.time()
    remainLength = __BUF_LENGTH
    while evt.isSet():
        buff = ser.read(remainLength)
        if len(buff) == 0:
                continue 
        remainLength = len(buff)
        buffArray = bytearray(buff)
        # 找帧头
        headIndex = buffArray.find(bytearray(b'\xea\x90'))
        if headIndex != -1:
            remainLength = __BUF_LENGTH - (remainLength - headIndex)
            buffList = []
            buffList.extend(list(buffArray)[headIndex:])
        else:  # 无帧头时
            buffList.extend(list(buffArray))
            remainLength = __BUF_LENGTH
            print("head not fount ")
            if len(buffList) > __BUF_LENGTH:
                buffList = []
                print("drop")
        if remainLength == 0:
            remainLength = __BUF_LENGTH

        # 收齐数据
        if len(buffList) == __BUF_LENGTH:
            ga = decode_imu(buffList)
            # print(buffList)
            print("[ imu head] ", end='')
            print("\tgx: " + format(ga[0],'.2f'), end='')
            print("\tgy: " + format(ga[1],'.2f'), end='')
            print("\tgz: " + format(ga[2],'.2f'), end='')
            print("\tax: " + format(ga[3],'.2f'), end='')
            print("\tay: " + format(ga[4],'.2f'), end='')
            print("\taz: " + format(ga[5],'.2f'), end='')
            print("\tt: " + format(ga[6],'.2f'), end='')
            print("\tstamp: " + format(ga[7],'.2f'))
            print("[imu board] ", end='')
            print("\tgx: " + format(ga[8],'.2f'), end='')
            print("\tgy: " + format(ga[9],'.2f'), end='')
            print("\tgz: " + format(ga[10],'.2f'), end='')
            print("\tax: " + format(ga[11],'.2f'), end='')
            print("\tay: " + format(ga[12],'.2f'), end='')
            print("\taz: " + format(ga[13],'.2f'), end='')
            print("\tt: " + format(ga[14],'.2f'), end='')
            print("\tstamp: " + format(ga[15],'.2f'))
            now_time = time.time()
            fps = fps * 0.8 + 1.0 / (now_time - last_time) * 0.2
            last_time = now_time
            print('[      FPS] \t' + format(fps,'.2f'))
        # if len(buff) > 0:
        #     print("recv: ", end='')
        #     print(buff)
    ser.close()


if __name__ == '__main__':
    main()