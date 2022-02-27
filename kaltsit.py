'''
Author: KOneLane
Date: 2022-02-13 22:51:56
LastEditors: KOneLane
LastEditTime: 2022-02-27 18:07:41
Description: 
version: V
'''
#! /usr/bin/env python3
# coding:utf-8

###### Kal'tsit Main Program ######
### arknights homework bot V3.1 ###
###      Author: KOneLane       ###
###    Engine&Support: Mirai    ###
###   Latest Update: 22.02.27   ###


# from graia.application import GraiaMiraiApplication, Session
# from graia.application.message.chain import MessageChain
# import asyncio
# from graia.application.message.elements.internal import Image_LocalFile, Image_NetworkAddress, Plain,At,Image
# from graia.application.friend import Friend

import asyncio
import os
import random
import sys
from xml.dom.minidom import Element

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, Plain
from graia.ariadne.model import Group, Member, MiraiSession
from graia.broadcast import Broadcast

# from function.prts import Prts
import function.squads_init as si
# 系统功能库
from AuthSet import AuthSet
from database.kaltsitReply import *
# from time import sleep
# import story_xu as sx
from function.DarkTemple import Monster3, SweepSquad
from function.Desk import kaltsitDesk
from function.stopRepeat import stopRepeatQueue
from MessageProcesser import MessageProcesser

# 回滚版本请在powershell中输入.\mcl --update-package net.mamoe:mirai-console --channel stable --version 2.6.7

loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host="http://localhost:8082",  # 填入 HTTP API 服务运行的地址
        verify_key="KOneLaneKaltsit",  # 填入 verifyKey
        account=591016144,  # 你的机器人的 qq 号
    )
)



@bcc.receiver(GroupMessage)
async def arknights_hw_rollbox(
    app: Ariadne,
    message: MessageChain,
    group: Group,
    member: Member
):
    # 触发bot的先决条件 有文本
    if message.has(Plain):

        message = message.exclude(Image)
        slightly_inittext = MessageProcesser(message,group,member)
        init_text = slightly_inittext.text_processer()
        # print(init_text)
        msgout = init_text
        """
        msg_out是个字典:
        'id':          QQ号 self.id,
        'text_split':  根据空格分词结果 message.get(Plain)[0].text.split(' '),
        'text_jieba':  分词结果,
        'group_id':    群号,
        'text_ori':    原始消息文本
        'type':        来源的类型：如group
        'name':        昵称
        """
        text = msgout['text_split']

        #### 关键词检测功能
        m3 = Monster3(msgout)
        m3_text = m3.check_words()
        if m3_text:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(m3_text)
            ]))

        
        sweepSquad = SweepSquad(msgout)
        #### SS.checkWords
        return_text,kal_text_order = sweepSquad.checkWords()
        if return_text:
            if kal_text_order == 'random':
                text_kal = random.sample(text_table,1)[0] + '\n'
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain(text_kal +'\n'+ return_text)
                ]))


            elif kal_text_order in ['random','查询的天气大致如此']:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain(kal_text_order +'\n'+ return_text)
                ]))


            elif kal_text_order == 'picture':
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain(random.sample(text_table,1)[0]),
                    Image(url=return_text)
                ]))
                # await app.sendGroupMessage(group, MessageChain.create([
                #     Plain('就这' +'\n'+ return_text)
                # ]))

            elif kal_text_order == 'local_picture':
                """牌桌预约功能
                功能返回值为 tuple('文件名/空字符','文字信息')
                """
                if return_text[0] == '':
                    await app.sendGroupMessage(group, MessageChain.create([
                        Plain(return_text[1])
                    ]))
                    

                elif type(return_text[1]) != list:
                    # 人没齐 / 有差错
                    await app.sendGroupMessage(group, MessageChain.create([
                        Plain(return_text[1]+"\n"),
                        Image(path=return_text[0])
                    ]))
                elif type(return_text[1]) == list:
                    await app.sendGroupMessage(group, MessageChain.create([
                        Plain('22人，就位！'+"\n"),
                        At(int(return_text[1][0])),At(int(return_text[1][1])),At(int(return_text[1][2])),At(int(return_text[1][3])),
                        Image(path=return_text[0])
                    ]))
                    # 删除最后的牌桌


            elif kal_text_order == 'local_picture2':
                if return_text[0] != '':
                    await app.sendGroupMessage(group, MessageChain.create([
                        Plain(return_text[1]),
                        Image(path=return_text[0])
                    ]))
                else:
                    await app.sendGroupMessage(group, MessageChain.create([
                        Plain(return_text[1])
                    ]))


            elif kal_text_order is not None:
                if kal_text_order.startswith('at'):
                    await app.sendGroupMessage(group, MessageChain.create([
                        At(int(kal_text_order[2::])),
                        Plain('\n' + return_text)
                    ]))
                
            else:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain(return_text)
                ]))

        ##############
        # 复读打断功能
        test = stopRepeatQueue(msgout)
        check_table_if_exist = test.checkTables() # 1和0
        
        if check_table_if_exist != 0:
            # print(test.activeRun())
            temp_text = test.activeRun()
            if not temp_text:
                pass
            elif temp_text == '咳咳':
                await app.sendGroupMessage(group, MessageChain.create([
                    Image(path = './botqq/database/stopRepeat.jpg')
                    # Image(url = 'https://m1.im5i.com/2021/11/19/Un5Qhf.jpg')
                ]))
        else:
            test.databaseInit()

        ##############
        # 漂流瓶功能
        test_driftingbottle = kaltsitDesk(msgout)
        if msgout['text_ori'][0:2] in ['#捞','#投']:
            return_text = test_driftingbottle.kaltsitDeskApi()
            if return_text is not None:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain(return_text)
                ]))
        else:
            pass
            

        id = str(member.id)
        #### 权限模块
        if (text[0] == "#auth"):
            temp_auth = AuthSet({'id':id})
            if len(text)==2:
                use_qqid = id
            else:
                use_qqid = text[2]

            if text[1] == '查询':
                que_ans = temp_auth.queryAuth(use_qqid)
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id),Plain('这是你要的结果……\n'+'\n'.join(str(x) for x in que_ans[0]))
                ]))
            if text[1] == '初始化':
                # 此时text[3]是修改后新的等级
                if len(text)==3:
                    temp_auth.initAuth(wxid_for_change=use_qqid)
                else:
                    temp_auth.initAuth(wxid_for_change=use_qqid,auth_level_new = int(text[3]))
                que_ans = temp_auth.queryAuth(wxid_for_query = text[2])
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id),Plain('初始化后为：\n'+'\n'.join(str(x) for x in que_ans))
                ]))
            if text[1] == '修改':
                # 此时text[3]是修改后新的等级
                temp_auth.changeAuth(wxid_for_change=use_qqid,auth_level_new = int(text[3]))
                que_ans = temp_auth.queryAuth(wxid_for_query = text[2])
                await app.sendGroupMessage(group, MessageChain.create([
                    At(member.id),Plain('修改后的信息为：\n'+'\n'.join(str(x) for x in que_ans[0]))
                ]))


        # 暂时删除群作业系统 - 附加模块
        if message.asDisplay().startswith("#hw"):
            f = os.popen('python ./botqq/function/operator_rollbox_bot.py','r')
            d = f.read()  # 读文件
            # print(message.get('source'))
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id),Plain(d)
            ]))


        if message.asDisplay().startswith("#help"):

            f = os.popen('python ./botqq/readme.py','r')
            d = f.read()  # 读文件
            # print(message.get('source'))
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(d)
            ]))

    else:
        print('消息为图片')

if __name__ == "__main__":
    # app.launch_blocking()
    try:
        loop.run_until_complete(app.lifecycle())
    except:
        pass

