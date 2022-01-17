#! /usr/bin/env python3
# coding:utf-8

# 文字冒险-roguelike
import random
import pickle
from collections import deque

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class TerraRogue:
    def __init__(self, init = False) -> None:
        """
        泰拉文字冒险-但求至简+极乐！
        在神奇的地方，遇上各种各样的人，最后离开地图

        """
        self.mapsize = (8,8) # 横宽 竖长 矩阵n*m
        self.monster_num = 4
        self.hpSet = 8# 血量
        self.scoreInit = 0 # 得分
        self.pos = [1,1] # 起始位置
        # self.monsterPos = [] # 保存的点
        if init:
            self.map_, self.monsterPos = [["_"  for _ in range(self.mapsize[1])] for _ in range(self.mapsize[0])] , []
        else:
            self.map_, self.monsterPos = pickle.load(open("./botqq/database/adventureMap.pkl", "rb"))
            # print(self.map_, self.monsterPos)
        # print(self.map_)
        pass

    def __wallInit(self):
        for i in range(self.mapsize[0]):
            self.map_[i][0] = "#"
            self.map_[i][self.mapsize[1]-1] = "#"
        for j in range(self.mapsize[1]):
            self.map_[0][j] = "#"
            self.map_[self.mapsize[0]-1][j] = "#"
        # print(self.map_)
    


    def __cutMap(self, size_tuple):
        """随机切割墙体
        size_tuple: (横起点，横终点，竖起点，竖终点)
        """
        if (size_tuple[1] - size_tuple[0]<5) or (size_tuple[3] - size_tuple[2]<5): 
            # print('[INFO]分割完毕')
            return

        cut_positionRange_x = (size_tuple[0]+2, size_tuple[1]-3)
        cut_positionRange_y = (size_tuple[2]+2, size_tuple[3]-3)
        
        cut_pos_x = random.randint(cut_positionRange_x[0],cut_positionRange_x[1])
        cut_pos_y = random.randint(cut_positionRange_y[0],cut_positionRange_y[1])
        
        # print(cut_pos_x,cut_pos_y)

        # 建设墙体
        for i in range(size_tuple[0]+1,size_tuple[1]-2):
            # print('循环',i)
            # print(cut_pos_y)
            self.map_[i][cut_pos_y] = "#"
        for j in range(size_tuple[2]+1,size_tuple[3]-2):
            # print('循环2',j)
            # print(cut_pos_x)
            self.map_[cut_pos_x][j] = "#"

        # 开门的格子
        noDoorDirection = random.sample([0,1,2,3],3) # 0123上下左右
        up_wall = 0; below_wall = 0; left_wall = 0; right_wall = 0
        if 0 in noDoorDirection:
            up_wall = (cut_pos_x, random.randint(size_tuple[2]+1, cut_pos_y-1))
            self.map_[up_wall[0]][up_wall[1]] = "_"
        if 1 in noDoorDirection:
            below_wall = (cut_pos_x, random.randint(cut_pos_y+1, size_tuple[3]-2))
            self.map_[below_wall[0]][below_wall[1]] = "_"
        if 2 in noDoorDirection:
            left_wall = (random.randint(size_tuple[0]+1, cut_pos_x-1), cut_pos_y)
            self.map_[left_wall[0]][left_wall[1]] = "_"
        if 3 in noDoorDirection:
            right_wall = (random.randint(cut_pos_x+1, size_tuple[1]-2), cut_pos_y)
            self.map_[right_wall[0]][right_wall[1]] = "_"
        
        # print(left_wall, right_wall)

        # 四个新的格子size
        leftup_size = (
            size_tuple[0], cut_pos_x, 
            size_tuple[2], cut_pos_y
        )
        rightup_size = (
            cut_pos_x, size_tuple[1], 
            size_tuple[2], cut_pos_y
        )
        leftbelow_size = (
            size_tuple[0], cut_pos_x, 
            cut_pos_y, size_tuple[3]
        )
        rightbelow_size = (
            cut_pos_x, size_tuple[1], 
            cut_pos_y, size_tuple[3]
        )

        # print(up_wall,below_wall,left_wall,right_wall)
        newWallList = [leftup_size, rightup_size, leftbelow_size, rightbelow_size]

        while len(newWallList) > 0:
            tempsize = newWallList.pop(0)
            self.__cutMap(tempsize)


    def __entranceExitSet(self):
        """mapCreate
        设置入口E与出口X
        """
        self.map_[1][1] = "E"
        self.map_[self.mapsize[0]-2][self.mapsize[1]-2] = "X"
        return

    def __monsterSet(self, monster_num = 0):
        """mapCreate
        设置怪物M
        """
        if monster_num == 0:
            
            monster_num = random.randint(4,int(sum(self.mapsize)/2))

        while monster_num > 0:
            mon_x = random.randint(1,self.mapsize[0]-2)
            mon_y = random.randint(1,self.mapsize[1]-2)
            if (mon_x == 1 and mon_y == 1) or (mon_x == self.mapsize[0]-2 and mon_y == self.mapsize[1]-2):
                # 不可以在e与x处
                continue
            else:
                mon_list_already = [str(i) for i in range(1,self.monster_num+1)]
                mon_list_already.append("#")
                # print(mon_list_already)
                if self.map_[mon_x][mon_y] in mon_list_already:
                    continue
                else:
                    self.map_[mon_x][mon_y] = str(monster_num)
                    self.monsterPos.append((mon_x,mon_y)) # 将当前地图存入
                    monster_num -= 1


    def mapCreate(self):
        self.__wallInit()
        self.__cutMap((0,self.mapsize[0],0,self.mapsize[1]))
        self.__entranceExitSet()
        self.__monsterSet(self.monster_num)
        pickle.dump((self.map_, self.monsterPos), open("./botqq/database/adventureMap.pkl", "wb"))
        # print(self.map_)


    def showMap(self):
        temp = []
        for i in range(len(self.map_)):
            temp.append(''.join(x for x in self.map_[i]))
        out_text = '\n'.join(x for x in temp)
        print(out_text)
        return out_text


    def __monsterBehave(self, intk):

        behave = random.randint(0,1)
        if behave == 0:
            self.hpSet += 10
            self.scoreInit += 3
            # 加血
            return (f'于节点{intk}，得分3，加血10')
            pass
        elif behave == 1:
            # 得分
            
            self.scoreInit += 10
            return(f'于节点{intk}，得分10')
            pass


 
    def __bfs(self, begin, end):
        """
        计算迷宫最短路距离"""
        n, m = self.mapsize[0]-1, self.mapsize[1]-1

        dist = self.map_
        # pre = [[None for _ in range(m)] for _ in range(n)]   # 当前点的上一个点,用于输出路径轨迹
    
        dx = [1, 0, -1, 0] # 四个方位
        dy = [0, 1, 0, -1]
        sx, sy = begin[0], begin[1]
        gx, gy = end[0], end[1]
    
        dist[sx][sy] = 0
        queue = deque()
        queue.append(begin)
        while queue:
            curr = queue.popleft()
            find = False
            for i in range(4):
                # 回溯算法，走一个方向，最后再折回来走其他方向
                nx, ny = curr[0] + dx[i], curr[1] + dy[i]
                # print(nx, ny)
                if 0<=nx and nx<n and 0<=ny and ny<m and self.map_[nx][ny] != '#' and self.map_[nx][ny] != 'E':
                    dist[nx][ny] = dist[curr[0]][curr[1]] + 1
                    # pre[nx][ny] = curr
                    queue.append((nx, ny))
                    if nx == gx and ny == gy:
                        find = True
                        break
            if find:
                break
        # print('最短路径的长度：')
        # print(dist[gx][gy])
        return dist[gx][gy]

    
 

    def answerSheet(self, input_char = "1234"):
        """
        冒险者输入1234字符串，转化为路径、距离、得分"""
        k = 0
        out_text_list = []
        road_list = []
        
        road_list.append((1,1))

        pos_list = list(input_char)
        for item in pos_list:
            road_list.append(self.monsterPos[self.monster_num - int(item)])
            # road_list.extend()
        
        road_list.append((self.mapsize[0]-2,self.mapsize[1]-2))
        while k<self.monster_num:
            # 没到头的时候，则循环开始
            tempdistance = self.__bfs(road_list[k],road_list[k+1])
            out_text_list.append(f'来到节点{pos_list[k]}，失血{tempdistance}' + f'\t当前得分{self.scoreInit},生命值{self.hpSet}')
            self.hpSet -= tempdistance
            if self.hpSet <= 0: 
                out_text_list.append('你挂了')
                return out_text_list
            text_temp = self.__monsterBehave(self.monster_num-k)
            out_text_list.append(text_temp)
            k += 1
        out_text_list.append('最终的得分是：' + str(self.scoreInit) + '\n最终的生命值为：' + str(self.hpSet))
        # print(out_text_list)
        return '\n'.join(x for x in out_text_list)



if __name__ == '__main__':
    # test = TerraRogue(True)
    # test.mapCreate()
    # test.showMap()


    test = TerraRogue()
    print(test.answerSheet('4123'))

