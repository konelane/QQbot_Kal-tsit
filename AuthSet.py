#! /usr/bin/env python3
# coding:utf-8

## 应用权限管理库-部分应用需要设置权限
## 适配Kal'tsit

import sqlite3 # 导入数据库
import datetime
import os


class AuthSet:
    """
    消息权限管理库
    """
    def __init__(self,msg) -> None:
        """权限类调用初始化"""
        self.auth_user = msg['id']
        self.filename = './botqq/database/' # 初始化权限文件名
        if not os.path.exists(self.filename):
            os.makedirs(self.filename)
        
        # 待修改/更新/查询结果字典-内容初始化
        self.auth_dict = {
            'name':self.auth_user,
            'auth_level':0, #初始化为0-普通用户
            'latest_change_time':'',
            'latest_change_by':''
        }
        
        # 对应每个外部接口都设置权限
        self.init_level_need = 2
        self.change_level_need = 2
        self.query_level_need = 1
        pass
    

    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return (con,cur)


    def initAuth(self, wxid_for_change = None,auth_level_new = 0):
        """【外部接口】初始化用户权限
        多一步建表过程的【真】初始化，运行结果不一定符合最终需求，但能使该行数据诞生
        ----parameters----
        wxid_for_change: 需要修改的用户wxid
        auth_level_new: 需要修改的用户auth_level_new
        """
        if wxid_for_change == None:
            wxid_for_change = self.auth_user
        if self.__ifExistAuth(wxid_for_change):
            print('数据已存在，无需初始化')
            return [['初始化完成']]
        if self.__checkAuth(self.auth_user) >= self.init_level_need: # 检查消息发送者是否有权限
            (con,cur) = self.__connectSqlite()
            # 主键【不可重复】wxid
            cur.execute("CREATE TABLE IF NOT EXISTS user_auth(wxid TEXT PRIMARY KEY NOT NULL, auth_level INT,latest_change_time TEXT,latest_change_by TEXT)")
            time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cur.execute(
                "INSERT OR IGNORE INTO user_auth(wxid, auth_level, latest_change_time, latest_change_by) VALUES(?,?,?,?)",
                (wxid_for_change, auth_level_new, time_stamp, self.auth_user)
            )
            con.commit()
            con.close()
            print('初始化完成')
            return [['初始化完成']]
        else:
            print('权限不足')
            return [['初始化失败']]



    def _initAuthFirstTime(self, wxid_for_change = None,auth_level_new = 0):
        """initAuth函数的无需权限版
        """
        if wxid_for_change == None:
            wxid_for_change = self.auth_user
        (con,cur) = self.__connectSqlite()
        # 主键【不可重复】wxid
        cur.execute("CREATE TABLE IF NOT EXISTS user_auth(wxid TEXT PRIMARY KEY NOT NULL, auth_level INT,latest_change_time TEXT,latest_change_by TEXT)")
        time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(
            "INSERT OR IGNORE INTO user_auth(wxid, auth_level, latest_change_time, latest_change_by) VALUES(?,?,?,?)",
            (wxid_for_change, auth_level_new, time_stamp, self.auth_user)
        )
        con.commit()
        con.close()
        return [['初始化完成']]


    def __getAuth(self,user_wxid = None):
        """读取权限文档，转化成标准格式"""
        if user_wxid == None:
            user_wxid = self.auth_user
        (con,cur) = self.__connectSqlite()
        dict_temp = self.auth_dict
        if self.__ifExistAuth(user_wxid):
            cur.execute(f"SELECT * FROM user_auth WHERE wxid = ?",(user_wxid,))
            dict_temp.update(zip(list(self.auth_dict.keys()), list(cur.fetchall()[0])))
            con.close()
        else:
            print('对应id结果为空')
        return dict_temp


    def __writeAuth(self):
        """将现有auth_dict字典数据写入用户权限数据库 - 不做更改"""
        time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print('写入时间',time_stamp)
        (con,cur) = self.__connectSqlite()
        cur.execute("UPDATE user_auth SET latest_change_time = ?,latest_change_by = ?,auth_level = ? where wxid = ?",
            (time_stamp,self.auth_user, int(self.auth_dict['auth_level']), self.auth_dict['name'])
        )
        con.commit()
        con.close()
        print('写入完成')
            

    def __checkAuth(self, wxid_for_check = None):
        """检查账号权限"""
        if wxid_for_check == None:
            wxid_for_check = self.auth_user
        dict_temp = self.__getAuth(wxid_for_check)
        return dict_temp['auth_level']
        

    def changeAuth(self,wxid_for_change = None,auth_level_new = 0):
        """【外部接口】用户修改权限
        成功运作前提是，数据的wxid在库中已存在
        ----parameters----
        wxid_for_change: 需要修改的用户wxid
        auth_level_new: 需要修改的用户auth_level_new
        """
        if wxid_for_change == None:
            wxid_for_change = self.auth_user
        if self.__checkAuth(wxid_for_check = self.auth_user) >= self.change_level_need:
            if self.__ifExistAuth(wxid_for_change):
                # 若已存在于库中，直接修改
                """修改/更新权限"""
                self.auth_dict['name'] = wxid_for_change
                self.auth_dict['auth_level'] = auth_level_new
                self.__writeAuth()
                return ['修改完成']
            else:
                # 若不存在于库中，则进行初始化
                self.initAuth(wxid_for_change,auth_level_new)
        else:
            print('权限不足，无法修改')
            return [['修改失败']]
        

    def __ifExistAuth(self,wxid):
        """查询该wxid对应数据是否在库中存在
        若存在，输出为True
        ----parameters----
        wxid: 需要查询的wxid
        """
        (con,cur) = self.__connectSqlite()
        cur.execute(f"SELECT * FROM user_auth WHERE wxid = ?",(wxid,))
        ans = len(cur.fetchall())==1
        con.close()
        return ans


    def queryAuth(self,wxid_for_query = None):
        """【外部接口】查询权限字典并返回"""
        if wxid_for_query == None:
            wxid_for_query = self.auth_user
        if self.__checkAuth(wxid_for_check = self.auth_user) >= self.change_level_need:
            if not self.__ifExistAuth(wxid_for_query):
                print('数据不存在')
                return [['数据不存在']]
            else:
                (con,cur) = self.__connectSqlite()
                cur.execute(f"SELECT * FROM user_auth WHERE wxid = ?",(wxid_for_query,))
                query_ans_list = cur.fetchall()
                con.close()
                return query_ans_list
        else:
            print('权限不足，无法查询')
            return [['查询失败']]
        


if __name__ == "__main__":
    msg2 = {'id':'591016144'}
    testkonelane = AuthSet(msg2)
    testkonelane._initAuthFirstTime(auth_level_new = 2)
    testkonelane.queryAuth()


    # msg1 = {'id':'2238701273'}
    # testhehe = AuthSet(msg1)

    # print('---query 建立前---')
    # print(testkonelane.queryAuth('2238701273'))

    # print('---init 自己修改---')
    # testhehe.initAuth(auth_level_new = 0)

    # print('---init2 有权限者帮忙修改---')
    # testkonelane.initAuth(wxid_for_change='2238701273',auth_level_new = 2)

    # print('---query 有权限者---')
    # print(testhehe.queryAuth())
    # # print(testtricks.queryAuth('HeAlwaysRush'))
    print('---change hehe【lv2 -> lv0】---')
    testkonelane.changeAuth(wxid_for_change='2238701273',auth_level_new=2)
    # print('---query---')
    # print(testhehe.queryAuth())
    # print(testkonelane.queryAuth('2238701273'))

