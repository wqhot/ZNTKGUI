import paramiko
import threading


class sshCtl(threading.Thread):
    def __init__(self, command, host, username, password, port=22):
        self.command = command + '\n'
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.isRun = True
        self.ssh = None
        self.shell = None
        super(sshCtl, self).__init__(daemon=True)

    def setCommand(self, command):
        self.command = command + '\n'

    def setHost(self, host):
        self.host = host
        
    def setPort(self, port):
        self.port = port

    def setUsername(self, username):
        self.username = username

    def setPassword(self, password):
        self.password = password

    def sendCommand(self, command):
        cmd = command + '\n'
        self.shell.send(cmd)

    def run(self):
        self.ssh = paramiko.SSHClient()
        know_host = paramiko.AutoAddPolicy()
        self.ssh.set_missing_host_key_policy(know_host)

        self.ssh.connect(
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password
        )

        self.shell = self.ssh.invoke_shell()
        self.shell.settimeout(1)    
        self.shell.send(self.command)
        while self.isRun:
            try:
                recv = self.shell.recv(512).decode()
                if recv:
                    print(recv)
                else:
                    continue
            except:
                continue
        
        self.shell.send("x\n")
        self.ssh.close()


