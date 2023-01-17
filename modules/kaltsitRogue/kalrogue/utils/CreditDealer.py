#! /usr/bin/env python3
# coding:utf-8
import sqlite3
from uuid import uuid4


class CreditDealer:
    '''
        信用变化
        初始化 input:
            - id    | qq号
            - name  | 昵称
    '''
    def __init__(self, msg_out) -> None:
        self.filename = './bot/database/' # 数据库位置
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

    def __dataSave(self):
        """保存当前用户数据"""
        con,cur = self.__connectSqlite()
        cur.execute(f"REPLACE INTO `signin` ( id, signin_uid, name, exp, total_days, consecutive_days, \
            is_signin_consecutively, reliance, credit, last_signin_time) VALUES(?,?,?,?,?,?,?,?,?,?)",(
            self.signin_box['id'], self.signin_box['signin_uid'],  self.signin_box['name'], self.signin_box['exp'], \
            self.signin_box['total_days'], self.signin_box['consecutive_days'], self.signin_box['is_signin_consecutively'], \
            self.signin_box['reliance'], self.signin_box['credit'], self.signin_box['last_signin_time']
            )
        )
        con.commit()
        con.close()

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

    def CreditAction(self, credit_change: int):
        '''信用功能入口
            input: 
                - credit_change | int 每次消耗某id的信用
        '''
        if credit_change < 0: credit_change = abs(credit_change)
        # 1.查询信用值
        if self.signin_box['id'] in [2238701273]: return 'done'
        dict_of_text = self.__searchSigninData()
        if dict_of_text is not None:
            """根据查询得到的字典更新数据"""
            self.signin_box.update(dict_of_text)
        else:
            return ''

        # 2.向DarkTemple返回指令
        if self.signin_box['reliance'] >= 200 and self.signin_box['credit'] >= int(credit_change/2):
            self.signin_box['credit'] -= int(credit_change*1.0/2)
            self.__dataSave()
            return 'done'
        elif self.signin_box['credit'] >= credit_change:
            self.signin_box['credit'] -= credit_change
            self.__dataSave()
            return 'done'
        else:
            return '信用不足。'