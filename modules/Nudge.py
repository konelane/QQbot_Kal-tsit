#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from posixpath import basename
from random import uniform

from graia.ariadne.app import Ariadne
from graia.ariadne.event.mirai import NudgeEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain, Poke, PokeMethods 
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.ariadne.model import Group, Member

from core.config.BotConfig import basic_cfg
from core.decos import DisableModule
from core.ModuleRegister import Module


channel = Channel.current()
module_name = basename(__file__)[:-3]

Module(
    name='Nudge',
    file_name=module_name,
    author=['KOneLane'],
    usage='module.Nudge',
).register()

msg = [
    '别{}啦别{}啦，无论你再怎么{}，我也不会多说一句话的~',
    '你再{}！你再{}！你再{}试试！！',
    '那...那里...那里不能{}...绝对...绝对不能（小声）...',
    '那里不可以...',
    '怎么了怎么了？发生什么了？！纳尼？没事？没事你{}我干哈？',
    '气死我了！别{}了别{}了！再{}就坏了呜呜...┭┮﹏┭┮',
    '呜…别{}了…',
    '呜呜…受不了了',
    '别{}了！...把手拿开呜呜..',
    'hentai！八嘎！无路赛！',
    '変態！バカ！うるさい！',
    '。',
    '哼哼╯^╰',
]




@channel.use(ListenerSchema(listening_events=[NudgeEvent], decorators=[DisableModule.require(module_name)]))
async def Nudge(app: Ariadne, event: NudgeEvent):
    if event.target != basic_cfg.mah_cfg.account:
        return
    # elif not ManualInterval.require(f'{event.supplicant}_{event.group_id if event.friend_id is not None else None}', 3):
    #     return
    # await asyncio.sleep(uniform(0.2, 0.6))
    try:
        await app.sendNudge(event.supplicant, event.group_id)  # 当戳一戳来自好友时 event.group_id 为 None，因此这里不判断也可以
        await asyncio.sleep(uniform(0.2, 0.6))
        if event.context_type == "group":
            await app.sendGroupMessage(event.group_id, MessageChain.create(
                Poke(event.supplicant) # PokeMethods.ChuoYiChuo
            ))
    except Exception:  
        pass
