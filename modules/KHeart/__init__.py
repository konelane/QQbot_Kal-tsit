#! /usr/bin/env python3
# coding:utf-8

import asyncio
import os
import random
import sqlite3
import time, datetime
from os.path import basename
from uuid import uuid4

from core.decos import check_group, check_member, DisableModule, check_permitGroup
from core.MessageProcesser import MessageProcesser
from core.ModuleRegister import Module
from database.kaltsitReply import (blockList, ActionList)
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, Plain
from graia.ariadne.message.parser.twilight import RegexMatch, Twilight, UnionMatch
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

# 学习复读功能

channel = Channel.current()
module_name = basename(__file__)[:-3]
Module(
    name='KHeart',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.KHeart',
).register()


class stopRepeatQueue:
    def __init__(self, msg) -> None:
        self.msg = msg
        self.filename = './bot/database/'
        self.groupId = str(msg['group_id'])
        self.pub_time = datetime.datetime.now()
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
        # print(linescheck)
        if linescheck <= 10:
            return False
        else:
            cur.execute(f"SELECT text FROM (SELECT * FROM '{self.groupId}_text' ORDER BY pub_time desc LIMIT 3)")
            temp = list(set(list(cur.fetchall())))
            if len(temp) == 1 and temp[0][0] == self.msg['text_ori']: 

                # 先检查复读模块
                cur.execute(f"SELECT text FROM (SELECT * FROM '{self.groupId}_text' ORDER BY pub_time desc LIMIT 5)")
                # print(cur.fetchall())
                temp_fi = list(set(list(cur.fetchall())))
                # print(temp) # [('凯尔希不能发图了草',), ('哭了',), ('哈哈哈',)]
                con.close()
                if len(temp_fi) == 1 and temp_fi[0][0] == self.msg['text_ori']:
                    return True
                else:
                    # 非复读，则学习
                    return (self.msg['text_ori'], self.msg['text_ori'], 'repeat') # 复读三次
            else:
                cur.execute(f"SELECT text FROM (SELECT * FROM '{self.groupId}_text' ORDER BY pub_time desc LIMIT 4)")  # 重复对话2次
                temp2 = list(cur.fetchall())
                if len(temp2)<4: pass
                else:
                    order_out = list(set([(temp2[0], temp2[1]),(temp2[2], temp2[3])])) # ,(temp2[4], temp2[5])
                    if len(order_out) == 1: 
                        return (temp2[1][0], temp2[0][0], 'dialogue') # 倒排索引
            
                # 未触发学习模块则退出
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
        temp_order = self.__checkData() # 上下文检查器
        if (temp_order is not None) and (temp_order not in [True, False]):
            ## 需要在触发后删除训练文本
            con,cur = self.__connectSqlite()
            cur.execute(f"DELETE FROM '{self.groupId}_text' WHERE text in(SELECT `text` FROM '{self.groupId}_text' ORDER BY pub_time desc LIMIT 3)")
            con.commit()# 事务提交，保存修改内容。
            con.close()

            return temp_order # keyword reply 元组
            
        elif temp_order == True:
            # 复读触发，发图，清理数据
            con,cur = self.__connectSqlite()
            cur.execute(f"DELETE FROM '{self.groupId}_text' WHERE text in(SELECT `text` FROM '{self.groupId}_text' ORDER BY pub_time desc LIMIT 4)") # 删除最后相同的数据
            con.commit()# 事务提交，保存修改内容。
            con.close()
            
            return '咳咳'
        else:
            # 保存新数据
            
        
            return 





class KHeart:
    """学习说话功能
    
    """
    
    def __init__(self, msg_out, order) -> None:
        """order是三维元祖"""
        self.filename = './bot/database/' # 数据库位置
        self.heart_box = {
            'rule_id':0,
            'rule_uid':str(uuid4()),
            'creator_id':msg_out['id'],
            'first_group':msg_out['group_id'],
            'keyword':order[0],
            'reply':order[1],
            
            # 'already_signin':0,

            'group_id':msg_out['group_id'],
            'text_ori':msg_out['text_ori'],
            'signin_new_name': msg_out['name'],
        }
        self.table_head = [
            'rule_id', 'rule_uid', 'creator_id', 'first_group', 'keyword', 'reply', 'change_id', 'change_group', 'start_date', 'end_date', 'dp'
        ]
        self.max_tm = '4712/12/31-23:59:59'
        self.order_input = order
        self.randomReply = 0
        

    def __random_pick(self, some_list, probabilities): 
        '''概率抽取'''
        x = random.uniform(0,1) 
        cumulative_probability = 0.0 
        for item, item_probability in zip(some_list, probabilities): 
            cumulative_probability += item_probability 
            if x < cumulative_probability:
                break 
        return item 


    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return (con,cur)


    def databaseInit(self):
        """建表 数据库表
        rule_id, rule_uid, creator_id, first_group, keyword, reply, change_id, change_group, start_date, end_date, dp
        """
        con,cur = self.__connectSqlite()
        cur.execute("CREATE TABLE IF NOT EXISTS `kheart` (  \
                rule_id INTEGER, rule_uid TEXT PRIMARY KEY NOT NULL, creator_id INTEGER, first_group INTEGER, \
                keyword TEXT, reply TEXT, change_id INTEGER, change_group INTEGER, \
                start_date TEXT, end_date TEXT, dp TEXT \
            )")
        cur.execute(f"REPLACE INTO `kheart` ( rule_id, rule_uid, creator_id, first_group, keyword, reply, change_id,  \
            change_group, start_date, end_date, dp ) VALUES(?,?,?,?,?, ?,?,?,?,?,?)",(
            1, str(uuid4()),  591016144, 114514, '催更', '快更新！', 
            1919810, 114514, time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime()), self.max_tm, 'ACTIVE'
            )
        )
        con.commit()
        con.close()
        print('建表成功')


    def __createRule(self):
        """创建关键词规则-不直接使用，作为备选项使用"""
        con,cur = self.__connectSqlite()

        cur.execute(f"REPLACE INTO `kheart` ( rule_id, rule_uid, creator_id, first_group, keyword, reply, change_id,  \
            change_group, start_date, end_date, dp ) VALUES(?,?,?,?,?, ?,?,?,?,?,?)",(
            1, self.heart_box['rule_uid'],  self.heart_box['creator_id'], self.heart_box['first_group'], self.heart_box['keyword'], self.heart_box['reply'], 
            self.heart_box['creator_id'], self.heart_box['first_group'], time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime()), self.max_tm, 'ACTIVE'
            )
        )
        con.commit()
        con.close()
        print('规则创建！')


    def editRuleCondition(self):
        """更新旧规则"""
        dict_of_text = self.__searchRuleData() # 获取表内最新规则
        if dict_of_text is not None:
            con,cur = self.__connectSqlite()

            cur.execute(f"REPLACE INTO `kheart` ( rule_id, rule_uid, creator_id, first_group, keyword, reply, change_id,  \
                change_group, start_date, end_date, dp ) VALUES(?,?,?,?,?, ?,?,?,?,?,?)",(
                dict_of_text['rule_id'], dict_of_text['rule_uid'],  dict_of_text['creator_id'], dict_of_text['first_group'], dict_of_text['keyword'], dict_of_text['reply'], 
                self.heart_box['creator_id'], self.heart_box['group_id'], dict_of_text['start_date'], time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime()), 'EXPIRED'
                )
            )
            cur.execute(f"REPLACE INTO `kheart` ( rule_id, rule_uid, creator_id, first_group, keyword, reply, change_id,  \
                change_group, start_date, end_date, dp ) VALUES(?,?,?,?,?, ?,?,?,?,?,?)",(
                dict_of_text['rule_id'], self.heart_box['rule_uid'],  dict_of_text['creator_id'], dict_of_text['first_group'], dict_of_text['keyword'], self.heart_box['reply'], 
                self.heart_box['creator_id'], self.heart_box['group_id'], time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime()), self.max_tm, 'ACTIVE'
                )
            )
            con.commit()
            con.close()
            print('规则更新完毕！')
        else:
            self.__createRule()


    def __searchRuleData(self):
        """查询规则资料"""
        dict_of_text = None
        con,cur = self.__connectSqlite()
        try:
            cur.execute("SELECT * FROM `kheart` WHERE keyword = ? AND dp = 'ACTIVE' ",(self.heart_box['keyword'],))
            test = list(cur.fetchall()[0])

            dict_of_text = dict(zip(self.table_head, test))
        except:
            print('未查到记录')
        finally:
            con.commit()
            con.close()

        return dict_of_text



    def heartAction(self):
        """回复功能入口"""
        dict_of_text = self.__searchRuleData()
        self.randomReply = self.__random_pick([0,1], [0.99, 0.01])
        # self.randomReply = 1
        if self.randomReply == 1:
            # 随机说一句话
            con,cur = self.__connectSqlite()
            try:
                cur.execute("SELECT reply FROM `kheart` WHERE dp = 'ACTIVE' ")
                test = list(cur.fetchall())
                print(test)
                return random.choice(test)[0]
            except:
                print('未查到记录')
            finally:
                con.commit()
                con.close()


        elif dict_of_text is None:
            return 
        else:
            return dict_of_text['reply']


    def deleteRule(self):
        dict_of_text = self.__searchRuleData() # 获取表内最新规则
        if dict_of_text is not None:
            con,cur = self.__connectSqlite()

            cur.execute(f"REPLACE INTO `kheart` ( rule_id, rule_uid, creator_id, first_group, keyword, reply, change_id,  \
                change_group, start_date, end_date, dp ) VALUES(?,?,?,?,?, ?,?,?,?,?,?)",(
                dict_of_text['rule_id'], dict_of_text['rule_uid'],  dict_of_text['creator_id'], dict_of_text['first_group'], dict_of_text['keyword'], dict_of_text['reply'], 
                self.heart_box['creator_id'], self.heart_box['group_id'], dict_of_text['start_date'], time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime()), 'EXPIRED'
                )
            )
            con.commit()
            con.close()
            print('规则删除完毕！')
            return 'done'




@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        # inline_dispatchers=[Twilight([RegexMatch(r'#sc')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def StopRepeat_inGroup(
    app: Ariadne, 
    group: Group, 
    message: MessageChain,
    member: Member
):
    # 复读打断功能
    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()   
    if msg_info_dict != '':
        test = stopRepeatQueue(msg_info_dict)
        check_table_if_exist = test.checkTables() # 1和0
        
        if check_table_if_exist != 0:
            # print(test.activeRun())
            temp_text = test.activeRun() # 内含复读检查与kheart学习功能
            if temp_text is None:
                # 检查是否满足kheart回复规则
                heart = KHeart(msg_info_dict, (msg_info_dict['text_ori'], '', 'space',))
                out_text = heart.heartAction()
                if out_text is not None and (msg_info_dict['text_ori'] not in ActionList.actionOrderList):
                    await app.sendGroupMessage(group, MessageChain.create([
                       Plain(out_text)
                    ]))
            elif len(temp_text) == 3:
                ## kheart学习功能入口
                heart = KHeart(msg_info_dict, temp_text)
                heart.editRuleCondition()
                if temp_text[2] in ['repeat']:
                    out_text = heart.heartAction()
                    print('chufachufachufa')
                    if out_text is not None and (temp_text[0] not in ActionList.actionOrderList) and (group.id in blockList.permitGroup):
                        await app.sendGroupMessage(group, MessageChain.create([
                            Plain(out_text)
                        ]))
            elif temp_text == '咳咳' and (group.id in blockList.permitGroup):
                await app.sendGroupMessage(group, MessageChain.create([
                    Image(path = './bot/database/faces/stopRepeat.jpg')
                    # Image(url = 'https://m1.im5i.com/2021/11/19/Un5Qhf.jpg')
                ]))
            
                
        else:
            test.databaseInit()



@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'#删除')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def deleteRule(
    app: Ariadne, 
    group: Group, 
    message: MessageChain,
    member: Member
):
    
    ## 直接删除规则
    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()   

    if msg_info_dict['text_split'][0] not in ['#删除']:
        return 
    else:
        temp = KHeart(msg_info_dict, (' '.join([x for x in msg_info_dict['text_split'][1:]]), '', 'delete',))
        return_of_delete = temp.deleteRule()
        if return_of_delete is not None:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain('规则已清理。')
            ]))