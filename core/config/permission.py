#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
权限即黑名单检查

移植自 Xenon：https://github.com/McZoo/Xenon/blob/master/lib/control.py
"""

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.model import Group, Member, MemberPerm
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend

from core.config.BotConfig import RConfig, basic_cfg


class PermConfig(RConfig):
    __filename__: str = 'permission'
    group_whitelist: list = []
    user_blacklist: list = []


perm_cfg = PermConfig()


class GroupPermission:
    """
    用于管理权限的类，不应被实例化

    适用于群消息和来自群的临时会话
    """

    BOT_MASTER: int = 100  # Bot主人
    BOT_ADMIN: int = 90  # Bot管理员
    OWNER: int = 30  # 群主
    ADMIN: int = 20  # 群管理员
    USER: int = 10  # 群成员/好友
    BANED: int = 0  # Bot黑名单成员
    DEFAULT: int = USER

    _levels = {
        MemberPerm.Member: USER,
        MemberPerm.Administrator: ADMIN,
        MemberPerm.Owner: OWNER,
    }

    @classmethod
    async def get(cls, target: Member) -> int:
        """
        获取用户的权限等级

        :param target: Friend 或 Member 实例
        :return: 等级，整数
        """
        if target.id == basic_cfg.admin.masterId:
            return cls.BOT_MASTER
        elif target.id in basic_cfg.admin.admins:
            return cls.BOT_ADMIN
        elif isinstance(target, Member):
            return cls._levels[target.permission]
        else:
            return cls.DEFAULT

    @classmethod
    def require(
        cls,
        perm: int = MemberPerm.Member,
        send_alert: bool = True,
        alert_text: str = '你没有权限执行此指令',
    ) -> Depend:
        """
        群消息权限检查

        指示需要 `level` 以上等级才能触发

        :param perm: 至少需要什么权限才能调用
        :param send_alert: 是否发送无权限消息
        :param alert_text: 无权限提示的消息内容
        """

        async def wrapper(app: Ariadne, group: Group, member: Member):
            if group.id not in perm_cfg.group_whitelist or member.id in perm_cfg.user_blacklist:
                raise ExecutionStop()
            if isinstance(perm, MemberPerm):
                target = cls._levels[perm]
            elif isinstance(perm, int):
                target = perm
            else:
                raise ValueError('perm 参数类型错误')
            if (await cls.get(member)) < target:
                if send_alert:
                    await app.sendMessage(group, MessageChain.create(At(member.id), Plain(' ' + alert_text)))
                raise ExecutionStop()

        return Depend(wrapper)
