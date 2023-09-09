#! /usr/bin/env python3
# coding:utf-8
from os.path import basename
import sys
import os
import re
sys.path.append(os.path.dirname(__file__))
import time

from core.decos import check_group, check_member, DisableModule, check_permitGroup
from core.ModuleRegister import Module
from core.MessageProcesser import MessageProcesser
from database.kaltsitReply import blockList
from modules.DiceKaltsit.dice import dice


from graia.ariadne.message.parser.twilight import RegexMatch
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At
from graia.ariadne.message.parser.twilight import Twilight
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

''' 
    dice from https://github.com/borntyping/python-dice
'''

channel = Channel.current()
module_name = basename(__file__)[:-3]

Module(
    name='DiceKaltsit',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.DiceKaltsit',
).register()



class DiceKaltsit:
    """凯尔希骰子
        1. 普通骰子([N]dS) 运算符取一个数量（N）和边数（S），并返回1到S之间的N个随机数的列表。
            例如：4d6可以返回[6，3，2，4]。使用a%作为第二个操作数是掷d100的简写，使用f是掷±1补正骰子的简写。
        2. 模糊骰子（[N]uS）操作符可以与骰子操作符互换，但使骰子的范围从-s到s，而不是1到s。这包括0。
        3. 野生骰子（[N]wS）掷骰子很特别。这一组中的最后一个掷骰子被称为“野骰子”。
            如果该骰子的投掷是最大值，则该组中第二高的投掷被设置为最大值。如果它的投掷最小，那么它和集合中的最高投掷都被设置为零。
            然后投掷另一个骰子。如果该辊再次为最小值，则所有骰子都设置为零。如果投掷单面野生骰子，则投掷行为与普通骰子类似。
            如果未指定N，则假定您要投掷单个骰子。d6等于1d6。
        4. 掷骰子可以使用x操作符进行分解，该操作符在给定阈值以上的每个掷骰子都会在集合中添加一个额外的骰子。
            如果没有给定阈值，则默认为最大可能投掷。如果额外的骰子超过这个阈值，它们会再次“爆炸”！保护措施已经到位，以防止这种情况导致解析器崩溃。
        5. 您可以使用r和rr运算符使解析器在某个阈值以下重新投掷骰子。单r品种允许新的投掷低于阈值，而双品种的投掷将投掷范围更改为阈值的最小值。阈值默认为最小投掷。
        6. 可以分别用（^或h）、（m或o）或（v或l）选择最高、中间或最低的投掷或列表条目。
            6d6^3将保持最高的3卷，而6d6v3将选择最低的3卷。如果未指定数字，则默认为除一个以外的所有数字表示最高和最低，除两个以外的其他数字表示中间。
            如果这些运算符的操作数为负值，则此操作将从结果中删除那么多元素。例如，6d6^-2将从集合中删除两个最低值，留下4个最高值。零没有效果。
        7. 分解运算符的一个变体是A（“再次”）运算符。该运算符不是重新投掷等于或大于阈值（或最大值）的值，而是将等于提供的阈值（或最小值）的数值加倍。
            如果未指定右侧操作数，则左侧必须是骰子表达式。
        8. 有两个操作符用于获取一组掷骰或数字，并计算达到或高于某个阈值的元素数，即“成功”。两者都需要右侧操作数作为阈值。第一个，e，只计算成功。第二个，f，计算成功减去失败的次数，这是当骰子元素的投掷为最小可能值时，或者列表为1时。
        9. 可以使用total(t)操作符将一个列表或一组卷转换为整数。6d1t将返回6而不是[1,1,1,1,1]。对投掷列表应用整数运算将自动对其进行总计。
        10. sort(s)可以使用排序操作符对一组骰子卷进行排序。4d6s不会改变返回值，但骰子将从最低到最高排序。
        11. +-运算符是投掷和列表集的特殊前缀。它否定了列表中的奇怪角色。示例：[1，2，3]->[-1，2，-3]。还有一个否定（-）操作符，用于单个元素、集合或投掷或列表。还有一个标识+运算符。
        12. 可以使用逐点加法（.+）和减法（.-）操作符从投掷列表或投掷集的每个元素中添加或减去值。例如：4d1.+3将返回[4,4,4]。
        13. 基本整数运算也可用：（16/8*4-2+1）%4->3。

    
        骰子入口命令.r
            .r nds [.+|.- 详细] [+f 单骰补正] [^x|hx 筛选x个最大值] [vx|lx 筛选x个最小值]
                [mx|ox 筛选x个中值] [s 排序输出] [t 计算总和]
    """
    def __init__(self, msg_info) -> None:
        '''初始化骰子'''
        # 保存用：
        self.dnd_msg = {
            "dm":"Kal'tsit"
            ,"dmID":591016144
            ,"pc":[]
            ,"rollID":[]  # 所有掷骰人id
            ,"group":msg_info['group_id']
            ,"create_time": time.strftime("%Y/%m/%d/ %p%I:%M:%S", time.localtime()) # 默认为当前时间
        }
        self.msg_info = msg_info
        self.expression = ''
        self.getText() # 更新字符
        pass
    
    def getText(self):
        ''' 将输入字符切分处理 '''
        if len(self.msg_info['text_split'])>=2:
            if self.msg_info['text_split'][-2] == 'ex':
                self.expression = self.msg_info['text_split'][-1]
                self.dice_text_input = ''.join(str(x) for x in self.msg_info['text_split'][:-1])
                print('1 ex:',self.dice_text_input)
            else:
                self.dice_text_input = ''.join(str(x) for x in self.msg_info['text_split'])
                print('1:',self.dice_text_input)
        else:
            self.dice_text_input = ''.join(str(x) for x in self.msg_info['text_split'])
            print('2:',self.dice_text_input)
    
    def basicOutput(self):
        '''输出骰子结果'''
        dice_text_input = self.dice_text_input
        if dice_text_input[:2] in ['.r', '#r']:
            dice_text_input=dice_text_input[2:]
            # print(dice_text_input)
        try:
            ans= dice.roll(dice_text_input)
            if type(ans) == dice.elements.Integer:
                return ans, [], 'out_val'
            elif len(list(ans))>1:
                return sum(list(ans)), list(ans), 'out_list'
        
        except:
            return 0, [], 'error'





@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'\.r.*|\#r.*').flags(re.X)])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
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

    dice_obj = DiceKaltsit(msg_info_dict) # 初始化骰子对象

    dice_tuple = dice_obj.basicOutput()
    
    if "help" in msg_info_dict['text_split']:
        if msg_info_dict['text_split'].index("help")==1:
            await app.send_group_message(group, MessageChain(
                Plain('掷骰指令为\n.r nds [.+|.- 详细骰值] [+f 单骰补正] [^x|hx 筛选x个最大值] [vx|lx 筛选x个最小值] [mx|ox 筛选x个中值] [s 排序输出] [t+f 计算总和+整体补正]')
            ))
    elif dice_tuple[2] == 'error':
        await app.send_group_message(group, MessageChain(
            Plain('掷骰指令有误。')
        ))
    elif dice_tuple[2] == 'out_val':
        outtext = '<'+msg_info_dict['name']+'>掷得的点数是：' + str(dice_tuple[0]) + '点。'
        await app.send_group_message(group, MessageChain(
            Plain(outtext)
        ))
    elif dice_tuple[2] == 'out_list':
        outtext = '<'+msg_info_dict['name']+'>各骰子掷得的点数是：' + '+'.join(str(x) for x in dice_tuple[1]) + '点。\n共计' + str(dice_tuple[0]) + '点。'
        await app.send_group_message(group, MessageChain(
            Plain(outtext)
        ))