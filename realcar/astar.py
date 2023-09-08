import heapq
import copy

class mynode():
    def __init__(self, x, y, tar_x, tar_y):
        self.position = [x, y]
        self.cost = 0
        self.h = abs(tar_x - x) + abs(tar_y - y)
        self.parent = None

    def __lt__(self, other):
        return self.cost + self.h < other.cost + other.h
    
    def __eq__(self, other):
        return self.position == other.position

class mymap():
    def __init__(self, trap_info):
        self.step = 0.5
        self.trap = trap_info
        self.findlist = []
        self.openlist = []
        self.range = [-7,7,-7,7]
        self.car_size = [0.3, 0.2]

    def issafe(self, x, y):
        if not (x > self.range[0] and x < self.range[1] and y > self.range[2] and y < self.range[3]):
            return False
        for info in self.trap:
            if abs(x - info[0]) < info[2] + self.car_size[0] and abs(y - info[1]) < info[3] + self.car_size[1]:
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
        self.findlist.append([x, y])

        trans = [[0,self.step], [0,-self.step], [self.step,0], [-self.step,0]]

        while(len(self.openlist) > 0):
            now_node = heapq.heappop(self.openlist)

            # 已经接近终点
            if self.neartar(now_node.position[0], now_node.position[1], tar_x, tar_y):
                break
            for j in range(4):
                if self.issafe(now_node.position[0] + trans[j][0], now_node.position[1] + trans[j][1]):
                    if [now_node.position[0] + trans[j][0], now_node.position[1] + trans[j][1]] not in self.findlist:
                        newnode = mynode(now_node.position[0] + trans[j][0], now_node.position[1] + trans[j][1], tar_x, tar_y)
                        newnode.parent = copy.deepcopy(now_node)
                        newnode.cost = newnode.parent.cost + self.step
                        self.findlist.append([newnode.position[0], newnode.position[1]])
                        heapq.heappush(self.openlist, copy.deepcopy(newnode))
        print('Get a new road.\n')
        road = []
        if now_node == end_node:
            pass
        else:
            road.append([tar_x, tar_y])
        while now_node:
            road.append([now_node.position[0], now_node.position[1]])
            now_node = now_node.parent
        road.reverse()
        return road


# if __name__=='__main__':
#     Map = mymap([3.0, 0.0, 1.0, 1.0])
#     Map.Astar(3, -1.1, 3, 3)