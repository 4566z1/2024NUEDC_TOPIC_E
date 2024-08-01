import numpy as np
import serial, time

class Servo:
    def __init__(self, port, baudrate) -> None:
        self.factor = 0.09
        self.connect(port, baudrate)
        self.reset()

    def connect(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port, baudrate)

    def reset(self):
        self.pos_set(90)

    def wait(self):
        self.ser.read_until(b'#OK!\r\n')

    def write_mode(self):
        # 180度模式
        self.ser.write(b'#241PMOD3!\r\n')
        self.wait()

    def force_enable(self):
        """恢复力矩
        """
        self.ser.write(b'#241PULR!\r\n')
        self.wait()

    def force_disable(self):
        """释放力矩
        """
        self.ser.write(b'#241PULK!\r\n')
        self.wait()

    def pos_read(self):
        self.ser.write(b'#241PRAD!\r\n')
        pos = int(self.ser.readline()[5:9].decode('utf-8'))
        angle = self.factor * (pos - 500)
        return angle
    
    def pos_set(self, angle):
        if angle > 180 or angle < 0:
            return False

        pos = angle / self.factor + 500
        self.ser.write(b'#241P%04dT1000!\r\n' % (int(pos)))
        return True
