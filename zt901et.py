# -*- coding: utf-8 -*-
import threading
import serial
import time

class ztTaskType():
    type = [
        {
            "name": "开机一条龙(上电->闭合->归零->延时100s)",
            "axis": True,
            "opt1": False,
            "opt2": False,
            "opt3": False,
            "opt4": False,
            "opt1name": "无效",
            "opt2name": "无效",
            "opt3name": "无效",
            "opt4name": "无效"
        },
        {
            "name": "关机一条龙(停止->闲置->下电)",
            "axis": True,
            "opt1": False,
            "opt2": False,
            "opt3": False,
            "opt4": False,
            "opt1name": "无效",
            "opt2name": "无效",
            "opt3name": "无效",
            "opt4name": "无效"
        },
        {
            "name": "位置设置一条龙(位置方式设置->运行->延时)",
            "axis": True,
            "opt1": True,
            "opt2": True,
            "opt3": True,
            "opt4": True,
            "opt1name": "位置",
            "opt2name": "速度",
            "opt3name": "加速度",
            "opt4name": "延时"
        },
        {
            "name": "速率设置一条龙(速率方式设置->运行->延时)",
            "axis": True,
            "opt1": True,
            "opt2": True,
            "opt3": True,
            "opt4": False,
            "opt1name": "速度",
            "opt2name": "加速度",
            "opt3name": "延时",
            "opt4name": "无效"
        },
        {
            "name": "摇摆设置一条龙(摇摆方式设置->运行->延时)",
            "axis": True,
            "opt1": True,
            "opt2": True,
            "opt3": True,
            "opt4": False,
            "opt1name": "幅度",
            "opt2name": "频率",
            "opt3name": "延时",
            "opt4name": "无效"
        },
        {
            "name": "上电",
            "axis": True,
            "opt1": False,
            "opt2": False,
            "opt3": False,
            "opt4": False,
            "opt1name": "无效",
            "opt2name": "无效",
            "opt3name": "无效",
            "opt4name": "无效"
        },
        {
            "name": "下电",
            "axis": True,
            "opt1": False,
            "opt2": False,
            "opt3": False,
            "opt4": False,
            "opt1name": "无效",
            "opt2name": "无效",
            "opt3name": "无效",
            "opt4name": "无效"
        },
        {
            "name": "闭合",
            "axis": True,
            "opt1": False,
            "opt2": False,
            "opt3": False,
            "opt4": False,
            "opt1name": "无效",
            "opt2name": "无效",
            "opt3name": "无效",
            "opt4name": "无效"
        },
        {
            "name": "闲置",
            "axis": True,
            "opt1": False,
            "opt2": False,
            "opt3": False,
            "opt4": False,
            "opt1name": "无效",
            "opt2name": "无效",
            "opt3name": "无效",
            "opt4name": "无效"
        },
        {
            "name": "运行",
            "axis": False,
            "opt1": False,
            "opt2": False,
            "opt3": False,
            "opt4": False,
            "opt1name": "无效",
            "opt2name": "无效",
            "opt3name": "无效",
            "opt4name": "无效"
        },
        {
            "name": "停止",
            "axis": True,
            "opt1": False,
            "opt2": False,
            "opt3": False,
            "opt4": False,
            "opt1name": "无效",
            "opt2name": "无效",
            "opt3name": "无效",
            "opt4name": "无效"
        },
        {
            "name": "位置方式设置",
            "axis": True,
            "opt1": True,
            "opt2": True,
            "opt3": True,
            "opt4": False,
            "opt1name": "位置",
            "opt2name": "速度",
            "opt3name": "加速度",
            "opt4name": "无效"
        },
        {
            "name": "速率方式设置",
            "axis": True,
            "opt1": True,
            "opt2": True,
            "opt3": True,
            "opt4": False,
            "opt1name": "速度",
            "opt2name": "加速度",
            "opt3name": "无效",
            "opt4name": "无效"
        },
        {
            "name": "速率方式设置",
            "axis": True,
            "opt1": True,
            "opt2": True,
            "opt3": True,
            "opt4": False,
            "opt1name": "速度",
            "opt2name": "加速度",
            "opt3name": "无效",
            "opt4name": "无效"
        },
        {
            "name": "归零",
            "axis": True,
            "opt1": False,
            "opt2": False,
            "opt3": False,
            "opt4": False,
            "opt1name": "无效",
            "opt2name": "无效",
            "opt3name": "无效",
            "opt4name": "无效"
        },
        {
            "name": "停止归零",
            "axis": True,
            "opt1": False,
            "opt2": False,
            "opt3": False,
            "opt4": False,
            "opt1name": "无效",
            "opt2name": "无效",
            "opt3name": "无效",
            "opt4name": "无效"
        },
        {
            "name": "延时",
            "axis": False,
            "opt1": True,
            "opt2": False,
            "opt3": False,
            "opt4": False,
            "opt1name": "延时",
            "opt2name": "无效",
            "opt3name": "无效",
            "opt4name": "无效"
        },
        {
            "name": "循环开始",
            "axis": False,
            "opt1": True,
            "opt2": False,
            "opt3": False,
            "opt4": False,
            "opt1name": "循环次数",
            "opt2name": "无效",
            "opt3name": "无效",
            "opt4name": "无效"
        },
        {
            "name": "循环结束",
            "axis": False,
            "opt1": False,
            "opt2": False,
            "opt3": False,
            "opt4": False,
            "opt1name": "无效",
            "opt2name": "无效",
            "opt3name": "无效",
            "opt4name": "无效"
        },
        {
            "name": "保存文件截断",
            "axis": False,
            "opt1": False,
            "opt2": False,
            "opt3": False,
            "opt4": False,
            "opt1name": "无效",
            "opt2name": "无效",
            "opt3name": "无效",
            "opt4name": "无效"
        },
    ]

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
    # 0xe: 循环开始
    # 0xf: 循环结束
    # 0x10: 截断保存文件
    # axis:
    # 1 航向
    # 2 俯仰
    # 3 航向+俯仰
    # runType_1 航向轴的运动方式
    # 5 位置 6 速率 7 摇摆
    # runType_2 俯仰轴的运动方式
    # 5 位置 6 速率 7 摇摆
    # repeat 循环次数
    def __init__(self, type, axis=0, runType_1=0, runType_2=0,
                 pos_p=0, pos_v=0, pos_a=0, vel_v=0, vel_a=0,
                 swing_range=0, swing_freq=0, swing_dur=0, delay=0, repeat=0, fatherID=-1):
        self.type = type
        self.command = bytearray(14)
        self.delay = abs(delay)
        self.repeat = abs(int(repeat))
        self.fatherID = fatherID # 保存主界面中列表序号，用于回显
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
            c_p = c_p if c_p >= 0 else c_p + 0x1000000
            c_v = c_v if c_v >= 0 else abs(c_v)
            c_a = c_a if c_a >= 0 else abs(c_a)
        elif type == 8: # 速率设置
            c_p = int(vel_v * 10000)
            c_v = int(vel_a * 10000)
            c_p = c_p if c_p >= 0 else c_p + 0x1000000
            c_v = c_v if c_v >= 0 else abs(c_v)
        elif type == 9: # 摇摆设置
            c_p = int(swing_range * 10000)
            c_v = int(swing_freq * 10000)
            c_a = int(swing_dur * 10000)
            c_p = c_p if c_p >= 0 else c_p + 0x1000000
            c_v = c_v if c_v >= 0 else abs(c_v)
            c_a = c_a if c_a >= 0 else abs(c_a)
        if type in [7, 8, 9]: # 设置
            for i in range(4):
                self.command[2 + i] = (c_p & (0xff << (i * 8))) >> (i * 8)
                self.command[6 + i] = (c_v & (0xff << (i * 8))) >> (i * 8)
                self.command[10 + i] = (c_a & (0xff << (i * 8))) >> (i * 8)
        if type == 0x0d: # delay
            self.command = bytearray(b'')
        if type == 0x0e: # 循环开始
            self.command = bytearray(b'')
        if type == 0x0f: # 循环结束
            self.command = bytearray(b'')
        if type == 0x10: # 截断保存文件
            self.command = bytearray(b'')

# 调度器负责两个任务：
# 对转台写命令，并延时等待执行
# 定时读取转台数据，通过回调函数范围
class ztScheduler():
    def __init__(self, readCallback, port, event_1, event_2, finishCallback=None):
        self.callback = readCallback
        self.finishCallback = finishCallback
        self.taskList = []
        self.unrollingTaskList = []
        self.readelay = 0.001
        self.readrun = True
        self.enableCallback = False
        self.event_1 = event_1
        self.event_2 = event_2
        self.waitCond = threading.Condition()
        self.zt902e1 = zt902e1(callback=self.callback, port=port)
        self.readth = threading.Thread(target=self.readProcess, daemon=True)
        self.th = threading.Thread(target=self.process, daemon=True)
    def createTasks(self, oriTasks):
        taskLst = []
        runtype1 = 5
        runtype2 = 5
        fatherID = 0
        for t in oriTasks:
            # 开机一条龙
            if t["id"] == 0:
                task = ztTask(type=1, axis=t["axis"], fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0, fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=3, axis=t["axis"], fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0, fatherID=fatherID)
                taskLst.append(task)
                if t["axis"] & 1 != 0:
                    task = ztTask(type=0x0b, axis=1, fatherID=fatherID)
                    taskLst.append(task)
                    task = ztTask(type=0xd, delay=100, fatherID=fatherID)
                    taskLst.append(task)
                if t["axis"] & 2 != 0:
                    task = ztTask(type=0x0b, axis=2, fatherID=fatherID)
                    taskLst.append(task)
                    task = ztTask(type=0xd, delay=100, fatherID=fatherID)
                    taskLst.append(task)
            # 关机一条龙
            if t["id"] == 1:
                task = ztTask(type=6, axis=t["axis"], fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0, fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=4, axis=t["axis"], fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0, fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=2, axis=t["axis"], fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0, fatherID=fatherID)
                taskLst.append(task)

            # 位置设置一条龙
            if t["id"] == 2:
                task = ztTask(
                    type=7, axis=t["axis"], pos_p=t["opt1"], pos_v=t["opt2"], pos_a=t["opt3"], fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0, fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=5, axis=t["axis"], runType_1=5, runType_2=5, fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=0xd, delay=t["opt4"], fatherID=fatherID)
                taskLst.append(task)

            # 速率设置一条龙
            if t["id"] == 3:
                task = ztTask(type=8, axis=t["axis"],
                              vel_v=t["opt1"], vel_a=t["opt2"], fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0, fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=5, axis=t["axis"], runType_1=6, runType_2=6, fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=0xd, delay=t["opt4"], fatherID=fatherID)
                taskLst.append(task)

            # 摇摆设置一条龙
            if t["id"] == 4:
                task = ztTask(
                    type=9, axis=t["axis"], swing_range=t["opt1"], swing_freq=t["opt2"], swing_dur=t["opt3"], fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0, fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=5, axis=t["axis"], runType_1=7, runType_2=7, fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=0xd, delay=t["opt3"] + 1, fatherID=fatherID)
                taskLst.append(task)

            # 上电 下电 闭合 闲置 运行 停止
            if t["id"] in [5, 6, 7, 8, 9, 10]:
                task = ztTask(type=t["id"] - 4, axis=t["axis"],
                              runType_1=runtype1, runType_2=runtype2, fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0, fatherID=fatherID)
                taskLst.append(task)

            # 位置设置
            if t["id"] == 11:
                task = ztTask(
                    type=7, axis=t["axis"], pos_p=t["opt1"], pos_v=t["opt2"], pos_a=t["opt3"], fatherID=fatherID)
                taskLst.append(task)
                if t["axis"] & 1 != 0:
                    runtype1 = 5
                if t["axis"] & 2 != 0:
                    runtype2 = 5
                task = ztTask(type=0x0d, delay=5.0, fatherID=fatherID)
                taskLst.append(task)
            # 速率设置
            if t["id"] == 12:
                task = ztTask(type=8, axis=t["axis"],
                              vel_v=t["opt1"], vel_a=t["opt2"], fatherID=fatherID)
                taskLst.append(task)
                if t["axis"] & 1 != 0:
                    runtype1 = 6
                if t["axis"] & 2 != 0:
                    runtype2 = 6
                task = ztTask(type=0x0d, delay=5.0, fatherID=fatherID)
                taskLst.append(task)

            # 摇摆设置
            if t["id"] == 13:
                task = ztTask(
                    type=9, axis=t["axis"], swing_range=t["opt1"], swing_freq=t["opt2"], swing_dur=t["opt3"], fatherID=fatherID)
                taskLst.append(task)
                if t["axis"] & 1 != 0:
                    runtype1 = 7
                if t["axis"] & 2 != 0:
                    runtype2 = 7
                task = ztTask(type=0x0d, delay=5.0, fatherID=fatherID)
                taskLst.append(task)

            # 归零 停止归零
            if t["id"] in [14, 15]:
                task = ztTask(type=t["id"] - 3, axis=t["axis"], fatherID=fatherID)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0, fatherID=fatherID)
                taskLst.append(task)

            # 保持
            if t["id"] == 16:
                task = ztTask(type=0x0d, delay=t["opt1"], fatherID=fatherID)
                taskLst.append(task)

            # 循环开始
            if t["id"] == 17:
                task = ztTask(type=0x0e, repeat=t["opt1"], fatherID=fatherID)
                taskLst.append(task)

            # 循环结束
            if t["id"] == 18:
                task = ztTask(type=0x0f, fatherID=fatherID)
                taskLst.append(task)

            # 截断文件
            if t["id"] == 19:
                task = ztTask(type=0x10, fatherID=fatherID)
                taskLst.append(task)
            fatherID += 1
        return taskLst

    def setProgressCallback(self, callback):
        self.enableCallback = True
        self.progressCallback = callback

    def addTask(self, task):
        self.taskList.append(task)
    
    def loopUnrolling(self):
        repeatList = []
        self.unrollingTaskList = []
        startUnrolling = False
        repeat = 0
        for task in self.taskList:
            if task.type == 0x0e: #循环开始
                startUnrolling = True
                repeatList = []
                repeat = task.repeat
            elif task.type == 0x0f: #循环结束
                startUnrolling = False
                self.unrollingTaskList.extend(repeatList * repeat)
            else:
                if startUnrolling:
                    repeatList.append(task)
                else:
                    self.unrollingTaskList.append(task)
            

    def run(self, readFPS = 1000):
        self.readrun = True   
        # 开始接收数据
        if (readFPS > 0):
            self.readelay = 1.0 / readFPS      
            self.readth.start()
        # 开始运行任务 
        self.loopUnrolling()      
        self.th.start()
        
    def readProcess(self):
        while self.readrun:
            self.waitCond.acquire()
            self.zt902e1.getValue()
            self.waitCond.release()
            time.sleep(self.readelay)

    def process(self):
        taskCount = 0
        for task in self.unrollingTaskList:
            taskCount += 1
            if task.type == 0x0d:
                # print("delay")
                time.sleep(task.delay)
                continue
            if task.type == 0x10:
                self.event_1.set()
                self.event_2.set()
            if task.type in [0x0e, 0x0f]:
                continue
            self.waitCond.acquire()
            self.zt902e1.sendCommand(task.command)
            if self.enableCallback:
                self.progressCallback(
                    float(taskCount / len(self.unrollingTaskList)), task.fatherID)
            time.sleep(0.5)
            self.waitCond.notifyAll()
            self.waitCond.release()
            # print(task.command)
        self.readrun = False
        if self.finishCallback is not None:
            self.finishCallback()

class zt902e1():
    def __init__(self, callback, port):
        bps = 9600
        time = 0.005
        self.mutex = threading.Lock()
        if port is None:
            self.connected = False
            return
        self.ser = serial.Serial(port=port.device, baudrate=bps, timeout=0.5)
        self.recvrun = True
        # self.ser.open()
        # self.th_recv = threading.Thread(target=self.recv, daemon=True)
        # self.th_recv.start()
        self.callback = callback
        self.send() # 建立链接
        self.connected = self.recv() # 接收建立连接返回信号
        self.connected = True


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
        buff = self.ser.read(length)
        # print("recv: ", end='')
        # print(buff)
        # buff = b'\x02\x0a\xa0\x86\x01\x00\xc0\xd4\x01\x00\xa0\x86\x01\x00\x11'
        buffArray = list(bytearray(buff))
        if len(buff) != length:
            return False
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
                if pos > 0x10000000: # 负数                  
                    pos -= 0xffffffff
                if velocity > 0x10000000: # 负数
                    velocity -= 0xffffffff
                pos *= 0.0001
                velocity *= 0.0001
                status.setAxisValue(buffArray[0], pos, velocity)
                return True
        else:
            print("校验失败")
        return False

    def sendCommand(self, command):
        sendbuff = bytearray(command)
        # test
        sum = 0
        for i in range(len(sendbuff)):
            sum = sum + int(sendbuff[i])
        sum = 256 - (sum % 256)
        sum %= 256
        #
        tempSum = bytearray(1)
        tempSum[0] = sum
        buf = bytes(command) + bytes(tempSum)
        if self.mutex.acquire(timeout=0.5):      
            # print('send:', end='')
            # print(buf)
            self.ser.write(buf)
            # self.ser.write(str(tempSum[0], encoding='utf-8'))
            self.mutex.release()
            # time.sleep(0.1)
            return True
        else:
            return False

    def send(self):
        # 建立通信
        startbuff = b'\x00\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.sendCommand(startbuff)
        
