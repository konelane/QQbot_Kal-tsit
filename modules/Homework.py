#! /usr/bin/env python3
# coding:utf-8
import random
from os.path import basename

from core.decos import check_group, check_member, DisableModule
from core.ModuleRegister import Module
from core.MessageProcesser import MessageProcesser
from database.kaltsitReply import blockList

from graia.ariadne.message.parser.twilight import RegexMatch
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At
from graia.ariadne.message.parser.twilight import Twilight
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()

module_name = basename(__file__)[:-3]

Module(
    name='Homework',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.Homework',
).register()

class Operator_rollbox:
    feature = ['先锋','狙击','医疗','术师','近卫','重装','辅助','特种']
    operator_dict = {
        '菲亚梅塔':'狙击','澄闪':'术师','令':'辅助','老鲤':'特种','灵知':'辅助','耀骑士临光':'近卫','焰尾':'先锋','远牙':'狙击','琴柳':'先锋',
        '假日威龙陈':'狙击','水月':'特种','帕拉斯':'近卫','卡涅利安':'术师','浊心斯卡蒂':'辅助','凯尔希':'医疗','歌蕾蒂娅':'特种','异客':'术师',
        '灰烬':'狙击','夕':'术师','嵯峨':'先锋','空弦':'狙击','山':'近卫','迷迭香':'狙击','泥岩':'重装','瑕光':'重装','史尔特尔':'近卫',
        '森蚺':'重装','棘刺':'近卫','铃兰':'辅助','W':'狙击','温蒂':'特种','早露':'狙击','傀影':'特种','风笛':'先锋','刻俄柏':'术师',
        '年':'重装','阿':'特种','煌':'近卫','莫斯提马':'术师','麦哲伦':'辅助','赫拉格':'近卫','黑':'狙击','陈':'近卫','斯卡蒂':'近卫',
        '银灰':'近卫','塞雷娅':'重装','星熊':'重装','夜莺':'医疗','闪灵':'医疗','安洁莉娜':'辅助','艾雅法拉':'术师','伊芙利特':'术师',
        '推进之王':'先锋','能天使':'狙击',
        '幽灵鲨*':'近卫','羽毛笔*':'近卫',
    }

    # ban_operator = random.sample(operator_dict.keys(), 8)  # 随机一个字典中的key，第二个参数为限制个数
    pick_type = random.sample(feature,3)

    @classmethod
    def roll_1_operator(cls, operator_dict):
        pick_type = cls.pick_type
        ban_operator = []
        if '近卫' in pick_type:
            # 近卫特殊规则：只有两个职业
            pick = []
            if pick_type[0]!='近卫':
                pick.append(pick_type[0])
            else:
                pick.append(pick_type[1])
            pick.append('近卫')
            pick_type = pick # 更新职业表
                
            # 近卫干员名单
            blade = [];p=0
            for i in list(map(lambda x:x=='近卫',list(operator_dict.values()))):

                if i:
                    blade.append(list(operator_dict.keys())[p])
                p += 1
            for x in random.sample(blade, 3):
                ban_operator.append(x)
            
        if '术师' in pick_type:        
            # 术师干员名单
            magi = [];p=0
            for i in list(map(lambda x:x=='术师',list(operator_dict.values()))):

                if i:
                    magi.append(list(operator_dict.keys())[p])
                p += 1
            for x in random.sample(magi, 2):
                ban_operator.append(x)

        if '狙击' in pick_type:        
            # 狙击干员名单
            sniper = [];p=0
            for i in list(map(lambda x:x=='狙击',list(operator_dict.values()))):

                if i:
                    sniper.append(list(operator_dict.keys())[p])
                p += 1
            for x in random.sample(sniper, 2):
                ban_operator.append(x)
            
            
        if '重装' in pick_type:        
            # 重装干员名单
            tank = [];p=0
            for i in list(map(lambda x:x=='重装',list(operator_dict.values()))):
                if i:
                    tank.append(list(operator_dict.keys())[p])
                p += 1
            for x in random.sample(tank, 2):
                ban_operator.append(x)
            
            
        if '辅助' in pick_type:        
            # 辅助干员名单
            support = [];p=0
            for i in list(map(lambda x:x=='辅助',list(operator_dict.values()))):
                if i:
                    support.append(list(operator_dict.keys())[p])
                p += 1
            ban_operator.append(random.sample(support, 1)[0])
            
            
        if '医疗' in pick_type:        
            # 医疗干员名单
            healing = [];p=0
            for i in list(map(lambda x:x=='医疗',list(operator_dict.values()))):
                if i:
                    healing.append(list(operator_dict.keys())[p])
                p += 1
            ban_operator.append(random.sample(healing, 1)[0])
            
            
        if '特种' in pick_type:        
            # 特种干员名单
            special = [];p=0
            for i in list(map(lambda x:x=='特种',list(operator_dict.values()))):
                if i:
                    special.append(list(operator_dict.keys())[p])
                p += 1
            ban_operator.append(random.sample(special, 1)[0])


        if '先锋' in pick_type:        
            # 先锋干员名单
            pioneer = [];p=0
            for i in list(map(lambda x:x=='先锋',list(operator_dict.values()))):
                if i:
                    pioneer.append(list(operator_dict.keys())[p])
                p += 1
            ban_operator.append(random.sample(pioneer, 1)[0])

        return ban_operator




@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'#hw')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), DisableModule.require(module_name)],
    )
)
async def Dice(
    app: Ariadne, 
    message: MessageChain,
    group: Group,
    member: Member 
):
    ban_operator = Operator_rollbox.roll_1_operator(Operator_rollbox.operator_dict)
    out_text = ''
    if random.randint(0,2) == 0:
        a = list(Operator_rollbox.operator_dict.keys())
        for a1 in ban_operator:
            a.remove(a1)
        lucky = random.sample(a, 1)
        while(Operator_rollbox.operator_dict[lucky[0]] in Operator_rollbox.pick_type):
            lucky = random.sample(a, 1)
        
        out_text += '额外赠送的干员为：' + lucky[0] + '\n'
    out_text +='被ban的干员为：' + ", ".join(ban_operator) + '\n'
    out_text +='可用的职业为：' + ", ".join(Operator_rollbox.pick_type) + '\n'

    out_text +='--钢铁男儿左手窝窝屎右手砍口垒 群作业系统v2.0--' + '\n'
    out_text +='--p.s.33%几率出稀有奖励干员--' + '\n'
    await app.sendGroupMessage(group, MessageChain.create(
        Plain(out_text)
    ))