import numpy as np
import serial, math
import time

HEIGHT_REFER = 7000  # 参考高度


class Robot:

    def __init__(self, port, baudrate):
        self.connect(port, baudrate)
        self.motion_reset()
        # self.random()

    def wait(self):
        self.ser.read_until(b"JS")

    def connect(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port, baudrate)
        self.ser.read_until(b'Start!Welcome to FLYBOT!\r\n')

    def attract(self, status: bool):
        """ 控制电磁铁吸引
        """
        if status:
            self.ser.write(b'D1')
        else:
            self.ser.write(b'D2')

    def motion_vaild(self, val) -> bool:
        if val < 18000 and val >= 0:
            return True
        else:
            return False

    def motion_x(self, x : int):
        if not self.motion_vaild(x):
            return False

        comm = f'x{x}'.encode('utf-8')
        self.ser.write(comm)
        return True

    def motion_y(self, y: int):
        if not self.motion_vaild(y):
            return False

        comm = f'y{y}'.encode('utf-8')
        self.ser.write(comm)
        return True

    def motion_z(self, z : int):
        if not self.motion_vaild(z):
            return False

        comm = f'z{z}'.encode('utf-8')
        self.ser.write(comm)
        return True

    def motion_async(self, x, y, z):
        """异步动作，同时进行

        Args:
            x (_type_): _description_
            y (_type_): _description_
            z (_type_): _description_
        """
        if x:
            self.motion_x(x)
        if y:
            self.motion_y(y)
        if z:
            self.motion_z(z)

    def motion_sync(self, x, y, z):
        """同步动作，完成一个再完成下一个

        Args:
            x (_type_): _description_
            y (_type_): _description_
            z (_type_): _description_
        """
        if self.motion_vaild(z):
            self.motion_z(z)
            self.wait()

        if self.motion_vaild(y):
            self.motion_y(y)
            self.wait()

        if self.motion_vaild(x):
            self.motion_x(x)
            self.wait()

    def motion_reset(self):
        self.motion_z(HEIGHT_REFER)
        self.wait()

        self.motion_x(0)
        self.motion_y(0)
        self.wait()

    def moveto_blackchess(self, id):
        """移动到指定黑棋位置点的参考高度

        Args:
            id (_type_): 1<= id <= 5
        """
        self.motion_z(HEIGHT_REFER)
        self.wait()

        x = 0
        y = 3000 * (id - 1)
        self.motion_x(x)
        self.motion_y(y)
        self.wait()

    def moveto_whitechess(self, id):
        """移动到指定白棋位置点的参考高度

        Args:
            id (_type_): 1<= id <= 5
        """
        self.motion_z(HEIGHT_REFER)
        self.wait()

        # 误差修正
        bias = 200
        x = 17000
        y = 3000 * (id - 1) - bias
        if y < 0:
            y = 0

        self.motion_x(x)
        self.motion_y(y)
        self.wait()

    def catch_chess(self, height):
        """抓取棋子并拉回到 参考高度
        """
        self.attract(True)
        self.wait()

        self.motion_z(height)
        self.wait()

        self.motion_z(HEIGHT_REFER)
        self.wait()

    def put_chess(self, height):
        """放到指定高度

        Args:
            height (_type_): 指定高度
        """

        self.motion_z(height)
        self.wait()

        time.sleep(0.5)

        self.attract(False)
        self.wait()

        self.motion_z(HEIGHT_REFER)
        self.wait()

    def moveto_board(self, id, angle_bias = 0):
        """放到指定棋盘方格上参考高度

        Args:
            id (_type_): 棋盘方格ID
            angle_bias (_type_): 偏移的角度
        """

        self.motion_z(HEIGHT_REFER)
        self.wait()

        d = 3200  # 方格中心点间距
        x0 = 5400  # 一号方格位置 X
        y0 = 9100  # 一号方格位置 Y

        x = x0 + (int((id - 1) % 3)) * d
        y = y0 - (int((id - 1) / 3)) * d

        # 旋转矩阵变换
        if angle_bias:
            # 计算5号方格的中心坐标
            centx = x0 + (int((5 - 1) % 3)) * d
            centy = y0 - (int((5 - 1) / 3)) * d

            # 原点旋转矩阵
            radian = np.radians(angle_bias)
            rotate_matrix = np.array([[np.cos(radian), np.sin(radian), 0],
                                      [-np.sin(radian),np.cos(radian), 0], 
                                      [0, 0, 1]])
            # 平移矩阵
            first = np.array([[1, 0, centx],
                              [0, 1, centy],
                              [0, 0, 1]])
            end = np.array([[1, 0, -centx],
                              [0, 1, -centy],
                              [0, 0, 1]])
            # 任一点旋转矩阵
            M = np.dot(np.dot(first, rotate_matrix), end)

            # 坐标整定
            output = np.dot(M, np.array([[x],[y],[1]]))
            x = math.ceil(output[0][0])
            y = math.ceil(output[1][0])

        self.motion_x(x)
        self.motion_y(y)
        self.wait()

    def random(self):
        self.motion_sync(HEIGHT_REFER, 16000, 16000)
        self.motion_reset()

    def valid(self):
        """校准棋盘
        """

        self.moveto_board(1, 0)
        self.moveto_board(9, 0)
