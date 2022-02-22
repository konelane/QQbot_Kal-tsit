'''
Author: KOneLane
Date: 2022-02-16 23:40:10
LastEditors: KOneLane
LastEditTime: 2022-02-21 21:11:22
Description: 
version: V
'''
# from msvcrt import kbhit
import sqlite3
import datetime

class StarCraftPVE:
    """
    查询每周突变
    """
    def __init__(self, searchtext):
        self.name = searchtext
        self.filename = './botqq/database/' # 初始化权限文件路径
        self.TableHeader = [
            '突变名称','编号','地图','因子一','因子二','因子三'
        ]
        
        ## 基准日
        self.start_number = 70
        self.date_of_base = {'year':2022,'month':2,'day':14}

    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return (con,cur)


    def NextTubian(self, k=0):
        """以某一周为起点，查询之后的突变"""
        (con,cur) = self.__connectSqlite()
        cur = con.cursor()
        date2 = datetime.datetime.today()
        interval = date2 -   datetime.datetime(2022,2,14) # 两日期差距
        newID = interval.days // 7 + self.start_number + 1 + k # 未来k周突变
        print(newID)
        try:
            cur.execute("SELECT * FROM starcraftpve WHERE 编号 = ?",(newID,))
            test = list(cur.fetchall()[0])
            dict_of_text = dict(zip(self.TableHeader, test))
            print(dict_of_text)
            msg_dict = dict_of_text
        except:
            print(self.name)
            msg_dict = 'error'
        if msg_dict == 'error':
            cardText = '查不到该突变'
        else:
            cardText = '\n'.join([str(x)+':'+str(msg_dict[x]) for x in self.TableHeader if msg_dict[x]]) # 只返回非空值
        return cardText


    def TubianSearch(self):
        """按照突变名称查询突变"""
        (con,cur) = self.__connectSqlite()
        cur = con.cursor()
        try:
            cur.execute("SELECT * FROM starcraftpve WHERE 突变名称 = ?",(self.name,))
            test = list(cur.fetchall()[0])
            dict_of_text = dict(zip(self.TableHeader, test))
            print(dict_of_text)
            msg_dict = dict_of_text
        except:
            print(self.name)
            msg_dict = 'error'

        if msg_dict == 'error':
            cardText = '查不到该突变'
        else:
            cardText = '\n'.join([str(x)+':'+str(msg_dict[x]) for x in self.TableHeader if msg_dict[x]]) # 只返回非空值
        return cardText



if __name__ == "__main__":
    # testclass = StarCraftPVE('自作自受')
    # print(testclass.TextReturn())
    testclass = StarCraftPVE('16')
    print(testclass.NextTubian())