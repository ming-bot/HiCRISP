#使用 python 连接 ODBC 远程数据库读写 demo
# connect to 192.168.139.18
# read "robot_positions.robot_pos_cam_all"
# write in "robot_commands.commands_all"

import numpy as np
import pandas as pd
import pymysql #需要预加装pip install PyMySQL
from sqlalchemy import create_engine
import math
import datetime
import time

# 平台坐标系目标向量转化为机器人坐标系上的位置向量
# Input: thetaRobo - 机器人朝向角度 vectorW - 平台坐标系目标向量 
# Output: robotX, robotY - 机器人坐标系位置向量
def coordinateTrans(thetaRobo, vectorW):
    thetaRoboX = thetaRobo
    thetaRoboY = thetaRoboX + 90
    # 机器人 x,y 轴的单位向量
    vectorX = [np.cos(thetaRoboX / 180 * np.pi), np.sin(thetaRoboX / 180 * np.pi)]    
    vectorY = [np.cos(thetaRoboY / 180 * np.pi), np.sin(thetaRoboY / 180 * np.pi)]
    robotX = np.dot(vectorW, vectorX)	# dot(x,y)点乘
    robotY = np.dot(vectorW, vectorY)
    return robotX, robotY

# @zxc 2021.11.12
# 控制速度
# 速度绝对值小于50的时候输出成0
# 绝对值大于有效值的时候限制上下限
# robotVel_max=500
# robotVel_min=120
def constrain_vel(vel, robotVel_min=120, robotVel_max=500):
    if abs(vel) < 0:        #50
        vel = 0
    elif vel > 0:
        vel = min(robotVel_max, vel)
        vel = max(robotVel_min, vel)
    else:
        vel = max(-robotVel_max, vel)
        vel = min(-robotVel_min, vel)
    return vel

class FINS_Car():
    def __init__(self):
        ## Initialization
        # 机器人总数及 ID 设定
        self.robotNum = 1       # 机器人总数
        self.robotID = 10        # robotID是0，机器人的编号是1
        ### dataWant 中填写需要机器人运动到的坐标（Pos_x, Pos_y, Theta)
        # Pos_x \in [40,4700]
        # Pos_y \in [285,2768]
        # Theta \in [0,360]
        # x, y 不要过于靠近边界否则摄像头可能没法读取数据
        self.data_target_position = np.zeros((1, 45))
        self.data_real_position = np.zeros((1, 45))
        ### robotVelOmega 中填写机器人的控制指令（Vel_x, Vel_y, Omega）
        # 提示：在控制指令中，theta 优先级高于 x,y
        # Vel_x, Vel_y, Omega \in [-1280, 1280]
        # Vel_x, Vel_y 设成 150 就可以动起来，一般 300 或 400 就可以动得挺快了
        self.data_robot_VelOmega = np.zeros((1, 46))
        #链接服务器
        self.connA = pymysql.connect(host='192.168.139.18',user='ControlCommand',password='Erleng921010',db='robot_positions',autocommit=1) #ODBC数据源名称,SQL Server的用户名和密码
        self.connB = pymysql.connect(host='192.168.139.18',user='ControlCommand',password='Erleng921010',db='robot_commands',autocommit=1) #ODBC数据源名称,SQL Server的用户名和密码
        self.curA = self.connA.cursor()
        self.curB = self.connB.cursor()
        # Fins_car information
        # self.car_size = np.array([300, 300])
        self.car_r = 180
        self.car_pose = np.array([0, 0, 0])
        self.car_vel = np.array([0, 0, 0])
        # traps information
        self.trap_airtag = [0, 4, 5, 7]
        self.trap = []
        self.get_init_traps()
        print(self.trap)
        self.detect_traps = []
        
    def get_init_traps(self):
        self.curA.execute('select * from robot_pos_cam_all_long order by time desc limit 1')
        data = list(self.curA.fetchall()[0])
        self.data_real_position = np.array(data[1:])
        for index in self.trap_airtag:
            self.trap.append(self.data_real_position[3 * index : 3 * index + 2].tolist() + [200, 200])

    def Update(self):
        self.curA.execute('select * from robot_pos_cam_all_long order by time desc limit 1')
        data = list(self.curA.fetchall()[0])
        # print(data)
        # data = sorted(data ,key=lambda x: x[0], reverse=True)
        # data = data[0]
        # print(data[0])
        self.data_real_position = np.array(data[1:])
        self.car_pose = self.data_real_position[3 * self.robotID : 3 * self.robotID + 3]
    
    def close(self):
        self.connA.close()
        self.connB.close()
        self.curA.close()
        self.curB.close()

    def add_traps(self, position, halfsize):
        self.trap.append([position[0], position[1], halfsize[0], halfsize[1]])
    
    def ifSafe(self):
        # dt = 1
        # for i in range(len(self.trap)):
        #     x_error = abs(self.trap[i][0] - self.car_pose[0] - self.car_vel[0] * dt)
        #     y_error = abs(self.trap[i][1] - self.car_pose[1] - self.car_vel[1] * dt)
        #     if x_error < self.trap[i][2] + self.car_size[0] / 2 and y_error < self.trap[i][3] + self.car_size[1] / 2:
        #         return False
        # return True
        expansion = 1.5
        for i in range(len(self.trap)):
            d = np.sqrt((self.trap[i][0] - self.car_pose[0])**2 + (self.trap[i][1] - self.car_pose[1])**2)
            a2br = expansion * np.sqrt(self.trap[i][2]**2 + self.trap[i][3]**2) + expansion * self.car_r
            if not (d > a2br):
                return False, i
        return True, -1
        
    def Detect_traps(self):
        index = []
        min_distance = 222
        for i in range(len(self.trap)):
            if np.sqrt((self.trap[i][0] - self.car_pose[0])**2 + (self.trap[i][1] - self.car_pose[1])**2) < min_distance:
                index.append(i)
        return index

    def ifClose(self, tar:list):
        self.Update()
        difference = np.sqrt((self.car_pose[0] - tar[0])**2 + (self.car_pose[1] - tar[1])**2)
        print('机器人距离目标点距离：{}.\n'.format(difference))
        if difference > 50:
            return False
        else:
            return True
    
    def set_velocity_indatabase(self):
        self.data_robot_VelOmega[:, 3 * self.robotID + 1: 3 * self.robotID + 4] = self.car_vel[:]
        # 写入数据库
        self.curB.execute('select * from commands_all')
        list_data = self.data_robot_VelOmega.tolist()

        list_data[0][0] = datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S.%f')[:-3] + "000"
        # print(list_data[0][0][:-3]+"000")
        writer = pd.DataFrame(list(list_data), columns=[x[0] for x in self.curB.description])
        conn = create_engine('mysql+pymysql://ControlCommand:Erleng921010@192.168.139.18:3306/robot_commands')
        writer.to_sql("commands_all", con=conn, index=False, if_exists='append')
        time.sleep(0.1)

    def compute_vel(self, tar:list):
        # 计算机器人在 x,y 轴上的速度
        # Input: dataCameraProcessed - 摄像头捕捉的机器人位置 robotID - 机器人编号 dataWant - 目标位置
        # Output: [robotVelX, robotVelY] - 机器人在 x,y 轴上的速度
        K = 0.8
        # 目标点在机器人坐标系上的 x,y 向量
        thetaRobo = self.car_pose[2]
        if self.car_pose[0] == 0 and self.car_pose[1] == 0:
            robotVelX = 0
            robotVelY = 0
            robotOmega = 0
        else:
            vectorW = tar[:2] - self.car_pose[:2]
            robotX, robotY = coordinateTrans(thetaRobo, vectorW)
            print(robotX, robotY)
            robotOmega = 0
            ## 设置速度
            robotVelX = constrain_vel(robotX * K, 0, 400)
            robotVelY = constrain_vel(robotY * K, 0, 400)
            robotVelX = round(robotVelX, 3)
            robotVelY = round(robotVelY, 3)
        self.car_vel = np.array([robotVelX, robotVelY, robotOmega])
        print("Car information : ", self.car_pose, self.car_vel)
        print("Target pose : ", tar[:])
    
    def move_to_position(self, pose:list):
        begin = time.time()
        while True:
            if time.time() - begin > 180:
                self.car_vel = np.array([0,0,0])
                self.set_velocity_indatabase()
                return False

            self.Update()
            # not safe(close to traps)
            flag, ind = self.ifSafe()
            if not flag:
                if self.trap[ind] not in self.detect_traps:
                    self.detect_traps.append(self.trap[ind])
                    self.car_vel = np.array([0,0,0])
                    self.set_velocity_indatabase()
                    return False
                    
            # close to target
            if self.ifClose(pose):
                self.car_vel = np.array([0,0,0])
                self.set_velocity_indatabase()
                return True
            # still move
            else:
                self.compute_vel(pose)
                self.set_velocity_indatabase()
    
    def move_dir_position(self, pose:list):
        begin = time.time()
        while True:
            if time.time() - begin > 180:
                self.car_vel = np.array([0,0,0])
                self.set_velocity_indatabase()
                return False

            self.Update()
            # close to target
            if self.ifClose(pose):
                self.car_vel = np.array([0,0,0])
                self.set_velocity_indatabase()
                return True
            # still move
            else:
                self.compute_vel(pose)
                self.set_velocity_indatabase()
                time.sleep(0.05)

if __name__=='__main__':
    fins = FINS_Car()
    for i in range(10):
        fins.Update()
        print(fins.car_pose)
#    fins.compute_vel([2500, 1000])
    fins.close()