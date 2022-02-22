'''
Author: KOneLane
Date: 2022-02-21 21:10:45
LastEditors: KOneLane
LastEditTime: 2022-02-22 16:20:34
Description: 
version: V
'''
import datetime
import os
import sqlite3
import urllib.request  # 下载图片

import cv2  # 图像合成
from PIL import Image


class TwoTwoOrder:
    """
    根据群里的报名情况，拼一桌22
    配置时需先运行本文件databaseInit建表
    """
    
    def __init__(self, input_text_dict) -> None:
        self.filename = './botqq/database/' # 数据库位置
        self.cardTable = {
            'table_no':0,
            'member_length':2,
            'creator': str(input_text_dict['id']),
            'group_number': str(input_text_dict['group_id']),
            'member':'591016144|',
            'wait_status':1,
            'create_time':datetime.datetime.now(),
            
        } # 用于保存报名信息
        self.TableHeader = ['table_no', 'member_length', 'creator', 'group_number', 'member', 'wait_status', 'create_time'] # 读取时使用

        self.input_text = input_text_dict['text_split'] # 用于保存各个输入参数
        self.input_text_dict = input_text_dict
        self.wait_status = 1
        self.creator = str(self.input_text_dict['id']) # 默认当前消息的creator是消息本人
        self.table_no = 0
        pass


    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return (con,cur)


    def __checkMember(self):
        """将字符串类型的member转化为list"""
        member_list = self.cardTable['member'].split('|')[:-1]
        return member_list


    def __buildTable(self):
        """
        新建牌桌 #22 等
        目前仅支持4人车
        """
        # 检查是否已建立正在等待成员的牌桌
        if not self.__getTableMessage(self.creator):

            # 建立dict
            self.cardTable['creator'] = str(self.input_text_dict['id'])
            self.creator = self.cardTable['creator'] # 更新creator信息

            self.cardTable['group_number'] = self.input_text_dict['group_id']
            self.cardTable['member_length'] = 1
            self.cardTable['member'] = str(self.input_text_dict['id']) + '|'
            # 将信息保存至数据库
            self.wait_status = 1 # 查询筛选用的
            self.__dataSave(new=True)
            # 返回路径
            return self.__imgTable()
        else:
            print('已有自己的牌桌')
            print(self.cardTable)
            return 


    def __shutdownTable(self):
        """ 
        关闭牌桌 #22 鸽
        """
        if self.__getTableMessage(self.creator):
            # 将牌桌情况存储至数据库
            try:
                self.cardTable['wait_status'] = 0
                self.__dataSave()
                print('牌桌信息已更新')
            except:
                print('删除失败')

            # 删除图片
            for img_id in range(4):
                remove_path1 = f'./botqq/database/qlogo/{self.creator}_{img_id}_c.png'
                remove_path2 = f'./botqq/database/qlogo/{self.creator}_{img_id}.png'
                try:
                    os.remove(remove_path1)# 删除图片
                    os.remove(remove_path2)# 删除图片
                except:
                    pass
            try:
                os.remove(f'./botqq/database/table_{self.creator}.jpg')
            except:
                pass
        else:
            print('未建立牌桌，无需关闭')
            

        pass

        


    def databaseInit(self):
        """建表"""
        con,cur = self.__connectSqlite()
        cur.execute("CREATE TABLE IF NOT EXISTS `twotwolist` (table_no INTEGER PRIMARY KEY AUTOINCREMENT, member_length INTEGER, creator TEXT, group_number TEXT, member TEXT, wait_status TEXT, create_time TEXT)")
        cur.execute(f"REPLACE INTO `twotwolist` ( member_length, creator, group_number, member, wait_status, create_time) VALUES(?,?,?,?,?,?)",(
            1, '591016144', '456123qun', '591016144|', 0, str(self.cardTable['create_time'])
            )
        )
        con.commit()
        con.close()


    def __dataSave(self, new=False):
        """存数据"""
        con,cur = self.__connectSqlite()
        if not new:
            cur.execute(f"REPLACE INTO `twotwolist` (table_no, member_length, creator, group_number, member, wait_status, create_time) VALUES(?,?,?,?,?,?,?)",(
                self.cardTable['table_no'],
                self.cardTable['member_length'], self.cardTable['creator'], self.cardTable['group_number'], self.cardTable['member'], self.cardTable['wait_status'], self.cardTable['create_time'],
                )
            )
        else:
             cur.execute(f"REPLACE INTO `twotwolist` (member_length, creator, group_number, member, wait_status, create_time) VALUES(?,?,?,?,?,?)",(
                self.cardTable['member_length'], self.cardTable['creator'], self.cardTable['group_number'], self.cardTable['member'], self.cardTable['wait_status'], self.cardTable['create_time']
                )
            )
        con.commit()# 事务提交，保存修改内容。
        con.close()


    def __checkTableEmpty(self):
        """检查牌桌是否有空位"""
        if self.cardTable['member_length'] == 4:
            self.wait_status = 0
            return False
        elif self.cardTable['member_length'] > 4:
            self.wait_status = 0
            return False
        elif self.cardTable['member_length'] < 4:
            self.wait_status = 1
            return True # 有空位


    def joinTable(self):
        """
        加入牌桌排队
        """
        # 保存信息来源
        id_original = str(self.input_text_dict['id'])

        # 查找本群存在的可加入牌桌
        try:
            con,cur = self.__connectSqlite()
            cur.execute("SELECT * FROM twotwolist WHERE group_number = ? AND wait_status = 1 LIMIT 1",(str(self.input_text_dict['group_id']),)) # 只取最早的一条
            test = list(cur.fetchall()[0])
            dict_of_text = dict(zip(self.TableHeader, test))
            self.cardTable.update(dict_of_text) # 根据查询到的牌桌更新
            self.creator = self.cardTable['creator'] # 更新creator信息
            print(self.cardTable)
            con.commit()
            con.close()
        except:
            print('本群无可加入牌桌')
            return 
        # 有可加入牌桌的前提下：
        # - 检查是否已经加入
        if str(self.input_text_dict['id']) in self.__checkMember():
            print('已在牌桌中')
            return 
        # - 为牌桌添加成员
        self.cardTable['member'] = self.cardTable['member'] + str(self.input_text_dict['id']) + '|'
        self.cardTable['member_length'] += 1
        if not self.__checkTableEmpty():
            # 牌桌满时，更新数据库状态
            self.cardTable['wait_status'] = self.wait_status
            print('牌桌状态已更新')
        self.__dataSave() # 保存最新的dict数据

        pass


    def leaveTable(self):
        """
        离开牌桌
        """

        pass


    def __getTableMessage(self, creator_id):
        """查询当前语句发送用户的牌桌信息"""
        con,cur = self.__connectSqlite()
        # 查询
        try:
            cur.execute("SELECT * FROM twotwolist WHERE creator = ? AND wait_status = 1",(creator_id,))
            test = list(cur.fetchall()[0])
            dict_of_text = dict(zip(self.TableHeader, test))
            con.commit()
            con.close()
            self.cardTable.update(dict_of_text)
            return True
        except:
            print('无记录')
            return False


    def __imgTable(self):
        """获取排队人头像，制图"""
        id_list = self.__checkMember()  # 获取当前member
        for i in range(self.cardTable['member_length']):
            # print(i)
            url1 = f"http://q1.qlogo.cn/g?b=qq&nk={str(id_list[i])}&s=640" # qq头像接口
            img_temp = urllib.request.urlopen(url1, timeout=30)
            if img_temp is not None:
                with open(f'./botqq/database/qlogo/{self.creator}_{i}.png', 'wb') as f:
                    f.write(img_temp.read())
                    f.flush()
                    f.close()
                self.__circle(i)
        # 将四张图片拼在一起
        for i in range(self.cardTable['member_length']):
            if os.path.exists(f'./botqq/database/table_{self.creator}.jpg'):
                out_dir = self.__mixPicture(i, if_exist=True) # 将图片路径返回
            else:
                out_dir = self.__mixPicture(i, if_exist=False) # 将图片路径返回
        return out_dir


    def __circle(self, img_id):
        img_path = f'./botqq/database/qlogo/{self.creator}_{img_id}.png'

        image = cv2.imread(img_path)
        image = cv2.resize(image, (140,140)) # 重塑大小
        cv2.imwrite(img_path, image)

        save_path = f'./botqq/database/qlogo/{self.creator}_{img_id}_c.png' # 保存位置
        ima = Image.open(img_path).convert("RGBA")
        size = ima.size
        # 因为是要圆形，所以需要正方形的图片
        r2 = min(size[0], size[1])
        if size[0] != size[1]:
            ima = ima.resize((r2, r2), Image.ANTIALIAS)
        # 最后生成圆的半径
        r3 = int(r2/2)
        imb = Image.new('RGBA', (r3*2, r3*2),(255,255,255,0))
        pima = ima.load() # 像素的访问对象
        pimb = imb.load()
        r = float(r2/2) #圆心横坐标
    
        for i in range(r2):
            for j in range(r2):
                lx = abs(i-r) #到圆心距离的横坐标
                ly = abs(j-r)#到圆心距离的纵坐标
                l = (pow(lx,2) + pow(ly,2))** 0.5 # 三角函数 半径
                if l < r3:
                    pimb[i-(r-r3),j-(r-r3)] = pima[i,j]
        
        imb.save(save_path)
        return save_path


    def __mixPicture(self, img_id, if_exist=False):
        """
        将图片合并在一起
        """
        creator = self.cardTable['creator']
        img_path = f'./botqq/database/qlogo/{creator}_{img_id}_c.png'

        if not if_exist:
            base_img = Image.open('./botqq/database/table.jpg')
        else:
            base_img = Image.open(f'./botqq/database/table_{creator}.jpg')
        base_img.convert('RGBA')
        img_start_end = [(0,0,140,140),(0,140,140,280),(140,0,280,140),(140,140,280,280)] # 4个位置

        box = img_start_end[img_id]  # 底图上需要P掉的区域
        tmp_img = Image.open(img_path) # 需要传的图片
        region = tmp_img
        
        region = region.convert('RGBA')
        base_img.paste(region, box)
        
        base_img.save(f'./botqq/database/table_{creator}.jpg') #保存图片
        return f'./botqq/database/table_{creator}.jpg'


    def checkOrder(self):
        """指令入口-外部接口"""
        if self.input_text[0] not in ['#22','22']:
            return 
        elif self.input_text[1] in ['等','有无']:      # 创建牌桌
            self.__buildTable()
            return (self.__imgTable(),'创建成功，赶快上车')
        elif self.input_text[1] in ['无了','鸽','鸽了']:      # 取消自己的牌桌
            self.__shutdownTable()
            return ('','牌桌取消成功')
        elif self.input_text[1] in ['来','来了','加入','加','上车']: # 加入牌桌
            self.joinTable()
            if self.__checkTableEmpty():
                return (self.__imgTable(),'成功加入，好好享受吧')
            else:
                return (self.__imgTable(), self.__checkMember())
            
        elif self.input_text[1] in ['建表']:
            self.databaseInit()
        



if __name__ == "__main__":
    msg = {
        'id':'2238701273',
        'text_split':['22','建表'],
        'group_id':'456123qun'
    }
    test = TwoTwoOrder(msg)
    test.checkOrder()