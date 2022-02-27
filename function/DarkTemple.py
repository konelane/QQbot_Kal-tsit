#! /usr/bin/env python3
# coding:utf-8

## 吾 即是M3 ##
## 中二完了想想怎么写……
# 关键词/检测库


import os
import random
import urllib

import requests
import story_xu as sx
from database.kaltsitReply import *
from graia.broadcast.utilles import printer

import function.squads_init as si
from function.adventure import TerraRogue
from function.CardSearch import CardSearch
from function.couplet import couplet_api
from function.ForcastForTricks import ForcastForTricks
from function.prts import Prts
from function.Signin import Signin
from function.StarCraftPVE import StarCraftPVE
from function.twotwoorder import TwoTwoOrder

# from function.Desk import kaltsitDesk

# 不触发功能的账号
blockID = [
    '1982751087', # 牛牛bot
    '1102108096','543361022' # 是傻逼
]



class Monster3:
    """关键词-功能 核心库"""
    def __init__(self,msg_info) -> None:
        """
        ----parameters----
        msg_info: 一些消息本身的属性字典【id等……
        space_cut_tokenizer: jieba分词的结果"""
        
        self.id = msg_info['id']
        self.text_list = msg_info['text_jieba']
        
        self.disappoint_text = [
            '老女人','谜语人','谜语','鹰语','猞猁','老妪','老太婆'
        ]
        self.meaning_less_text = [
            '好耶','哈哈哈哈哈哈哈','打牌','黑暗决斗' # 慎重添加出警词汇
        ]

        pass

    def __disappoint(self):
        """检查是否满足失望词"""
        
        return random.sample(disappoint_words,1)[0]

    def __meaning_less(self):
        """检查是否满足水群词"""
        
        return random.sample(repeat_words,1)[0]


    def check_words(self):
        """核心功能/暴露接口"""
        if self.id in blockID:
            return None


        a = [x for x in self.text_list if x in self.disappoint_text]
        # b = [x for x in self.text_list if x in self.w_cos_text]
        c = [x for x in self.text_list if x in self.meaning_less_text]
        output_words = []
        if len(a)!=0:
            output_words.append(self.__disappoint())
        # if len(b)!=0:
        #     output_words.append(self.__w_cos())
        if len(c)!=0:
            output_words.append(self.__meaning_less())
        
        return '\n'.join(x for x in output_words)



##################################################################################

class SweepSquad:
    """切分词检测库"""
    def __init__(self,msg_info) -> None:
        """msg_info是n维字典"""
        self.msg_info = msg_info
        self.id = msg_info['id']
        self.text_list = msg_info['text_split']
        


        # 词语配置
        self.repeat_mod = ['好耶','查杀','催更'] # 复读模块
        self.prts_text = ['#prts']
        self.praise_text = ['#praise']
        self.dnd_text = ['#读取','#初始化','#检定','#背包','#经验','.r']
        self.map_weather_text = ['#天气','#地图']
        self.couplet_text =  ['#对']
        self.cardSearch_text = ['#查卡']
        self.picBlindBox_text = ['#draw']
        self.adventure = ['#ad']
        self.starcraft = ['#sc']
        self.twotwo = ['22','#22']
        self.signin = ['#打卡','#签到']
        # self.driftingBottle_text = ['#捞', '#投']

        pass

    def checkWords(self):
        """功能核心激活函数"""
        if str(self.id) in blockID:
            return None, None
        
        
        
        if self.text_list[0] in self.repeat_mod:
            return self.__repeat(),None
        elif self.text_list[0] in self.prts_text:
            return self.__prts(),'random'
        elif self.text_list[0] in self.praise_text:
            text, at = self.__praise_()
            if at is not None:
                return text, at
            else:
                return text, None
        elif self.text_list[0] in self.dnd_text:
            return self.__dnd_kaltsit(), None
        elif self.text_list[0] in self.map_weather_text:
            return self.__map_weather(),'查询的天气大致如此'
        elif self.text_list[0] in self.couplet_text:
            return self.__coupletGet(), None
        elif self.text_list[0] in self.cardSearch_text:
            return self.__cardSearch(), None
        elif self.text_list[0] in self.picBlindBox_text:
            return self.__picBlindBox(),'picture'
        elif self.text_list[0] in self.adventure:
            return self.__adventure(), None
        elif self.text_list[0] in self.starcraft:
            return self.__starcraft(), None
        elif self.text_list[0] in self.twotwo:
            return self.__twotwoorder(), 'local_picture'
        elif self.text_list[0] in self.signin:
            return self.__signinImage(), 'local_picture2'
        # elif self.text_list[0] in self.driftingBottle_text:
        #     return self.__driftingBottle(), None


        else:
            return None,None

        pass

    def __repeat(self):
        """复读模块？"""
        if len(self.text_list) == 1:
            return self.text_list[0]
        else:
            return None

    def __prts(self):
        """prts查询功能"""
        prts_mod = ['技能专精','晋升材料','属性','后勤','生日','今日生日']
        exception_squad = ['凯尔希']
        if len(self.text_list)<= 2:
            return None
        if self.text_list[1] in exception_squad:
            return '我的情况由我自己判断，各位应该把注意力放在其他需要帮助的感染者身上。'
        if self.text_list[2] not in prts_mod:
            return None
        else:
            prts_1 = Prts(self.text_list[1])
            if self.text_list[2] == '技能专精':
                out_list = prts_1.MasteryMetarialGet()
            if self.text_list[2] == '晋升材料':
                out_list = prts_1.EliteMetarialGet()
            if self.text_list[2] == '属性':
                out_list = prts_1.AttributeGet()
            if self.text_list[2] == '后勤':
                out_list = prts_1.LogisticsSkill()
            if self.text_list[2] == '生日':
                out_list = '这位干员的生日是' + prts_1.BirthdayGet()
            if self.text_list[2] == '今日生日':
                out_list = prts_1.TodayBirthday()
        return ''.join(x for x in out_list)


    def __praise_(self):
        """夸夸功能"""
        d = None
        if (len(self.text_list) == 1):
            f = os.popen('python ./botqq/function/praise.py','r')
            d = f.read() 
            return d, None
        elif (len(self.text_list) == 2):
            f = os.popen('python ./botqq/function/praise.py','r')
            d = f.read() 
            return d, 'at' + self.text_list[1]


    def __dnd_kaltsit(self):
        """跑团"""
        # package_mod = ['增加','减少','使用','查询']

        if self.text_list[0] == '#读取':
            filename =  './botqq/' + self.text_list[0] + '_opt.txt'
            with open(filename, "r") as f:
                d = f.read()
            return d
        if self.text_list[0] == '#初始化':
            if len(self.text_list)!=6:
                return '初始化输入错误'
            else:
                create_opt = si.operator(self.text_list[1],self.text_list[2],self.text_list[3],self.text_list[4],self.text_list[5])
                create_opt.init_opt()
                # sleep(10)
                filename =  './botqq/' + self.text_list[1] + '_opt.txt'
                with open(filename, "r") as f:
                    d = f.read()
                return d
        if self.text_list[0] == '#检定':
            create_opt = si.operator(self.text_list[1],0,0,0,0)
            if len(self.text_list) == 4:
                # #检定 hehe agile 
                _point,_against = create_opt.against_action(self.text_list[2], skillful_ = self.text_list[3])
                return '主体检定值为：'+str(_point)+'\n客体豁免值为：'+str(_against)
            elif len(self.text_list) == 3:
                _point,_against = create_opt.against_action(self.text_list[2])
                return '主体检定值为：'+str(_point)+'\n客体豁免值为：'+str(_against)
            elif len(self.text_list)==5:
                against_opt = si.operator(self.text_list[4],0,0,0,0)
                _point,_against = create_opt.against_action(self.text_list[2], skillful_ = self.text_list[3], object_dict = against_opt.read_opt())
                return '主体检定值为：'+str(_point)+'\n客体豁免值为：'+str(_against)
            return None
        if self.text_list[0] == '#背包':
            create_opt = si.operator(self.text_list[1],0,0,0,0)
            if (self.text_list[2] == "增加"):
                create_opt.__update_opt__('package','增加'+self.text_list[3])
                filename =  './botqq/' + self.text_list[1] + '_opt.txt'
                with open(filename, "r") as f:
                    d = f.read()
            if (self.text_list[2] == "减少"):
                create_opt.__update_opt__('package','减少'+self.text_list[3])
                filename =  './botqq/' + self.text_list[1] + '_opt.txt'
                with open(filename, "r") as f:
                    d = f.read()
            if (self.text_list[2] == "使用"):
                create_opt.use_equip_package_change('use',self.text_list[3])
                
            if (self.text_list[2] == "查询"):
                create_opt.use_equip_package_change('lookup',self.text_list[3])
            return d
        if self.text_list[0] == '#经验':
            if len(self.text_list) == 3:
                create_opt = si.operator(self.text_list[1],0,0,0,0)
                create_opt.__update_opt__('exp','增加' + self.text_list[2])
                create_opt.opt_upgrade()
                exp_ = create_opt.read_opt()['exp']
                level_ = create_opt.read_opt()['level']
                return exp_,level_
            else:
                return None
        if self.text_list[0] == '.r':
            try:
                return sx.roll(self.text_list[1])
            except:
                return None


    def __map_weather(self):
        """地图 - 天气预报模块"""
        if self.text_list[0] not in ['#天气','#地图']:
            return
        if self.text_list[0] == '#地图':
            return '地图服务器在更新，博士或许可以试试更加古老的方式。'
            # 暂时关闭地图功能211101
            map = ForcastForTricks(self.msg_info)
            return map.orderToReturn()
        else:
            forcast = ForcastForTricks(self.msg_info)
            return forcast.orderToReturn()

    def __coupletGet(self):
        """对联功能"""
        if self.text_list[0] != '#对':
            return 
        else:
            temp = couplet_api(self.text_list[1])
            return temp.CoupletGet()
            

    def __cardSearch(self):
        """游戏王查卡功能"""
        if self.text_list[0] != '#查卡':
            return 
        else:
            textall = ' '.join([x for x in self.text_list[1::]]) # 空格连接
            temp = CardSearch(textall)
            return temp.cardTextReturn()
            

    def __picBlindBox(self):
        if self.text_list[0] != "#draw":
            return 
        else:
            link = requests.get(url = 'https://iw233.cn/api/Random.php').url
            
            return link


    def __adventure(self):
        if self.text_list[0] != '#ad':
            return 
        else:
            
            if len(self.text_list) == 1:
                temp = TerraRogue(init = True)
                temp.mapCreate()
                return temp.showMap()
            else:
                temp = TerraRogue(init = False)
                out_text = temp.answerSheet(str(self.text_list[1]))
            return out_text


    def __starcraft(self):
        if self.text_list[0] != '#sc':
            return 
        else:
            if len(self.text_list) == 1: # 即使用#sc查本周突变的
                temp = StarCraftPVE('下周突变')
                return temp.NextTubian()
            elif len(self.text_list[1])>2:
                temp = StarCraftPVE(self.text_list[1])
                out_text = temp.TubianSearch()
            else:
                temp = StarCraftPVE('第k周后的突变')
                out_text = temp.NextTubian(int(self.text_list[1])-1)
            return out_text


    def __twotwoorder(self):
        """22牌桌功能"""
        if self.text_list[0] not in ['22','#22']:
            return 
        else:
            temp = TwoTwoOrder(self.msg_info)
            return temp.checkOrder() # 图片地址
        

    def __signinImage(self):
        """打卡签到"""
        
        if self.text_list[0] not in ['#打卡','#签到']:
            return 
        else:
            temp = Signin(self.msg_info)
            outtext = temp.signinAction()
            # print(outtext)
            if (outtext is not None) and (outtext != ''):
                return (os.path.dirname(__file__) + '/signinImageGenerator/save_test.png', random.sample(signsuccesstext,1)[0]) # 之后可以加上随机生成
            elif outtext == '':
                return ('', random.sample(signinfailtext,1)[0])
            
            else:
                return ('', '出错了')



class SecretaryKaltsit:
    """私信秘书"""
    def __init__(self) -> None:
        pass



if __name__ == "__main__":
    msg2 = {
        'id':'591016144',
        'text_jieba': ['我','是','老女人']
    }
    msg3 = {
        'id':'591016144',
        'text_split': ['#prts','桃金娘','技能专精']
    }
    msg4 = {
        'id':'591016144',
        'text_split': ['#查卡','元素英雄','新星主']
    }
    # space_cut_tokenizer = ['我','是','老女人']
    # m3 = Monster3(msg2)
    # print(m3.check_words())

    # ss = SweepSquad(msg3)
    # print(ss.check_words())
    ss = SweepSquad(msg4)
    print(ss.cardSearch())
