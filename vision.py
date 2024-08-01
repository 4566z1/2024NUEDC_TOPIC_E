import numpy as np
import chess
import cv2

capture = cv2.VideoCapture(1)
capture.set(cv2.CAP_PROP_AUTO_WB,0)

#
#   白色为 1，黑色为 2
#   玩家为 1，人机为 -1
#
def find_qizi(chess_centers, human_color):
    ret, img = capture.read()
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)

    chess_mat = [[0, 0, 0] for _ in range(3)]

    for i in range(9):
        x = int(chess_centers[i][0])
        y = int(chess_centers[i][1])
        roi = hsv[y - 10:y + 10, x - 10:x + 10]

        # 检测黑白棋子
        if len(roi):
            s = np.mean(roi[:, :, 1])
            v = np.mean(roi[:, :, 2])
            if 0 < v < 115:
                if human_color == 2:
                    chess_mat[int(i / 3)][int(i % 3)] = chess.HUMAN
                else:
                    chess_mat[int(i / 3)][int(i % 3)] = chess.COMP
            elif 0 < s < 50 and 114 < v < 256:
                if human_color == 1:
                    chess_mat[int(i / 3)][int(i % 3)] = chess.HUMAN
                else:
                    chess_mat[int(i / 3)][int(i % 3)] = chess.COMP

    return chess_mat


def find_qipan():
    ret, img = capture.read()
    rect = []
    theta = 0

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0.8, 0.8)
    edged = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        # 筛选出最大的轮廓
        largest_contour = max(contours, key=cv2.contourArea)

        theta = cv2.minAreaRect(largest_contour)[2]

        # [x, y, w, h] = cv2.boundingRect(largest_contour)
        # cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # print(angle)

        # 近似多边形
        epsilon = 0.01 * cv2.arcLength(largest_contour, True)
        approx = cv2.approxPolyDP(largest_contour, epsilon, True)

        # 如果找到的是一个四边形
        if len(approx) == 4:
            corners = approx.reshape((4, 2))

            # 绘制顶点和轮廓
            for corner in corners:
                cv2.circle(img, tuple(corner), 4, (0, 255, 0), -1)

            # 洪泛填充外部
            # img_copy = img.copy()
            # mask = np.zeros([img_copy.shape[0] + 5, img_copy.shape[1] + 5, 1],
            #                 np.uint8)
            # cv2.floodFill(img, None, (corners[0][0] - 5, corners[0][1] - 5),
            #               (255, 100, 100), (20, 20, 20), (50, 50, 50),
            #               cv2.FLOODFILL_FIXED_RANGE)

            # 上面出来的结果已经是 点从左上逆时针，所以跳过找顶点
            tl = corners[0]
            bl = corners[1]
            br = corners[2]
            tr = corners[3]

            # 计算3x3格子的交叉点
            cross_points = []
            for i in range(4):
                for j in range(4):
                    # 线性插值计算交叉点
                    cross_x = int((tl[0] * (3 - i) + tr[0] * i) * (3 - j) / 9 +
                                  (bl[0] * (3 - i) + br[0] * i) * j / 9)
                    cross_y = int((tl[1] * (3 - i) + tr[1] * i) * (3 - j) / 9 +
                                  (bl[1] * (3 - i) + br[1] * i) * j / 9)
                    cross_points.append((cross_x, cross_y))
                    cv2.circle(img, (cross_x, cross_y), 3, (0, 255, 0), -1)

            centers = []
            for i in range(3):
                for j in range(3):
                    center_x = int((cross_points[i * 4 + j][0] +
                                    cross_points[i * 4 + j + 1][0] +
                                    cross_points[(i + 1) * 4 + j][0] +
                                    cross_points[(i + 1) * 4 + j + 1][0]) / 4)
                    center_y = int((cross_points[i * 4 + j][1] +
                                    cross_points[i * 4 + j + 1][1] +
                                    cross_points[(i + 1) * 4 + j][1] +
                                    cross_points[(i + 1) * 4 + j + 1][1]) / 4)
                    centers.append((center_x, center_y))
                    cv2.circle(img, (center_x, center_y), 2, (0, 255, 0), -1)

            # 对找到的中心点进行编号, y + x 最大就是右下角，最小就是左上角， y-x 最大就是左下角，y-x 最小就是右上角，其它几个点根据在旁边两个点中间判断
            if len(centers) == 9:
                centers = np.array(centers)
                rect = np.zeros((9, 2), dtype="float32")
                s = centers.sum(axis=1)
                idx_0 = np.argmin(s)
                idx_8 = np.argmax(s)
                diff = np.diff(centers, axis=1)
                idx_2 = np.argmin(diff)
                idx_6 = np.argmax(diff)
                rect[0] = centers[idx_0]
                rect[2] = centers[idx_2]
                rect[6] = centers[idx_6]
                rect[8] = centers[idx_8]
                #   其它点
                calc_center = (rect[0] + rect[2] + rect[6] + rect[8]) / 4
                mask = np.zeros(centers.shape[0], dtype=bool)
                idxes = [1, 3, 4, 5, 7]
                mask[idxes] = True
                others = centers[mask]
                idx_l = others[:, 0].argmin()
                idx_r = others[:, 0].argmax()
                idx_t = others[:, 1].argmin()
                idx_b = others[:, 1].argmax()
                found = np.array([idx_l, idx_r, idx_t, idx_b])
                mask = np.isin(range(len(others)), found, invert=False)
                idx_c = np.where(mask == False)[0]
                if len(idx_c) == 1:
                    rect[1] = others[idx_t]
                    rect[3] = others[idx_l]
                    rect[4] = others[idx_c]
                    rect[5] = others[idx_r]
                    rect[7] = others[idx_b]
                    # 写编号
                    for i in range(9):
                        cv2.putText(img,
                                    f"{i + 1}",
                                    (int(rect[i][0]), int(rect[i][1])),
                                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                    color=(0, 0, 255),
                                    fontScale=2)
                else:
                    # 大于 45度的情况
                    # print("> 45 degree")
                    pass
    cv2.imshow("FindQiPan", img)
    return (rect, theta)