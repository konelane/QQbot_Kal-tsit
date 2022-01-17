#! /usr/bin/env python3
# coding:utf-8

###### Kal'tsit Main Program ######
### arknights homework bot V2.5 ###
###      Author: KOneLane       ###
###    Engine&Support: Mirai    ###
###   Latest Update: 21.12.18   ###


from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain
import asyncio
from graia.application.message.elements.internal import Image_LocalFile, Image_NetworkAddress, Plain,At,Image
from graia.application.friend import Friend

import os
import sys
import random
from graia.application.event.messages import Group,Member

# from function.prts import Prts
import function.squads_init as si
# from time import sleep
# import story_xu as sx
from function.DarkTemple import Monster3
from function.DarkTemple import SweepSquad
from function.stopRepeat import stopRepeatQueue
from function.Desk import kaltsitDesk


# 系统功能库
from AuthSet import AuthSet
from MessageProcesser import MessageProcesser

# 回滚版本请在powershell中输入.\mcl --update-package net.mamoe:mirai-console --channel stable --version 2.6.7

loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://localhost:8082", # 填入 httpapi 服务运行的地址
        authKey="KOneLaneKaltsit", # 填入 authKey
        account=591016144, # 你的机器人的 qq 号
        websocket=True # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)

# 测试未通过。。。
# #### 加好友请求
# @bcc.receiver("NewFriendRequestEvent")
# async def newfriendacc(event):
#     await event.accept('不定期进行中断测试/中断修复，只能在群聊中使用。可联系作者2238701273')
# #### 加群请求
# @bcc.receiver('BotInvitedJoinGroupRequestEvent')
# async def newgroup(event):
#     await event.accept('博士，我出现在这里，说明情况并不乐观。\n\n(输入#help 查看可用指令)')


# @bcc.receiver("FriendMessage")
# async def friend_message_listener(app: GraiaMiraiApplication, friend: Friend):
    
#     f = os.popen('python operator_rollbox_bot.py','r')
#     d = f.read()  # 读文件
#     await app.sendFriendMessage(friend, MessageChain.create([
#         Plain(d)
#     ]))

text_table = [
    '帮你查好了，不过你应该多自己动动手，毕竟这有益于恢复记忆。',
    '不要问没有意义的问题，你早已明白答案，只是不愿意接受……',
    '博士，怎样才算真正地活着？……',
    '关心你的身体有什么意义？对罗德岛暂且不提，对我，则是有相当重要的意义。',
    '罗德岛的核心部门是医疗部门，之后的时间里，你需要招募更多的医疗干员。',
    '这是你要的资料……',
    '你醒了吗，还是还在梦中？',
    '被剥夺身份的我们，有了共同的名字。',
    '你会质疑自己存在的意义吗，博士？',
    '我们无法忘怀过去，但你会有不一样的未来。',
    '可以。',
    '走了。',
    '沉默是最大的傲慢。',
    '完美是完美者的通行证，谜语是谜语者的墓志铭。',
    '博士，其实我……唔，当我没说。',
    '博士，我们收到的剿灭委托完成了吗？',
    '工作使我们充实，能赋予这缺乏意义的人生一段高光。',
    '博士，凌晨两点有你的考勤记录。罗德岛不推荐这样的加班。'
]



@bcc.receiver("GroupMessage")
async def arknights_hw_rollbox(
    app: GraiaMiraiApplication,
    message: MessageChain,
    group: Group,
    member: Member
):
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
                Image_NetworkAddress(return_text)
            ]))
        elif kal_text_order.startswith('at'):
            await app.sendGroupMessage(group, MessageChain.create([
                At(kal_text_order[2::]),
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
                Image_LocalFile('./botqq/database/stopRepeat.jpg')
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

    # # 对联
    # couplet_text = sweepSquad.coupletGet()
    # if couplet_text:
    #     await app.sendGroupMessage(group, MessageChain.create([
    #         Plain(couplet_text)
    #     ]))

if __name__ == "__main__":
    app.launch_blocking()

