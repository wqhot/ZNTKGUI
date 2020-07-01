# -*- coding: utf-8 -*-
import threading
import serial
import time
# self.comboBox.setItemText(0, _translate("Dialog", "开机一条龙(建立通信->闭合->归零->延时100s)"))
#         self.comboBox.setItemText(1, _translate("Dialog", "关机一条龙(停止->闲置->断开)"))
#         self.comboBox.setItemText(2, _translate("Dialog", "位置运动模式"))
#         self.comboBox.setItemText(3, _translate("Dialog", "速度运动模式"))
#         self.comboBox.setItemText(4, _translate("Dialog", "正弦运动模式"))
#         self.comboBox.setItemText(5, _translate("Dialog", "增量运动模式"))
#         self.comboBox.setItemText(6, _translate("Dialog", "建立通信"))
#         self.comboBox.setItemText(7, _translate("Dialog", "闭合"))
#         self.comboBox.setItemText(8, _translate("Dialog", "闲置"))
#         self.comboBox.setItemText(9, _translate("Dialog", "断开通信"))
#         self.comboBox.setItemText(10, _translate("Dialog", "停止"))
#         self.comboBox.setItemText(11, _translate("Dialog", "归零"))
#         self.comboBox.setItemText(12, _translate("Dialog", "延时"))
#         self.comboBox.setItemText(13, _translate("Dialog", "循环开始"))
#         self.comboBox.setItemText(14, _translate("Dialog", "循环结束"))


class ztTaskType():
    type = [
        {
            "name": "开机一条龙(建立通信->闭合->归零->延时100s)",
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
            "name": "关机一条龙(停止->闲置->断开)",
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
            "name": "位置运动模式",
            "axis": False,
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
            "name": "速度运动模式",
            "axis": False,
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
            "name": "正弦运动模式",
            "axis": False,
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
            "name": "增量运动模式",
            "axis": False,
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
            "name": "建立通信",
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
            "name": "闭合",
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
            "name": "闲置",
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
            "name": "断开通信",
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
            "name": "归零",
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
            "name": "延时",
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
    # 0x55: 建立通讯
    # 0x66: 退出远控
    # 0x01: 闭合
    # 0x02: 释放
    # 0x03: 停止
    # 0x04: 归零
    # 0x06: 速度方式
    # 0x07: 位置方式
    # 0x15: 正弦方式
    # 0x33: 增量方式
    # 0xd: 等待
    # 0xe: 循环开始
    # 0xf: 循环结束
    # 0x77: 选择负载
    # axis:
    # 1 航向
    # 2 俯仰
    # 3 航向+俯仰
    # runType_1 航向轴的运动方式
    # 5 位置 6 速率 7 摇摆
    # runType_2 俯仰轴的运动方式
    # 5 位置 6 速率 7 摇摆
    # repeat 循环次数
    def __init__(self, type, axis=0, runType_1=0, runType_2=0, load_type=0,
                 pos_p=0, pos_v=0, pos_a=0, vel_v=0, vel_a=0,
                 swing_range=0, swing_freq=0, swing_dur=0, delay=0, repeat=0):
        self.type = type
        self.command = bytearray(10)
        self.delay = abs(delay)
        self.repeat = abs(int(repeat))
        for c in self.command:
            c = 0
        self.command[1] = type
        self.command[0] = axis
        c_p = 0
        c_v = 0
        c_a = 0
        if type == 0x07:  # 位置设置
            c_p = int(pos_p * 10000)
            c_v = int(pos_v * 2000)
            c_a = int(pos_a * 10)
            c_p = c_p if c_p >= 0 else c_p + 0x10000
            c_v = c_v if c_v >= 0 else abs(c_v)
            c_a = c_a if c_a >= 0 else abs(c_a)
            for i in range(3):
                self.command[1 + i] = (c_p & (0xff << (i * 8))) >> (i * 8)
                self.command[4 + i] = (c_v & (0xff << (i * 8))) >> (i * 8)
            for i in range(2):
                self.command[7 + i] = (c_a & (0xff << (i * 8))) >> (i * 8)
        elif type == 0x06:  # 速率设置
            c_p = int(vel_v * 10000)
            c_v = int(vel_a * 10)
            c_p = c_p if c_p >= 0 else c_p + 0x1000000
            c_v = c_v if c_v >= 0 else abs(c_v)
            for i in range(4):
                self.command[1 + i] = (c_p & (0xff << (i * 8))) >> (i * 8)
            for i in range(3):
                self.command[5 + i] = (c_v & (0xff << (i * 8))) >> (i * 8)
        elif type == 0x15:  # 摇摆设置
            c_p = int(swing_range * 10000)
            c_v = int(swing_freq * 10)
            c_p = c_p if c_p >= 0 else abs(c_p)
            c_v = c_v if c_v >= 0 else abs(c_v)
            for i in range(3):
                self.command[1 + i] = (c_p & (0xff << (i * 8))) >> (i * 8)
            for i in range(2):
                self.command[4 + i] = (c_v & (0xff << (i * 8))) >> (i * 8)
        elif type == 0x33:  # 增量设置
            c_p = int(pos_p * 10000)
            c_v = int(pos_v * 2000)
            c_a = int(pos_a * 10)
            c_p = c_p if c_p >= 0 else c_p + 0x10000
            c_v = c_v if c_v >= 0 else abs(c_v)
            c_a = c_a if c_a >= 0 else abs(c_a)
            for i in range(3):
                self.command[1 + i] = (c_p & (0xff << (i * 8))) >> (i * 8)
                self.command[4 + i] = (c_v & (0xff << (i * 8))) >> (i * 8)
            for i in range(2):
                self.command[7 + i] = (c_a & (0xff << (i * 8))) >> (i * 8)
        if type == 0x77:  # 选择负载
            self.command[1] = load_type
        if type == 0x0d:  # delay
            self.command = bytearray(b'')
        if type == 0x0e:  # 循环开始
            self.command = bytearray(b'')
        if type == 0x0f:  # 循环结束
            self.command = bytearray(b'')

# 调度器负责两个任务：
# 对转台写命令，并延时等待执行
# 定时读取转台数据，通过回调函数范围


class ztScheduler():
    def __init__(self, readCallback, finishCallback=None, portname='/dev/ttyUSB1'):
        self.callback = readCallback
        self.finishCallback = finishCallback
        self.taskList = []
        self.unrollingTaskList = []
        self.readelay = 0.001
        self.readrun = True
        self.enableCallback = False
        self.waitCond = threading.Condition()
        self.zt902e1 = zt902e1(callback=self.callback, portname=portname)
        self.readth = threading.Thread(target=self.readProcess, daemon=True)
        self.th = threading.Thread(target=self.process, daemon=True)

    def createTasks(self, oriTasks):
        # 0x55: 建立通讯
        # 0x66: 退出远控
        # 0x01: 闭合
        # 0x02: 释放
        # 0x03: 停止
        # 0x04: 归零
        # 0x06: 速度方式
        # 0x07: 位置方式
        # 0x15: 正弦方式
        # 0x33: 增量方式
        # 0xd: 等待
        # 0xe: 循环开始
        # 0xf: 循环结束
        # 0x77: 选择负载
        taskLst = []
        runtype1 = 5
        runtype2 = 5
        for t in oriTasks:
            # 开机一条龙
            if t["id"] == 0:
                task = ztTask(type=0x55)  # 建立通信
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0)  # 延时
                taskLst.append(task)
                task = ztTask(type=1)  # 闭合
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0)  # 延时
                taskLst.append(task)
                task = ztTask(type=0x04)  # 归零
                taskLst.append(task)
                task = ztTask(type=0xd, delay=100)  # 延时
                taskLst.append(task)
            # 关机一条龙(停止->闲置->断开)
            if t["id"] == 1:
                task = ztTask(type=0x03)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0)
                taskLst.append(task)
                task = ztTask(type=2)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0)
                taskLst.append(task)
                task = ztTask(type=0x66)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0)
                taskLst.append(task)

            # 位置运动模式
            if t["id"] == 2:
                task = ztTask(
                    type=7, pos_p=t["opt1"], pos_v=t["opt2"], pos_a=t["opt3"])
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0)
                taskLst.append(task)
                task = ztTask(type=0xd, delay=t["opt4"])
                taskLst.append(task)

            # 速度运动模式
            if t["id"] == 3:
                task = ztTask(type=0x06,
                              vel_v=t["opt1"], vel_a=t["opt2"])
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0)
                taskLst.append(task)
                task = ztTask(type=0xd, delay=t["opt4"])
                taskLst.append(task)

            # 正弦运动模式
            if t["id"] == 4:
                task = ztTask(
                    type=0x15, swing_range=t["opt1"], swing_freq=t["opt2"], swing_dur=t["opt3"])
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0)
                taskLst.append(task)
                task = ztTask(type=0xd, delay=t["opt3"] + 1)
                taskLst.append(task)

            # 增量运动模式
            if t["id"] == 5:
                task = ztTask(
                    type=0x33, pos_p=t["opt1"], pos_v=t["opt2"], pos_a=t["opt3"])
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0)
                taskLst.append(task)
                task = ztTask(type=0xd, delay=t["opt3"] + 1)
                taskLst.append(task)

            # 建立通信 闭合 闲置 断开通讯 停止 归零
            if t["id"] == 6:
                task = ztTask(type=0x55)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0)
                taskLst.append(task)
            if t["id"] == 7:
                task = ztTask(type=0x01)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0)
                taskLst.append(task)
            if t["id"] == 8:
                task = ztTask(type=0x02)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0)
                taskLst.append(task)
            if t["id"] == 9:
                task = ztTask(type=0x66)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0)
                taskLst.append(task)
            if t["id"] == 10:
                task = ztTask(type=0x03)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0)
                taskLst.append(task)
            if t["id"] == 11:
                task = ztTask(type=0x04)
                taskLst.append(task)
                task = ztTask(type=0x0d, delay=5.0)
                taskLst.append(task)

            # 延时
            if t["id"] == 12:
                task = ztTask(type=0x0d, delay=t["opt1"])
                taskLst.append(task)

            # 循环开始
            if t["id"] == 13:
                task = ztTask(type=0x0e, repeat=t["opt1"])
                taskLst.append(task)

            # 循环结束
            if t["id"] == 14:
                task = ztTask(type=0x0f)
                taskLst.append(task)
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
            if task.type == 0x0e:  # 循环开始
                startUnrolling = True
                repeatList = []
                repeat = task.repeat
            elif task.type == 0x0f:  # 循环结束
                startUnrolling = False
                self.unrollingTaskList.extend(repeatList * repeat)
            else:
                if startUnrolling:
                    repeatList.append(task)
                else:
                    self.unrollingTaskList.append(task)

    def run(self, readFPS=1000):
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
            if task.type in [0x0e, 0x0f]:
                continue
            self.waitCond.acquire()
            self.zt902e1.sendCommand(task.command)
            if self.enableCallback:
                self.progressCallback(
                    float(taskCount / len(self.unrollingTaskList)))
            time.sleep(0.5)
            self.waitCond.notifyAll()
            self.waitCond.release()
            # print(task.command)
        self.readrun = False
        if self.finishCallback is not None:
            self.finishCallback()


class zt902e1():
    def __init__(self, callback, portname='/dev/ttyUSB1'):
        portName = portname
        bps = 9600
        time = 0.005
        self.mutex = threading.Lock()
        self.ser = serial.Serial(port=portName, baudrate=bps, timeout=0.5)
        self.recvrun = True
        # self.ser.open()
        # self.th_recv = threading.Thread(target=self.recv, daemon=True)
        # self.th_recv.start()
        self.callback = callback
        # self.send() # 建立链接
        # self.connected = self.recv() # 接收建立连接返回信号
        self.connected = True

    def getValue(self):
        status = ztStatus()
        # 速度
        command = b'\x10\x00\x00\x00\x00\x00\x00\x00\x00\xF0'
        if self.sendCommand(command):
            self.recv(status=status)
        # 位置
        command = b'\x11\x00\x00\x00\x00\x00\x00\x00\x00\xEF'
        if self.sendCommand(command):
            self.recv(status=status)
        # callback
        self.callback(status.toDict())

    def recv(self, status=None):
        length = 8
        sum = 0
        buff = self.ser.read(length)
        buffArray = list(bytearray(buff))
        if len(buff) != length:
            return False
        # 校验
        for b in buffArray:
            sum += b
        sum %= 256
        if sum == 0:
            # if buffArray[1] == 0x55:
            #     return True
            # 速度
            if buffArray[0] == 0x10 and status is not None:
                pos = 0
                for i in range(3, 7, 1):
                    pos |= (buffArray[i] << 8 * (i - 2))
                if pos > 0x10000000:  # 负数
                    pos -= 0xffffffff
                pos *= 0.0001
                status.setAxisValue(buffArray[0], status.pos, pos)
                return True
            elif buffArray[0] == 0x11 and status is not None:
                pos = 0
                for i in range(3, 7, 1):
                    pos |= (buffArray[i] << 8 * (i - 2))
                if pos > 0x10000000:  # 负数
                    pos -= 0xffffffff
                pos *= 0.0001
                status.setAxisValue(buffArray[0], pos, status.velocity)
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
