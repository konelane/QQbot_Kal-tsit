#! /usr/bin/env python3
# coding:utf-8
from os.path import basename

from core.decos import check_group, check_member, DisableModule
from core.ModuleRegister import Module
from database.kaltsitReply import blockList

from graia.ariadne.message.parser.twilight import RegexMatch
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.twilight import Twilight
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema



channel = Channel.current()

module_name = basename(__file__)[:-3]

Module(
    name='Readme',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.Readme',
).register()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'#help')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), DisableModule.require(module_name)],
    )
)
async def Praise(
    app: Ariadne, 
    group: Group, 
):
    
    outtext = "博士，你好，我是Kal'tsit\n别紧张，我只是碰巧路过你的办公室。\n"
    outtext += '--最新更新于 22.03.21--\n'
    outtext += '功能查询https://konelane.github.io/QQbot_Kal-tsit/#/Guide'

    await app.sendGroupMessage(group, MessageChain.create(
        Plain(outtext)
    ))



