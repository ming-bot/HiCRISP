import heapq
import copy
import numpy as np

class mynode():
    def __init__(self, x, y, tar_x, tar_y):
        self.position = [x, y]
        self.cost = 0
        self.h = abs(tar_x - x) + abs(tar_y - y)
        self.parent = None
        self.last_dir = -1

    def __lt__(self, other):
        return self.cost + self.h < other.cost + other.h
    
    def __eq__(self, other):
        return self.position == other.position

class mymap():
    def __init__(self, trap_info):
        self.step = 50
        self.trap = trap_info                # obstacles info
        self.findlist = []                   # close list
        self.openlist = []                   # open list
        self.range = [1000, 4000, 500, 2500] # platform size
        self.car_r = 180                     # we model our car as a round

    def issafe(self, x, y):
        if not (x > self.range[0] and x < self.range[1] and y > self.range[2] and y < self.range[3]):
            return False
        for info in self.trap:
            distance = np.sqrt((x - info[0])**2 + (y - info[1])**2)
            obs = np.sqrt(info[2]**2 + info[3]**2)
            # if abs(x - info[0]) < 1.2 * info[2] + self.car_r and abs(y - info[1]) < 1.2 * info[3] + self.car_r:
            if not (distance > self.car_r + obs):
                return False
        return True

    def neartar(self, x, y, tar_x, tar_y):
        if abs(tar_x - x) < self.step and abs(tar_y - y) < self.step:
            return True
        return False

    def Astar(self, x, y, tar_x, tar_y):
        start_node = mynode(x, y, tar_x, tar_y)
        end_node = mynode(tar_x, tar_y, tar_x, tar_y)

        heapq.heappush(self.openlist, start_node)

        trans = [[0,self.step], [0,-self.step], [self.step,0], [-self.step,0]]
        isfind = False
        while(len(self.openlist) > 0):
            now_node = heapq.heappop(self.openlist)
            self.findlist.append(copy.copy(now_node.position))
            # 已经接近终点
            if self.neartar(now_node.position[0], now_node.position[1], tar_x, tar_y):
                isfind = True
                break
            for j in range(4):
                if self.issafe(now_node.position[0] + trans[j][0], now_node.position[1] + trans[j][1]):
                    if [now_node.position[0] + trans[j][0], now_node.position[1] + trans[j][1]] not in self.findlist:
                        newnode = mynode(now_node.position[0] + trans[j][0], now_node.position[1] + trans[j][1], tar_x, tar_y)
                        newnode.parent = copy.deepcopy(now_node)
                        newnode.last_dir = j
                        newnode.cost = newnode.parent.cost + self.step
                        if (not j == now_node.last_dir) and (not now_node.last_dir == -1):
                            newnode.cost += 2 * self.step
                        
                        if newnode not in self.openlist: # not in close list and open list
                            heapq.heappush(self.openlist, copy.deepcopy(newnode))
                        else:                            # in close list and open list
                            index = self.openlist.index(newnode)
                            if self.openlist[index].cost > newnode.cost:
                                self.openlist[index].cost = newnode.cost
                                self.openlist[index].last_dir = newnode.last_dir
                                self.openlist[index].parent = copy.deepcopy(newnode.parent)
                                heapq.heapify(self.openlist)
        if isfind:
            print('Get a new road.\n')
            road = []
            dir = -2
            if now_node == end_node:
                pass
            else:
                road.append([tar_x, tar_y])
            while now_node.parent:
                if not dir == now_node.last_dir:
                    road.append([now_node.position[0], now_node.position[1]])
                    dir = now_node.last_dir
                now_node = now_node.parent
            road.reverse()
            print("REVERSED.")
            return road
        else:
            return None


if __name__=='__main__':
    Map = mymap([])
    print(Map.Astar(2463, 1517, 1978, 2160))