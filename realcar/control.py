import rospy
from geometry_msgs.msg import Twist, Pose
from gazebo_msgs.msg import ModelStates
import time
import copy

WIDTH = 0.2
LENGTH = 0.3

class mycar():
    def __init__(self):
        self.car_size = [LENGTH, WIDTH]
        self.car_pose = Pose()
        self.car_vel = Twist()
        rospy.init_node("mycar_control")
        # self.pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        self.pub = rospy.Publisher("/big_cmd_vel", Twist, queue_size=10)
        self.set_car_vel = Twist()

        self.trap = [[3.0, 0.0, 1.0, 1.0],[-0.100672, -1.659490, 0.5, 0.5],[-1.349260, 0.870802, 0.5, 0.3],[0.563355, 2.240700, 0.5, 0.5]]
        self.trapcabinet = [[-0.100672, -1.659490, 1.0, 1.0]]
        self.traptable = [[-1.349260, 0.870802, 1.0, 1.0]]
        self.trapcoffeetable = [[0.563355, 2.240700, 1.0, 1.0]]

    def locate_car(self):
        models_states = rospy.wait_for_message('/gazebo/model_states', ModelStates, timeout=None)
        # index = models_states.name.index('nexus_4wd_mecanum')
        index = models_states.name.index('smc_1')
        self.car_pose = models_states.pose[index]
        self.car_vel = models_states.twist[index]

    def add_traps(self, position, halfsize):
        self.trap.append([position[0], position[1], halfsize[0], halfsize[1]])
    
    def isSafe(self):
        dt = 1
        for i in range(len(self.trap)):
            x_error = abs(self.trap[i][0] - self.car_pose.position.x - self.car_vel.linear.x * dt)
            y_error = abs(self.trap[i][1] - self.car_pose.position.y - self.car_vel.linear.y * dt)
            if x_error < self.trap[i][2] + self.car_size[0] / 2 and y_error < self.trap[i][3] + self.car_size[1] / 2:
                return False
        return True

    def move_to_position(self, pose):
        k_p = 1.0
        rate = rospy.Rate(10)
        while True:
            self.locate_car()
            if not self.isSafe():
                self.set_car_vel.linear.x = 0
                self.set_car_vel.linear.y = 0
                self.pub.publish(self.set_car_vel)
                return False
            x_error = (pose.position.x - self.car_pose.position.x)
            if abs(x_error) < 0.1:
                break
            else:
                x_vel = k_p * x_error
                self.set_car_vel.linear.x = x_vel
                self.pub.publish(self.set_car_vel)
                rate.sleep()
        time.sleep(1)
        while True:
            self.locate_car()
            if not self.isSafe():
                self.set_car_vel.linear.x = 0
                self.set_car_vel.linear.y = 0
                self.pub.publish(self.set_car_vel)
                return False
            x_error = (pose.position.x - self.car_pose.position.x)
            y_error = (pose.position.y - self.car_pose.position.y)
            if abs(y_error) < 0.1 and abs(x_error) < 0.1:
                break
            else:
                y_vel = k_p * y_error
                x_vel = k_p * x_error
                self.set_car_vel.linear.y = y_vel
                self.set_car_vel.linear.x = x_vel
                self.pub.publish(self.set_car_vel)
                rate.sleep()
        
        return True
    
    def move_dir(self, pose):
        k_p = 1.0
        rate = rospy.Rate(10)
        while True:
            self.locate_car()
            x_error = (pose.position.x - self.car_pose.position.x)
            if abs(x_error) < 0.1:
                break
            else:
                x_vel = k_p * x_error
                self.set_car_vel.linear.x = x_vel
                self.pub.publish(self.set_car_vel)
                rate.sleep()
        time.sleep(1)
        while True:
            self.locate_car()
            x_error = (pose.position.x - self.car_pose.position.x)
            y_error = (pose.position.y - self.car_pose.position.y)
            if abs(y_error) < 0.1 and abs(x_error) < 0.1:
                break
            else:
                y_vel = k_p * y_error
                x_vel = k_p * x_error
                self.set_car_vel.linear.y = y_vel
                self.set_car_vel.linear.x = x_vel
                self.pub.publish(self.set_car_vel)
                rate.sleep()
        
        return True


# if __name__=='__main__':
#     Mycar = mycar()
#     tar = Pose()
#     tar.position.x = 5
#     tar.position.y = 5
#     Mycar.move_to_position(tar)