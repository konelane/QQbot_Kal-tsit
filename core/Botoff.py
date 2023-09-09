import asyncio
from os.path import basename

from database.kaltsitReply import blockList
# from graia.ariadne import 
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import (  # RegexResult,; SpacePolicy,
    RegexMatch, Twilight)
from graia.ariadne.model import Friend, Group, Member, MemberPerm
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema

from core.decos import DisableModule
from core.ModuleRegister import Module

saya = Saya.current()
channel = Channel.current()
inc = InterruptControl(saya.broadcast)
module_name = basename(__file__)[:-3]

Module(
    name='Botoff',
    file_name=module_name,
    author=['KOneLane'],
    usage='core.Botoff',
    can_disable=False,
).register()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([
                RegexMatch(r'#bot退群')
            ])
        ]
    )
)
async def ask_to_leave_group(
        app: Ariadne,
        group: Group,
        member: Member
):
    """
    主动退群
    """
    print('[INFO]主动退群命令')
    if member.permission in [MemberPerm.Administrator, MemberPerm.Owner]:
        await app.send_group_message(group,MessageChain(f'Kal-tsit bot已退群。'),)
        await app.quit_group(group)


## 关闭功能
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([
                RegexMatch(r'#bot off')
            ])
        ],
        decorators=[DisableModule.require(module_name)],
    )
)
async def ask_to_close_for_a_day(
        app: Ariadne,
        group: Group,
        member: Member
):
    """
    主动关闭功能 - 一天
    """
    if member.permission in [MemberPerm.Administrator, MemberPerm.Owner]:
        print('[INFO]检测到功能关闭命令')
        await app.send_group_message(
            group,
            MessageChain(
                # f'我是 {basic_cfg.admin.masterName} 的机器人 {basic_cfg.botName}\n'
                f'改天。'
            ),
        )
        blockList.blockGroup.append(group.id)
        print(blockList.blockGroup)
        print(member.permission)
        return


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([
                RegexMatch(r'#bot on')
            ])
        ],
        decorators=[DisableModule.require(module_name)],
    )
)
async def ask_to_open(
        app: Ariadne,
        group: Group,
        member: Member
):
    # print(type(member.permission), member.permission)
    if member.permission in [MemberPerm.Administrator, MemberPerm.Owner]:
        blockList.blockGroup.remove(group.id)
        await app.send_group_message(
            group,
            MessageChain(
                # f'我是 {basic_cfg.admin.masterName} 的机器人 {basic_cfg.botName}\n'
                f'博士，我不在这一天，辛苦了。'
            ),
        )
