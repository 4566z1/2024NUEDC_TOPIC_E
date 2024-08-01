import serial, time

class Voice:
    def __init__(self, port, baudrate) -> None:
        self.connect(port, baudrate)

    def connect(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port, baudrate)

    def checksum(self, data):
        bcc = 0
        for byte in data:
            bcc ^= byte
        return bcc

    def speak(self, str):
        data = bytes(str, 'gbk')
        size = len(data) + 3
        buf = bytes([0xFD, size // 256, size % 256, 0x01, 0x01]) + bytes(str, 'gbk')
        content = buf + bytes([self.checksum(buf)])
        self.ser.write(content)
        time.sleep(0.7)
