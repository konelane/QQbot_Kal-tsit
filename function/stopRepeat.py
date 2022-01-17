#! /usr/bin/env python3
# coding:utf-8

import sqlite3
from datetime import datetime

class stopRepeatQueue:
    def __init__(self, msg) -> None:
        self.msg = msg
        self.filename = './botqq/database/'
        self.groupId = str(msg['group_id'])
        self.pub_time = datetime.now()
        pass


    def databaseInit(self):
        """给当前群建表"""
        con,cur = self.__connectSqlite()
        cur.execute(f"CREATE TABLE IF NOT EXISTS `{self.groupId}_text` (pub_time TEXT PRIMARY KEY NOT NULL, text TEXT, pub_id TEXT)")
        con.commit()# 事务提交，保存修改内容。
        con.close()
        cur.execute(f"REPLACE INTO '{self.groupId}_text' (pub_time, text, pub_id) VALUES(?,?,?)",(
            'header', 'good', '123456789'
            )
        )
        self.__dataSave() # 保存消息内容




    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return (con,cur)


    def __dataSave(self):
        """存数据"""
        con,cur = self.__connectSqlite()
        cur.execute(f"REPLACE INTO '{self.groupId}_text' (pub_time, text, pub_id) VALUES(?,?,?)",(
            self.pub_time, self.msg['text_ori'], self.msg['id']
            )
        )
        con.commit()# 事务提交，保存修改内容。
        con.close()


    def __checkData(self):
        """消息-查询-检查"""
        con,cur = self.__connectSqlite()
        cur.execute(f"SELECT COUNT(*) FROM '{self.groupId}_text'")
        linescheck = cur.fetchall()[0][0]
        print(linescheck)
        if linescheck <= 10:
            return False
        else:
            cur.execute(f"SELECT text FROM (SELECT * FROM '{self.groupId}_text' ORDER BY pub_time desc LIMIT 5)")
            # print(cur.fetchall())
            temp = list(set(list(cur.fetchall())))
            # print(temp) # [('凯尔希不能发图了草',), ('哭了',), ('哈哈哈',)]
            con.close()
            if len(temp) == 1 and temp[0][0] == self.msg['text_ori']:
                return True
            else:
                return False

    def checkTables(self):
        con,cur = self.__connectSqlite()
        # cur.execute(f"SELECT ObjectProperty(Object_ID('{self.groupId}_text'),'IsUserTable')")
        # cur.execute(f"SELECT COUNT(1) FROM sys.objects WHERE name = '{self.groupId}_text'")
        cur.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name = '{self.groupId}_text'")
        check_result = list(cur.fetchall()[0])[0]
        return check_result


    def activeRun(self):
        """检查-选择操作-保存"""
        self.__dataSave()
        if self.__checkData():
            # 复读触发，发图，清理数据
            con,cur = self.__connectSqlite()
            cur.execute(f"DELETE FROM '{self.groupId}_text' WHERE text in(SELECT `text` FROM '{self.groupId}_text' ORDER BY pub_time desc LIMIT 4)") # 删除最后相同的数据
            con.commit()# 事务提交，保存修改内容。
            con.close()
            
            return '咳咳'
        else:
            # 保存新数据
            
        
            return 


