# import graia.application.group as Group

from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain
import asyncio
from graia.application.message.elements.internal import Plain,At,Image
from graia.application.friend import Friend

import os
import sys
import random
# import graia.application.message.elements.internal as Elements
from graia.application.event.messages import Group,Member

# from squads_init import operator
from prts import prts
import squads_init as si
from time import sleep

# 回滚版本请在powershell中输入.\mcl --update-package net.mamoe:mirai-console --channel stable --version 2.6.7

# from graia.saya import Saya, Channel
# from graia.saya.builtins.broadcast.schema import ListenerSchema
# from graia.application.exceptions import AccountMuted
# from graia.application.event.messages import GroupMessage
# from graia.application.message.parser.kanata import Kanata
# from graia.application.message.parser.signature import RegexMatch


loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://localhost:8080", # 填入 httpapi 服务运行的地址
        authKey="INITKEYyicPQIDq", # 填入 authKey
        account=591016144, # 你的机器人的 qq 号
        websocket=True # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)


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
    '沉默是最大的傲慢。'
]



@bcc.receiver("GroupMessage")
async def arknights_hw_rollbox(
    app: GraiaMiraiApplication,
    message: MessageChain,
    group: Group,
    member: Member
):

    text = message.get(Plain)[0].text.split(' ')
    id = member.id
    # 暂时删除群作业系统
    if message.asDisplay().startswith("#hw"):
        f = os.popen('python ./botqq/operator_rollbox_bot.py','r')
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

    # 暂时删除夸夸系统
    if message.asDisplay().startswith("#praise"):
        f = os.popen('python ./botqq/praise.py','r')
        d = f.read() 
        # print(message.get('source'))
        await app.sendGroupMessage(group, MessageChain.create([
            At(member.id),Plain(d)
        ]))

    # 暂时删除复读系统
    if message.asDisplay().startswith("？"):
        await app.sendGroupMessage(group, MessageChain.create([
            Plain("？")
        ]))

    if message.asDisplay().startswith("好耶"):
        await app.sendGroupMessage(group, MessageChain.create([
            Plain("好耶")
        ]))


    #### 跑团 ####
    if (text[0] == "#读取"):
        filename =  'C:/Users/ASUS/botqq/' + text[1] + '_opt.txt'
        with open(filename, "r") as f:
            d = f.read()
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(d)
        ]))

    if (text[0] == "#初始化"):
        """ #初始化 hehe 1 2 3 4"""
        if len(text)!=6:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain('初始化缺失输入')
            ]))
        else:
            create_opt = si.operator(text[1],text[2],text[3],text[4],text[5])
            create_opt.init_opt()
            # sleep(10)
            filename =  'C:/Users/ASUS/botqq/' + text[1] + '_opt.txt'
            with open(filename, "r") as f:
                d = f.read()
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(d)
            ]))

    if (text[0] == "#检定"):
        # 检定 hehe agile 【skillful_ = 0，object_dict = None
        create_opt = si.operator(text[1],0,0,0,0)
        
        if len(text) == 4:
            _point,_against = create_opt.against_action(text[2], skillful_ = text[3])
        elif len(text) == 3:
            _point,_against = create_opt.against_action(text[2])
        elif len(text)==5:
            against_opt = si.operator(text[4],0,0,0,0)
            _point,_against = create_opt.against_action(text[2], skillful_ = text[3], object_dict = against_opt.read_opt())
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('主体检定值为：'+str(_point)+'\n客体豁免值为：'+str(_against))
        ]))

    if (text[0] == "#背包"):
        # 目前仅支持热水壶XD
        # 后续需绑定id
        create_opt = si.operator(text[1],0,0,0,0)
        if (text[2] == "增加"):
            create_opt.__update_opt__('package','增加'+text[3])
            filename =  'C:/Users/ASUS/botqq/' + text[1] + '_opt.txt'
            with open(filename, "r") as f:
                d = f.read()
        if (text[2] == "减少"):
            create_opt.__update_opt__('package','减少'+text[3])
            filename =  'C:/Users/ASUS/botqq/' + text[1] + '_opt.txt'
            with open(filename, "r") as f:
                d = f.read()
        if (text[2] == "使用"):
            create_opt.use_equip_package_change('use',text[3])
            
        if (text[2] == "查询"):
            create_opt.use_equip_package_change('lookup',text[3])

        await app.sendGroupMessage(group, MessageChain.create([
            Plain(d)
        ]))

    if (text[0] == "#经验"):
        # 【#经验 hehe 10000
        # 后续需绑定id
        if len(text) == 3:
            create_opt = si.operator(text[1],0,0,0,0)
            create_opt.__update_opt__('exp','增加' + text[2])
            create_opt.opt_upgrade()
            exp_ = create_opt.read_opt()['exp']
            level_ = create_opt.read_opt()['level']
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(text[1]+':\n当前的经验值为:'+str(exp_)+'\n当前的等级为:'+str(level_))
            ]))
        else:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain('输入错误')
            ]))
            


    #### prts ####
    if(text[0] == '#prts'):
        prts_1 = prts(text[1])
        # 自查保护机制
        if text[1] == '凯尔希':
            await app.sendGroupMessage(group, MessageChain.create([
                Plain('我的情况由我自己判断，各位应该把注意力放在其他需要帮助的感染者身上。')
            ]))
            return
        
        text_kal = random.sample(text_table,1)[0] + '\n'
        # print(text_kal)
        # 技能专精材料
        if text[2] == '技能专精':
            try:
                out_list = prts_1.MasteryMetarialGet()
            except:
                out_list = ['……输入错误了，看起来失忆对你造成了不小的影响']
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(text_kal + '\n'+'\n'.join(out_list))
            ]))

        elif text[2] =='信息':
            try:
                out_list = prts_1.BaseInfoGet()
            except:
                out_list = ['……输入错误了，看起来失忆对你造成了不小的影响']
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(text_kal + '\n'+'\n'.join(out_list))
            ]))

        elif text[2] =='晋升材料':
            try:
                out_list = prts_1.EliteMetarialGet()
            except:
                out_list = ['……输入错误了，看起来失忆对你造成了不小的影响']
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(text_kal + '\n'+'\n'.join(out_list))
            ]))

        elif text[2] =='属性':
            try:
                out_list = prts_1.AttributeGet()
            except:
                out_list = ['……输入错误了，看起来失忆对你造成了不小的影响']
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(text_kal + '\n'+'\n'.join(out_list))
            ]))

        elif text[2] =='后勤':
            try:
                out_list = prts_1.LogisticsSkill()
            except:
                out_list = ['……输入错误了，看起来失忆对你造成了不小的影响']
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(text_kal + '\n'+'\n'.join(out_list))
            ]))

        elif text[2] =='专精图':
            try:
                prts_1.MasteryPicGet()
                out_list = ['或许我们思索的并不是同一件事。']
            except:
                out_list = ['……输入错误了，看起来失忆对你造成了不小的影响']
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(text_kal + '\n'+'\n'.join(out_list)),
                Image.fromLocalFile('./botqq/temp.png')
            ]))

        elif text[2] == '生日':
            try:
                out_list = prts_1.BirthdayGet()
            except:
                out_list = ['……输入错误了，看起来失忆对你造成了不小的影响']
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(text_kal + '\n这位干员的生日是'+out_list)
            ]))
        # await app.sendGroupMessage(group, MessageChain.create([
        #     Plain(f'我说的太多了，你应该`http://prts.wiki/w/{text[1]}`'+'\n去自己看看')
        # ]))

if __name__ == "__main__":
    app.launch_blocking()

