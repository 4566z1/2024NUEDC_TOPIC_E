import vision, cv2, robot, time, chess, serial, voice
from threading import Thread

mychess = chess.Chess()
myvoice = voice.Voice("COM22", 9600)
myscreen = serial.Serial("COM3", 9600)
myrobot = robot.Robot("COM20", 9600)
# myservo = servo.Servo("COM21", 115200)

is_exit_flag = False
HUMAN_COLOR = 1  # 默认玩家为白色棋子


def vision_thread():
    """ 视觉线程 => 异步获取棋盘矩阵
    """
    global chess_board

    while not is_exit_flag:
        (chess_centers, theta) = vision.find_qipan()  # 找棋盘位置
        # print(mychess.get_angle())
        if len(chess_centers) == 9:  # 是否存在棋盘
            mychess.set_board(vision.find_qizi(chess_centers, HUMAN_COLOR))
            mychess.set_angle(theta)
        else:
            chess_board = [[0, 0, 0] for _ in range(3)]
        cv2.waitKey(1)


def select_chess(color, id, target_id, angle_bias=0):
    """挑选任意一颗棋子放到指定方格

    Args:
        color (_type_): 棋子颜色
        id (_type_): 若id为0，则自动搜索可用棋子
        target_id (_type_): 指定方格id
        angle_bias: 角度偏差
    """
    if id != 0:
        mychess.select_chess(color, id)
    else:
        id = mychess.find_chess(color)

    if color == 'white':
        myrobot.moveto_whitechess(id)
    else:
        myrobot.moveto_blackchess(id)

    myrobot.catch_chess(0)
    myrobot.moveto_board(target_id, angle_bias)
    myrobot.put_chess(5700)


def reback_chess(color, id, target_id, angle_bias=0):
    """挑选方格上的棋子放回

    Args:
        color (_type_): 棋子颜色
        id (_type_): 若id为0，则自动搜索可用空间
        target_id (_type_): 指定方格id
        angle_bias: 角度偏差
    """
    myrobot.moveto_board(target_id, angle_bias)
    myrobot.catch_chess(5700)

    if id != 0:
        mychess.reback_chess(color, id)
    else:
        pass
        # 暂未修复
        # id = mychess.find_empty(color)

    if color == 'white':
        myrobot.moveto_whitechess(id)
    else:
        myrobot.moveto_blackchess(id)

    myrobot.put_chess(0)


def check_chess():
    """修正棋盘
    """

    ret = mychess.check_chess()
    if ret[0] and ret[1]:
        print("修正位置，从f{ret[0]}移动到f{ret[1]}")
        myrobot.moveto_board(ret[0])
        myrobot.catch_chess(5700)
        myrobot.moveto_board(ret[1])
        myrobot.put_chess(5700)
        myrobot.motion_reset()
        return True
    return False


def decode_id(id):
    return int.from_bytes(id, 'little')


def task1():
    """挑选任意一颗黑棋子放到5号方格
    """
    id = decode_id(myscreen.read()) - 5
    select_chess('black', id, 5)


def task2():
    """将任意两颗黑棋子和白棋子放到指定方格
    """

    for _ in range(4):
        color = 'white'
        id = int.from_bytes(myscreen.read(), 'little')
        target_id = int.from_bytes(myscreen.read(), 'little') - 10

        if id > 5:
            id = id - 5
            color = 'black'

        select_chess(color, id, target_id)


def task3():
    """ 计算旋转角度，将任意两颗黑棋子和白棋子放到指定方格
    """

    # 舵机计算角度
    # myservo.force_disable()
    # start_angle = myservo.pos_read()
    # myscreen.read() #   读到数据后
    # end_angle = myservo.pos_read()
    # angle = start_angle - end_angle

    # 视觉读取角度
    myscreen.read()
    angle = mychess.get_angle()

    # 将任意两颗黑棋子和白棋子放到指定方格
    for _ in range(4):
        color = 'white'
        id = int.from_bytes(myscreen.read(), 'little')
        target_id = int.from_bytes(myscreen.read(), 'little') - 10

        if id > 5:
            id = id - 5
            color = 'black'

        select_chess(color, id, target_id, angle)


def task4():
    """ 进行对弈，玩家为白棋，人机先行
    """
    global HUMAN_COLOR
    HUMAN_COLOR = 1

    # 人机先行
    target_id = int.from_bytes(myscreen.read(), 'little') - 10
    select_chess('black', 0, target_id)
    myrobot.motion_reset()

    while not mychess.is_end():
        # 设置监控棋盘
        mychess.set_check_board()

        # 等待
        myscreen.read()

        # 修正人机棋子
        if not check_chess():
            chess_board = mychess.get_board()

            # 对弈
            target_id = chess.ai_turn(chess_board)

            if target_id is None:
                break

            select_chess('black', 0, target_id)
            myrobot.motion_reset()

            # 亮灯  


def task5():
    """ 进行对弈，玩家为黑棋，玩家先行
    """
    global HUMAN_COLOR
    HUMAN_COLOR = 2

    while not mychess.is_end():
        # 设置监控棋盘
        mychess.set_check_board()

        # 等待
        myscreen.read()

        # 修正人机棋子
        if not check_chess():
            chess_board = mychess.get_board()

            # 对弈
            target_id = chess.ai_turn(chess_board)

            if target_id is None:
                break

            select_chess('white', 0, target_id)
            myrobot.motion_reset()

            # 亮灯


#
#   入口函数
#
_vision_thread = None
def main():
    _vision_thread = Thread(target=vision_thread)
    _vision_thread.start()

    is_exit_flag = False
    while not is_exit_flag:
        task_id = int.from_bytes(myscreen.read(), 'little')
        if task_id == 20:
            task1()
        elif task_id == 21:
            task2()
        elif task_id == 22:
            task3()
        elif task_id == 23:
            task4()
        elif task_id == 24:
            task5()

        mychess.reset()
        myrobot.motion_reset()
        time.sleep(1)

    _vision_thread.join()

if __name__ == "__main__":
    while True:
        try:
            main()
        except:
            is_exit_flag = True
            mychess.reset()
            myrobot.motion_reset()
            if _vision_thread is not None:
                _vision_thread.join()
            

