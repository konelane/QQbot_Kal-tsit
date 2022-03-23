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

'''骰子功能'''

channel = Channel.current()

module_name = basename(__file__)[:-3]

Module(
    name='StoryDice',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.StoryDice',
).register()

class StoryDice:
    @classmethod
    def dice_t(cls, text = '1d6'):
        '''1d6'''
        out = []
        num,side = text.split('d')
        for i in range(int(num)):
            out.append(random.randint(1,int(side)))
        return out


    @classmethod    
    def dice_basic(cls, msg_dict):
        text_in = ' '.join(x for x in msg_dict['text_split'][1:])
        if 'd' not in text_in:
            return ''
        diff_dice = 0
        if '+' in text_in:
            text_dice = text_in.split('+')[0]
            diff_dice = int(text_in.split('d')[1].split('+')[1])
        elif '-' in text_in:
            text_dice = text_in.split('-')[0]
            diff_dice = int(text_in.split('d')[1].split('-')[1]) * -1
        else:
            text_dice = text_in.split()[0]

        return cls().dice_t(text_dice), diff_dice




@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'.r')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), DisableModule.require(module_name)],
    )
)
async def Dice(
    app: Ariadne, 
    message: MessageChain,
    group: Group,
    member: Member 
):
    
    slightly_inittext = MessageProcesser(message,group,member)
    msg_info_dict = slightly_inittext.text_processer()
    dice_tuple = StoryDice.dice_basic(msg_info_dict)
    if dice_tuple[1] == 0:
        dice_sum = sum(dice_tuple[0])
        outtext = '你掷得的点数分别是：' + '+'.join(str(x) for x in dice_tuple[0]) + '。\n共计' + str(dice_sum) + '点。'
        await app.sendGroupMessage(group, MessageChain.create(
            At(member.id),
            Plain(outtext)
        ))
    elif dice_tuple[1] != 0:
        dice_sum = sum(dice_tuple[0]) + dice_tuple[1]
        outtext = '你掷得的点数分别是：' + '+'.join(str(x) for x in dice_tuple[0]) + '，以及额外的' + str(dice_tuple[1]) + '点。\n共计' + str(dice_sum) + '点。'
        await app.sendGroupMessage(group, MessageChain.create(
            At(member.id),
            Plain(outtext)
        ))


