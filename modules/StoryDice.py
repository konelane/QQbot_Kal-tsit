#! /usr/bin/env python3
# coding:utf-8
import pickle
import random
from os.path import basename
import os
import re

from core.config.BotConfig import BasicConfig
from core.decos import check_group, check_member, DisableModule, check_permitGroup
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
    story_dir = BasicConfig().databaseUrl + 'story'

    @classmethod
    def dice_t(cls, text='1d6'):
        """1d6"""
        out = []
        num, side = text.split('d')
        if int(num) >= 100:
            num = 100
        if int(side) >= 1000:
            side = 1000
        for i in range(int(num)):
            out.append(random.randint(1, int(side)))
        return out

    @classmethod
    def dice_basic(cls, msg_dict):
        """
        @param
            text_in : "1d100 + 7"
        """
        text_in = ' '.join(x for x in msg_dict['text_split'][1:])
        if 'd' not in text_in:
            return '',
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

    @classmethod
    def choice_maker(cls, msg_dict, group: Group):
        if msg_dict['text_split'][1] == 'new':
            path_in = cls.story_dir + f'/{group.id}_sw.pkl'
            if os.path.exists(path_in):
                return '群里已有一本随机议题。'

            set_story_name = ' '.join(x for x in msg_dict['text_split'][2:])
            story_dict = {'name': set_story_name, 'choice': []}
            pickle.dump(story_dict, open(path_in, 'wb'))
            return f'创建议题`{set_story_name}` 成功'

        if msg_dict['text_split'][1] == 'add':
            path_in = cls.story_dir + f'/{group.id}_sw.pkl'
            if not os.path.exists(path_in):
                return '博士，这群里并没有你说的那一本议题。'
            story_dict = pickle.load(open(path_in, 'rb'))
            story_dict['choice'].append(' '.join(x for x in msg_dict['text_split'][2:]))
            outtext = ''
            outtext += '关于问题`' + story_dict['name'] + '`经过会议讨论，共得到以下选择：'
            for i in range(len(story_dict['choice'])):
                outtext += '\n' + str(i + 1) + ' - ' + story_dict['choice'][i]

            pickle.dump(story_dict, open(path_in, 'wb'))

            return outtext

        if msg_dict['text_split'][1] == 'choice':
            path_in = cls.story_dir + f'/{group.id}_sw.pkl'
            if not os.path.exists(path_in):
                return '博士，这群里并没有你说的那一本手册。'
            story_dict = pickle.load(open(path_in, 'rb'))
            outtext = ''
            outtext += '关于问题`' + story_dict['name'] + '`经过会议讨论，共得到以下选择：\n'
            for i in range(len(story_dict['choice'])):
                outtext += str(i + 1) + ' - ' + story_dict['choice'][i] + '\n'

            choice_ans = random.randint(0, len(story_dict['choice']) - 1)
            outtext += f'罗德岛决策部门一致认为，应当选择{choice_ans + 1}号方案，' + '即`' + story_dict['choice'][
                choice_ans] + '`'

            os.remove(path_in)
            return outtext


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'\#s.*')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID),
                    check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def StoryWrite(
        app: Ariadne,
        message: MessageChain,
        group: Group,
        member: Member
):
    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()
    if msg_info_dict['text_split'][1] in ['new', 'add', 'choice']:
        outtext = StoryDice.choice_maker(msg_info_dict, group)
        if outtext != '':
            await app.send_group_message(group, MessageChain(
                Plain(outtext)
            ))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'\.r.*|\#r.*').flags(re.X)])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID),
                    check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def DiceOnly(
        app: Ariadne,
        message: MessageChain,
        group: Group,
        member: Member
):
    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()

    if msg_info_dict['text_split'][0] not in ['#r', '.r']:
        return
    else:
        out_put = StoryDice.dice_basic(msg_info_dict)
        if out_put != '' and len(out_put) == 2:
            dice_sum = sum(out_put[0]) + out_put[1]
            outtext = '骰子滚动后，你掷出了' + ','.join([str(x) for x in out_put[0]]) + '，以及额外的' + str(
                out_put[1]) + '点，共计' + str(dice_sum) + '点。'
            # TODO 大失败
            if sum(out_put[0]) <= 1:
                outtext += '\n看来，泰拉不相信骰子呢。'
            await app.send_group_message(group, MessageChain(
                Plain(outtext)
            ))
