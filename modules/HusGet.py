#男老婆

import random
import sqlite3
from os.path import basename
from uuid import uuid4

from core.decos import DisableModule, check_group, check_member, check_permitGroup
from core.MessageProcesser import MessageProcesser
from core.ModuleRegister import Module
from database.kaltsitReply import blockList, text_table
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, Plain
from graia.ariadne.message.parser.twilight import RegexMatch, Twilight
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()

module_name = basename(__file__)[:-3]

Module(
    name='HusGet',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.HusGet',
).register()



class HusGet:

    def __init__(self, msg_out) -> None:
        self.filename = './bot/database/' # 数据库位置
        self.signin_box = {
            'id':msg_out['id'],
            'signin_uid':str(uuid4()),
            'name': msg_out['name'],
            'exp':0,
            'total_days':0,
            'consecutive_days':0,
            'is_signin_consecutively':0,
            'reliance':0,
            'credit':0,
            'last_signin_time': "2021/05/12-12:00:00",
            # 'already_signin':0,

            'group_id':msg_out['group_id'],
            'text_ori':msg_out['text_ori'],
            'signin_new_name': msg_out['name'],
        }
        self.TableHeader = [
            'id','signin_uid','name','exp','total_days','consecutive_days',
            'is_signin_consecutively','reliance','credit','last_signin_time',#'already_signin'
        ]


    done_opt = ['银灰','赫拉格','异客','傀影','棘刺','极境','阿','灵知']
    husband_wife_dict = {
        
        '银灰':{
            'name':'银灰',
            'level':'6',
            'occu':'近卫',
            'location':'谢拉格',
            # 'organization':'',
            'reply':{
                0:'你与我的关系高于公司往来，并且我也很乐意与你相处。',
                0:'或许，我们该约一个时间出去聊聊。哪怕仅仅小酌一杯，罗德岛的饮品如何？',
                1:"对感染者，我们看法一致，盟友。我很高心与你站在同一战线。",
                1:'前……前夫是什么称呼，我的盟友，你应该做一些企业文化方面的管理了，对么？',
                2:'练尽一车谱，棋道狂几人。俯仰一世天地间，只有你与我共弈一局。',
                2:'嗯？你说凯尔希这周出外勤？我明白了，盟友。',
                2:'我的利刃，会永远为你而挥。这不是我们之间的契约，我也甘愿被你欺骗。尽情使用我的力量吧。',
            },
        },

        '赫拉格':{
            'name':'赫拉格',
            'level':'6',
            'occu':'近卫',
            'location':'乌萨斯',
            # 'organization':'',
            'reply':{
                0:'胜地不常，盛筵难再。多少旧友，一去不回。举杯吧博士，愿我们都有强大的身心。',
                0:'比起现代科技，我更信任“降斩”。它主人的牺牲绝非无谓。',
                1:'博士，我会保护你……不论是乌萨斯，还是别的什么，都休想。',
                1:'出色的表现，我还以为你没有见过真正的战争。',
                2:'不求同年同月同日生，但求……博士，为什么不让我说下去？',
                2:'罗德岛和你总是远离目光，我也一样。但至少此刻，让我好好看看你，博士。',
                2:'愿你自由地生活下去，博士。这是我平凡的愿望。',
                2:'或许有一天你能真正结束我们的痛苦。博士，来吧，向我下令！',
                2:'想吃点心？我这里还剩一些。小心蛀牙。'
            },
        },

        '异客':{
            'name':'异客',
            'level':'6',
            'occu':'术师',
            'location':'哥伦比亚',
            # 'organization':'',
            'reply':{
                0:'现在，我们的布局天衣无缝。',
                0:'这些机械……我无法对他们倾注情感……突然回忆起很多事，抱歉。',
                1:'在罗德岛的这些日子，我了解了很多。我只是好奇，凯尔希怎么一点变化都没有？',
                1:'我痛恨萨尔贡的黄沙和那里的一切，一直都是。',
                2:'博士，你说凯尔希要和我聊聊？嗯？原来是你找我吗博士？',
                2:'你们这群家伙别老是把角色和声优关联到一起！',
                2:'要我念这个？……首先，是犯下傲慢之罪的凯尔希，于是神，降下了祂的惩罚。客门……这是什么东西？',
                2:'我不知道我的家乡在何处。只有博士在我身边，我……才有余裕整理自己。',
            },
        },

        '傀影':{
            'name':'傀影',
            'level':'6',
            'occu':'特种',
            'location':'维多利亚',
            # 'organization':'',
            'reply':{
                0:'放心博士，我没有对你出手的理由，相反的，我想保护你。',
                0:'……我无意开口，希望你了解我的心意。',
                1:'如果有人找我，博士你可以做出判断。你知道怎么叫我。',
                1:'希望有一天，我能坦然面对自己的悲剧。',
                2:'博士，Miss.Christine托我给你带了摸摸券……女士很喜欢你。',
                2:'喜剧，悲剧，悲喜剧……随便怎么比喻，生活都不会',
                2:'舞台幕后，是整个剧团最精彩的地方。',
                2:'即使现在并非黑夜，黑夜也不曾离开你的身边。小心那些不合时宜的睡意，博士。',
            },
        },

        '棘刺':{
            'name':'棘刺',
            'level':'6',
            'occu':'近卫',
            'location':'伊比利亚',
            # 'organization':'',
            'reply':{
                0:'看仔细，这才是伊比利亚的最高之术！两只老虎爱跳舞~小兔子乖乖拔萝卜……',
                0:'保养武器？我的武器颜色总被人误会，所以我只好拜托工匠师傅们常换点颜色。',
                1:'博士，谢谢你来甲板救我。旁边那个傻瓜可以让他再挂一会。',
                1:'一硫二硝三木炭，每个加工站工作人员都应该知道的魔法配方。',
                2:'博士，你说我的肤色？哈，这可是伊比利亚人骄傲的健康黑麦色！',
                2:'嘿~哟~带着诡异的面罩，藏起诡计的嵌套~恶灵挣脱了镣铐，为战争带来……烧烤……唔，押的不好，重来重来……',
                2:'博士，我又买了三十套一模一样的衬衫，要不要分你几套？',
                2:'我个人的小小建议，如果能从罗德岛中删除一个红毛挑染黎博利，就能保持世界和平了呢。',
            },
        },

        '极境':{
            'name':'极境',
            'level':'5',
            'occu':'先锋',
            'location':'伊比利亚',
            # 'organization':'',
            'reply':{
                0:'我觉得有时一个人的帅气是挡不住的，博士你也这么认为？我还以为你在蓝门什么都能挡……',
                0:'什么人会把旗子当做武器啊！旗子就是用来挥舞的不是么？',
                1:'那个小姐叫什么来着……啊，惊蛰？我刚刚喝的那杯奶茶上似乎有这个名字……难道这就是她热情似火追了我五层楼的原因？',
                2:'每当想起我的故乡，总让我无比怀念。我们终究要面对那个地方，对么博士？',
                2:'棘刺和我开发了一套强身健体的广播操，可以充分活动腰部的肌肉，久坐人士的福音！我教你做吧博士！',
                2:'博士，我知道你很忙，但是你应该抽时间理发的，我把推子和剪刀都带来了……为什么不理我？',
                2:'每当想起我的故乡，总让我无比怀念。我们终究要面对那个地方，对么博士？',
            },
        },

        '阿':{
            'name':'',
            'level':'6',
            'occu':'特种',
            'location':'',
            # 'organization':'',
            'reply':{
                0:'博士，不管大病小病我都能治，如果你有什么不方便的病……你懂得~我这里给您开良心价！',
                0:'新口味的试剂该找谁测试呢？啊，博士那个不能喝哦，身体可能会融化的。',
                1:'真羡慕凯尔希，能独享你的治疗诊断权，博士。',
                2:'我不会亏了你的信用点的博士，总算能做点想做的事啦，你会同意的吧博士。',
            },
        },

        '山':{
            'name':'',
            'level':'6',
            'occu':'近卫',
            'location':'',
            # 'organization':'',
            'reply':{
                0:'',
                1:'',
                2:'',
            },
        },

        '乌有':{
            'name':'乌有',
            'level':'5',
            'occu':'特种',
            'location':'',
            # 'organization':'',
            'reply':{
                0:'',
                1:'',
                2:'',
            },
        },

        '老鲤':{
            'name':'',
            'level':'6',
            'occu':'特种',
            'location':'',
            # 'organization':'',
            'reply':{
                0:'',
                1:'',
                2:'',
            },
        },

        '灵知':{
            'name':'灵知',
            'level':'6',
            'occu':'辅助',
            'location':'',
            # 'organization':'',
            'reply':{
                0:'嗯，这柄短剑是给你的博士，我借用了工坊，这里的技术值得我学习。',
                0:'做错了就是做错了，多余的辩解只会徒增交流的成本。',
                1:'博士想知道我的看法？这需要很长时间来解说，你有耐心听完吗？没别的意思，我只是确认一下。',
                1:'我的个人情感在工作中没有那么重要。我也不想参与任何莫名其妙的“心理疏导会”……博士也同意吗？',
                2:'博士，你也觉得我有些难以相处吗？这些，这些都增加了沟通的损耗，我会调整的。',
                2:'嗯？问我以什么态度面对家乡？唔，我从来不考虑这些问题。只要做的事能够让那里好起来，其他就没那么重要了。',
                2:'你把太多时间放在了与研究无关的杂务上，博士。身为研究者，你应该明白，这只会阻碍你前进的脚步。',
                2:'看来你对自己身体的管理有所欠缺，博士。',
            },
        },

        '':{
            'name':'',
            'level':'6',
            'occu':'近卫',
            'location':'',
            # 'organization':'',
            'reply':{
                0:'',
                1:'',
                2:'',
            },
        },

        '':{
            'name':'',
            'level':'6',
            'occu':'近卫',
            'location':'',
            # 'organization':'',
            'reply':{
                0:'',
                1:'',
                2:'',
            },
        },

        '':{
            'name':'',
            'level':'6',
            'occu':'近卫',
            'location':'',
            # 'organization':'',
            'reply':{
                0:'',
                1:'',
                2:'',
            },
        },


    }

    @classmethod
    def roll_box(cls):
        opt_choice = random.choice(cls.done_opt)
        reply_hus = random.choice(list(cls.husband_wife_dict[opt_choice]['reply'].values()))
        return opt_choice, reply_hus


    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return (con,cur)



    def __dataSave(self):
        """保存当前用户数据 - se图功能魔改版"""
        con,cur = self.__connectSqlite()
        cur.execute(f"REPLACE INTO `signin` ( id, signin_uid, name, exp, total_days, consecutive_days, \
            is_signin_consecutively, reliance, credit, last_signin_time) VALUES(?,?,?,?,?,?,?,?,?,?)",(
            self.signin_box['id'], self.signin_box['signin_uid'],  self.signin_box['name'], self.signin_box['exp'], \
            self.signin_box['total_days'], self.signin_box['consecutive_days'], self.signin_box['is_signin_consecutively'], \
            self.signin_box['reliance'], self.signin_box['credit'], self.signin_box['last_signin_time']
            )
        )
        con.commit()
        con.close()
        pass


    def __searchSigninData(self):
        dict_of_text = None
        con,cur = self.__connectSqlite()
        try:
            cur.execute("SELECT * FROM `signin` WHERE id = ? ",(self.signin_box['id'],))
            test = list(cur.fetchall()[0])

            dict_of_text = dict(zip(self.TableHeader, test))
        except:
            print('未查到记录')
        finally:
            con.commit()
            con.close()

        return dict_of_text


    def zhibanAction(self):
        """值班功能入口"""
        if self.signin_box['text_ori'] in ["#值班"]:
            # 1.查询信用值
            dict_of_text = self.__searchSigninData()
            if dict_of_text is not None:
                """根据查询得到的字典更新数据"""
                self.signin_box.update(dict_of_text)
            else:
                return ''

            # 2.向DarkTemple返回指令
            if self.signin_box['credit'] >= 3:
                self.signin_box['credit'] -= 3
                self.__dataSave()
                return 'work'
            else:
                return '博士，信用不足，自己值班。'


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'#值班')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def Praise(
    app: Ariadne, 
    group: Group, 
    message: MessageChain,
    member: Member
):
    

    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()   

    if msg_info_dict['text_split'][0] not in ['#值班']:
        return 
    else:
        temp = HusGet(msg_info_dict)
        outtext = temp.zhibanAction()
        if outtext == 'work':
            hus_opt, hus_reply= HusGet.roll_box()
            reply_text = '今日值班干员：' + hus_opt + '\n' + hus_reply
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(reply_text)
            ]))
        elif outtext == '':
            await app.sendGroupMessage(group, MessageChain.create([
                Plain('干员薪资都发不起，自己去打卡上班。')
            ]))

        else:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(outtext)
            ]))
