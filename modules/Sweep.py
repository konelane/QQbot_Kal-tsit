import random
from os.path import basename

from core.decos import check_group, check_member, DisableModule
from core.ModuleRegister import Module
from core.MessageProcesser import MessageProcesser
from database.kaltsitReply import disappoint_words, repeat_words, blockList
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.twilight import RegexMatch, Twilight, UnionMatch
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema



channel = Channel.current()

module_name = basename(__file__)[:-3]
Module(
    name='Sweep',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.Sweep',
).register()



class Sweep:
    """关键词-功能 核心库"""
    


    def __init__(self,msg_info) -> None:
        """
        ----parameters----
        msg_info: 一些消息本身的属性字典【id等……
        space_cut_tokenizer: jieba分词的结果"""

        self.disappoint_text = [
            '老女人','谜语人','谜语','鹰语','猞猁','老妪','老太婆'
        ]
        self.meaning_less_text = [
            '哈哈哈哈哈哈哈','打牌','黑暗决斗' # 慎重添加出警词汇
        ]

        self.msg_info = msg_info
        self.text_ori = msg_info['text_ori'] # 消息原始文本

        pass

    def __disappoint(self):
        """检查是否满足失望词"""
        
        return random.sample(disappoint_words,1)[0]

    def __meaning_less(self):
        """检查是否满足水群词"""
        return random.sample(repeat_words,1)[0]


    def check_words(self):
        """核心功能/暴露接口"""
        print(self.text_ori)
        disappoint_reply = [x for x in self.disappoint_text if x in self.text_ori]
        meaning_less_reply = [x for x in self.meaning_less_text if x in self.text_ori]
        output_words = []
        if len(disappoint_reply)!=0:
            output_words.append(self.__disappoint())
        if len(meaning_less_reply)!=0:
            output_words.append(self.__meaning_less())
        
        return '\n'.join(x for x in output_words)




@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([
            RegexMatch('.*老女人|.*谜语|.*鹰语|.*猞猁|.*老妪|.*老太婆|.*哈哈哈哈哈哈哈|.*打牌|.*黑暗决斗')                                 # ,'谜语',
        ])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), DisableModule.require(module_name)],
    )
)
async def SweepSquad(
    app: Ariadne, 
    group: Group, 
    message: MessageChain,
    member: Member
):
    
    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()

    sweep_obj = Sweep(msg_info_dict)
    sweep_text = sweep_obj.check_words()

    if sweep_text is not None:
        print(sweep_text)
        await app.sendGroupMessage(group, MessageChain.create([
            Plain(sweep_text)
        ]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([
            RegexMatch(r'好耶')                                 
        ])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), DisableModule.require(module_name)],
    )
)
async def Repeat(
    app: Ariadne, 
    group: Group, 
    message: MessageChain,
    member: Member
):
    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()
    if msg_info_dict['text_ori'] == '好耶':
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('好耶')
        ]))