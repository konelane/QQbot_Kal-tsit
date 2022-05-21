# 权限
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
# from graia.ariadne.event.message import FriendMessage, GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, Plain
from graia.ariadne.model import Group, Member
# from graia.ariadne.util import await_predicate
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.exceptions import ExecutionStop

from config.BotConfig import modules_cfg

# from core.MessageProcesser import MessageProcesser


# 权限装饰器
def check_group(*groups):
    async def check_group_deco(app: Ariadne, group: Group):
        if group.id in groups[0]:
            # await app.sendGroupMessage(group, MessageChain.create("对不起，该群并不能发涩图"))
            print('[INFO]权限不足-群组被封禁')
            raise ExecutionStop
    return Depend(check_group_deco)


def check_member(*members):
    async def check_member_deco(app: Ariadne, group: Group, member: Member):
        if member.id in members[0]:
            print('[INFO]权限不足-ID被封禁')
            # await app.sendGroupMessage(group, MessageChain.create(At(member.id), "对不起，您的权限并不够"))
            raise ExecutionStop
    return Depend(check_member_deco)

# 文本检查装饰器
def check_plain(*message):
    async def check_message_is_plain(app: Ariadne, message: MessageChain):
        # 触发bot的先决条件 有文本
        if not message.has(Plain):
            print('消息不含文字')
            raise ExecutionStop
    return Depend(check_message_is_plain)



class DisableModule:
    """
    用于管理模块的类，不应该被实例化
    """

    @classmethod
    def require(cls, module_name: str) -> Depend:
        def wrapper(event: Dispatchable):
            if module_name in modules_cfg.globalDisabledModules:
                raise ExecutionStop()
            elif isinstance(event, GroupMessage) and module_name in modules_cfg.disabledGroups:
                if event.sender.group.id in modules_cfg.disabledGroups[module_name]:
                    raise ExecutionStop()

        return Depend(wrapper)
