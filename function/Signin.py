'''
Author: KOneLane
Date: 2022-02-26 10:40:40
LastEditors: KOneLane
LastEditTime: 2022-02-27 18:54:46
Description: 
    github: https://github.com/Redlnn/signin-image-generator
    edit by KOneLane (AGPL-3.0)
version: V
'''
import os
import sqlite3
import time
from uuid import uuid4
import time
# from signinImageGenerator.main import get_signin_img

class Signin:
    """签到数据库、图片操作等
    
    """
    
    def __init__(self, msg_out) -> None:
        self.filename = './botqq/database/' # 数据库位置
        self.signin_box = {
            'id':msg_out['id'],
            'signin_uid':str(uuid4()),
            'name': msg_out['name'],
            'exp':0,
            'total_days':0,
            'consecutive_days':0,
            'is_signin_consecutively':0,
            'reliance':0,
            'credit':0,
            'last_signin_time': "2021/05/12-12:00:00",
            # 'already_signin':0,

            'group_id':msg_out['group_id'],
            'text_ori':msg_out['text_ori'],
        }
        self.TableHeader = [
            'id','signin_uid','name','exp','total_days','consecutive_days',
            'is_signin_consecutively','reliance','credit','last_signin_time',#'already_signin'
        ]
        


    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return (con,cur)


    def databaseInit(self):
        """建表"""
        con,cur = self.__connectSqlite()
        cur.execute("CREATE TABLE IF NOT EXISTS `signin` (  \
                id INTEGER PRIMARY KEY NOT NULL, signin_uid TEXT, name TEXT, \
                exp INTEGER, total_days INTEGER, consecutive_days INTEGER, is_signin_consecutively INTEGER, \
                reliance INTEGER, credit INTEGER, last_signin_time TEXT \
            )")
        cur.execute(f"REPLACE INTO `signin` ( id, signin_uid, name, exp, total_days, consecutive_days, \
            is_signin_consecutively, reliance, credit, last_signin_time ) VALUES(?,?,?,?,?,?,?,?,?,?)",(
            591016144, str(uuid4()),  '凯尔希初始化', 200, 365, 10, 
            1, 120, 2000, time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime())
            )
        )
        con.commit()
        con.close()
        print('建表成功')


    def __dataSave(self):
        """保存当前用户数据"""
        con,cur = self.__connectSqlite()
        cur.execute(f"REPLACE INTO `signin` ( id, signin_uid, name, exp, total_days, consecutive_days, \
            is_signin_consecutively, reliance, credit, last_signin_time) VALUES(?,?,?,?,?,?,?,?,?,?)",(
            self.signin_box['id'], self.signin_box['signin_uid'],  self.signin_box['name'], self.signin_box['exp'], \
            self.signin_box['total_days'], self.signin_box['consecutive_days'], self.signin_box['is_signin_consecutively'], \
            self.signin_box['reliance'], self.signin_box['credit'], time.strftime("%Y/%m/%d-%H:%M:%S")
            )
        )
        con.commit()
        con.close()
        pass



    def __searchSigninData(self):
        dict_of_text = None
        con,cur = self.__connectSqlite()
        try:
            cur.execute("SELECT * FROM `signin` WHERE id = ? ",(self.signin_box['id'],))
            test = list(cur.fetchall()[0])

            dict_of_text = dict(zip(self.TableHeader, test))
        except:
            print('未查到记录')
        finally:
            con.commit()
            con.close()

        return dict_of_text


    def __signin(self):
        """签到检测+数据增改
        """
        # self.signin_box['already_signin'] = 1
        # 检查签到时间差
        print(self.signin_box['last_signin_time'])
        timeNow = time.strptime(self.signin_box['last_signin_time'], "%Y/%m/%d-%H:%M:%S")
        # point_time = time.struct_time(tm_year=timeNow.tm_year, tm_mon=timeNow.tm_mon, tm_mday=timeNow.tm_mday) # 签到的当天00:00:00
        # print(str(timeNow.tm_year)+'-'+str(timeNow.tm_mon)+'-'+str(timeNow.tm_mday))
        point_time = time.strptime(str(timeNow.tm_year)+'-'+str(timeNow.tm_mon)+'-'+str(timeNow.tm_mday), "%Y-%m-%d")
        ans = time.time() - time.mktime(point_time)
        print('距离上一次签到时间为:',ans,'秒')
        if (ans > 86400) and (ans < 86400*2):
            self.signin_box['consecutive_days'] += 1
            self.signin_box['is_signin_consecutively'] = 1 
        elif ans > 86400*2:
            self.signin_box['consecutive_days'] = 1
            self.signin_box['is_signin_consecutively'] = 0 
        else:
            print('今日已签过到')
            return False

        # 签到后的奖励 
        self.signin_box['exp'] += 1            # 经验
        self.signin_box['reliance'] += 1       # 信赖
        self.signin_box['credit'] += 20        # 信用
        self.signin_box['total_days'] += 1     # 总天数
        return True


    def signinAction(self):
        """签到功能入口"""
        if self.signin_box['text_ori'] in ["#签到",'#打卡']:
            # 先从数据库中查询签到总天数、连续签到天数、上次签到时间、签到经验值
            dict_of_text = self.__searchSigninData()
            print('查到的记录为：',dict_of_text)
            if dict_of_text is not None:
                """根据查询得到的字典更新数据"""
                self.signin_box.update(dict_of_text)
            else:
                """第一次进行签到"""
                dict_of_text = {
                    'exp':0,
                    'total_days':0,
                    'consecutive_days':0,
                    'is_signin_consecutively':0,
                    'reliance':0,
                    'credit':0,
                    'last_signin_time': "2021/05/12-00:00:00",
                    # 'already_signin':0,
                }
                self.signin_box.update(dict_of_text)
            # if self.signin_box['already_signin'] != 0:
            #     return ''
            

            if self.__signin():
                self.__dataSave()
                # 生成签到图
                
                image_generator_path = os.path.dirname(__file__) + '/signinImageGenerator/main.py'
                if os.path.exists(os.path.dirname(__file__) + '/signinImageGenerator/save_test.png'):
                    os.remove(os.path.dirname(__file__) + '/signinImageGenerator/save_test.png') # 已存在，则删除
                    time.sleep(1)
                self.signin_box['name'] = self.signin_box['name'].replace(' ','·')
                print('运行路径为：',image_generator_path)
                order = f"python {image_generator_path} \
                    --id={self.signin_box['id']} \
                    --signin_uid={self.signin_box['signin_uid']} \
                    --name={self.signin_box['name']} \
                    --exp={self.signin_box['exp']} \
                    --total_days={self.signin_box['total_days']} \
                    --consecutive_days={self.signin_box['consecutive_days']} \
                    --is_signin_consecutively={self.signin_box['is_signin_consecutively']} \
                    --reliance={self.signin_box['reliance']} \
                    --credit={self.signin_box['credit']} \
                    --last_signin_time={self.signin_box['last_signin_time']}"
                # print(order)
                os.popen(order).readlines()
                
                return 'text'
            else:
                return ''
                
                
    def testtesttest(self):
        """测试打卡用，删除自己的记录"""
        con,cur = self.__connectSqlite()
        cur.execute(f"DROP TABLE `signin`")
        con.commit()
        con.close()
        self.__searchSigninData()
        self.databaseInit()


if __name__ == "__main__":
    msg = {
        'id':158088633,
        'group_id':123456,
        'name':'博士9527',
        'text_ori':'#签到',
        
    }


    test = Signin(msg)
    test.databaseInit()
    test.testtesttest()
    # test.signinAction()
    # print(timedelta(year =2022,month = 2,day = 26))
    # print(time.strftime("%Y/%m/%d-%H:%M:%S"))