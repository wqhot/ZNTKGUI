# -*- coding: utf-8 -*-
import threading
import serial
import time


class ztStatus():
    def __init__(self):
        self.status = -1
        self.firstAxisPos = 0
        self.firstAxisVelocity = 0
        self.secondAxisPos = 0
        self.secondAxisVelocity = 0

    def setAxisValue(self, axis, pos, velocity):
        if axis == 1:
            self.firstAxisPos = pos
            self.firstAxisVelocity = velocity
        elif axis == 2:
            self.secondAxisPos = pos
            self.secondAxisVelocity = velocity

    def toDict(self):
        dc = {}
        dc["firstAxisPos"] = self.firstAxisPos
        dc["firstAxisVelocity"] = self.firstAxisVelocity
        dc["secondAxisPos"] = self.secondAxisPos
        dc["secondAxisVelocity"] = self.secondAxisVelocity
        return dc


class ztTask():
    # type:
    # 0x1: 上电
    # 0x2: 下电
    # 0x3: 闭合
    # 0x4: 闲置
    # 0x5: 运行
    # 0x6: 停止
    # 0x7: 位置方式
    # 0x8: 速率方式
    # 0x9: 摇摆方式
    # 0xb: 归零
    # 0xc: 停止归零
    # 0xd: 等待
    # axis:
    # 1 航向
    # 2 俯仰
    # 3 航向+俯仰
    # runType_1 航向轴的运动方式
    # 5 位置 6 速率 7 摇摆
    # runType_2 俯仰轴的运动方式
    # 5 位置 6 速率 7 摇摆
    def __init__(self, type, axis=0, runType_1=0, runType_2=0,
                 pos_p=0, pos_v=0, pos_a=0, vel_v=0, vel_a=0,
                 swing_range=0, swing_freq=0, swing_dur=0, delay=0):
        self.type = type
        self.command = bytearray(14)
        self.delay = delay
        for c in self.command:
            c = 0
        self.command[1] = type
        self.command[0] = axis
        if type in [7, 8, 9, 0x0b, 0x0c] and axis > 2:  # 只能同时运行一个轴
            print("只能同时运行一个轴")
            self.command = bytearray(b'')
            return
        if type == 5:  # 运行设置
            if axis & 1 != 0:
                self.command[2] = runType_1
            if axis & 2 != 0:
                self.command[6] = runType_2
        c_p = 0
        c_v = 0
        c_a = 0
        if type == 7: # 位置设置
            c_p = int(pos_p * 10000)
            c_v = int(pos_v * 10000)
            c_a = int(pos_a * 10000)
        elif type == 8: # 速率设置
            c_p = int(vel_v * 10000)
            c_v = int(vel_a * 10000)
        elif type == 9: # 摇摆设置
            c_p = int(swing_range * 10000)
            c_v = int(swing_freq * 10000)
            c_a = int(swing_dur * 10000)
        if type in [7, 8, 9]: # 设置
            for i in range(4):
                self.command[2 + i] = (c_p & (0xff << (i * 8))) >> (i * 8)
                self.command[6 + i] = (c_v & (0xff << (i * 8))) >> (i * 8)
                self.command[10 + i] = (c_a & (0xff << (i * 8))) >> (i * 8)
        if type == 0x0d: # delay
            self.command = bytearray(b'')

# 调度器负责两个任务：
# 对转台写命令，并延时等待执行
# 定时读取转台数据，通过回调函数范围
class ztScheduler():
    def __init__(self, readCallback, finishCallback=None, portname='/dev/ttyUSB1'):
        self.callback = readCallback
        self.finishCallback = finishCallback
        self.taskList = []
        self.readelay = 0.001
        self.readrun = True
        con = self.zt902e1 = zt902e1(callback=self.callback, portname=portname)
        self.readth = threading.Thread(target=self.readProcess, daemon=True)
        self.th = threading.Thread(target=self.process, daemon=True)

    
    def addTask(self, task):
        self.taskList.append(task)
    
    def run(self, readFPS = 1000):
        self.readrun = True   
        # 开始接收数据
        self.readelay = 1.0 / readFPS      
        self.readth.start()
        # 开始运行任务       
        self.th.start()
        
    
    def readProcess(self):
        while self.readrun:
            self.zt902e1.getValue()
            time.sleep(self.readelay)

    def process(self):
        for task in self.taskList:
            if task.type == 0x0d:
                time.sleep(task.delay)
                continue
            self.zt902e1.sendCommand(task.command)
            print(task.command)
        self.readrun = False
        if self.finishCallback is not None:
            self.finishCallback()

class zt902e1():
    def __init__(self, callback, portname='/dev/ttyUSB1'):
        portName = portname
        bps = 9600
        time = 0.5
        self.mutex = threading.Lock()
        self.ser = None
        # self.ser = serial.Serial(port=portName, baudrate=bps, timeout=0.5)
        self.recvrun = True
        # self.ser.open()
        # self.th_recv = threading.Thread(target=self.recv, daemon=True)
        # self.th_recv.start()
        self.callback = callback
        self.send() # 建立链接
        self.connected = self.recv() # 接收建立连接返回信号


    def getValue(self):
        status = ztStatus()
        # 01
        command = b'\x01\x0a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        if self.sendCommand(command):
            self.recv(status=status)
        # 02
        command = b'\x02\x0a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        if self.sendCommand(command):
            self.recv(status=status)
        # callback
        self.callback(status.toDict())

    def recv(self, status=None):
        length = 15
        sum = 0
        # buff = self.ser.read(length)
        buff = b'\x02\x0a\xa0\x86\x01\x00\xc0\xd4\x01\x00\xa0\x86\x01\x00\x11'
        buffArray = list(bytearray(buff))
        # 校验
        for b in buffArray:
            sum += b
        sum %= 256
        if sum == 0:
            if buffArray[1] == 0x55:
                return True
            elif buffArray[1] == 0x0a and status is not None:
                pos = 0
                velocity = 0
                for i in range(2, 6, 1):
                    pos |= (buffArray[i] << 8 * (i - 2))
                    velocity |= (buffArray[i + 4] << 8 * (i - 2))
                pos *= 0.0001
                velocity *= 0.0001
                status.setAxisValue(buffArray[0], pos, velocity)
                return True
        else:
            print("校验失败")
        return False

    def sendCommand(self, command):
        if self.mutex.acquire(timeout=0.5):
            sendbuff = bytearray(command)
            # test
            sum = 0
            for i in range(len(sendbuff)):
                sum = sum + int(sendbuff[i])
            sum = (~(sum % 256))
            sum &= 0xffffffff
            sum %= 256
            sum += 1
            #
            tempSum = bytearray(1)
            tempSum[0] = sum
            buf = command + bytes(tempSum)
            # self.ser.write(buf)
            # self.ser.write(str(tempSum[0], encoding='utf-8'))
            self.mutex.release()
            return True
        else:
            return False

    def send(self):
        # 建立通信
        startbuff = b'\x00\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.sendCommand(startbuff)


# def cbTest(status):
#     print(status)


# # aa = zt902e1(cbTest)
# ss = ztScheduler(cbTest)

# cc = ztTask(type=7,axis=2, pos_p=10, pos_v=12, pos_a=10)
# ss.addTask(cc)
# cc = ztTask(type=7,axis=1, pos_p=20, pos_v=12, pos_a=10)
# ss.addTask(cc)
# cc = ztTask(type=5,axis=3, runType_1=5, runType_2=5)
# ss.addTask(cc)
# cc = ztTask(type=0x0d,axis=3, delay=10)
# ss.addTask(cc)
# cc = ztTask(type=6,axis=3)
# ss.addTask(cc)
# cc = ztTask(type=7,axis=2, pos_p=10, pos_v=12, pos_a=10)
# ss.addTask(cc)
# cc = ztTask(type=7,axis=1, pos_p=20, pos_v=12, pos_a=10)
# ss.addTask(cc)
# cc = ztTask(type=5,axis=3, runType_1=5, runType_2=5)
# ss.addTask(cc)
# cc = ztTask(type=0x0d,axis=3, delay=10)
# ss.addTask(cc)
# cc = ztTask(type=6,axis=3)
# ss.addTask(cc)
# ss.run(1)
