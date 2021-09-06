#! /usr/bin/env python3
# coding:utf-8

## 吾 即是M3 ##
## 中二完了想想怎么写……
# 关键词/检测库


import random
import os
from graia.broadcast.utilles import printer
from function.prts import Prts
import function.squads_init as si
from function.ForcastForTricks import ForcastForTricks
import story_xu as sx

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
            '老女人','谜语人','谜语','鹰语','猞猁'
        ]
        self.meaning_less_text = [
            "?",'好耶','哈哈哈哈哈'
        ]

        pass

    def __disappoint(self):
        """检查是否满足失望词"""
        repeat_words = [
            '博士，我原谅你的冒失，给你一次重新组织语言的机会。',
            '岁月与我，是相对静止的，不知你能否理解。',
            '夕惕若厉，则无咎矣。',
            '说出这种话来，博士大概需要恢复理智。',
            'M3，安静。',
            'M3，之后再亲近博士。',
            '博士，我听说古老的萨卡兹有一种将罪徒撕碎的刑罚。',
            '刚刚博士是不是说了什么，M3？',
            '……'
        ]
        return random.sample(repeat_words,1)[0]

    def __meaning_less(self):
        """检查是否满足水群词"""
        repeat_words = [
            'M3: (意义不明的嘶吼)',
            '进化的本质，人类的本质……',
            '不要吧时间浪费在我身上。',
            '虽然必要的休息是需要的，但你更需要专注于手上的任务。'
        ]
        return random.sample(repeat_words,1)[0]


    def check_words(self):
        """核心功能/暴露接口"""
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
        """msg_info是三维字典"""
        self.msg_info = msg_info
        self.id = msg_info['id']
        self.text_list = msg_info['text_split']
        pass

    def repeat(self):
        """复读模块？"""
        repeat_mod = ['？','?','好耶']
        if self.text_list[0] in repeat_mod:
            return self.text_list[0]
        else:
            return None

    def prts(self):
        """prts查询功能"""
        prts_text = ['#prts']
        prts_mod = ['技能专精','晋升材料','属性','后勤','生日']
        exception_squad = ['凯尔希']
        if self.text_list[0] in prts_text:
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
            return ''.join(x for x in out_list)
        else:
            return None

    def praise_(self):
        """夸夸功能"""
        praise_text = ['#praise']
        d = None
        if (len(self.text_list) == 1) & (self.text_list[0] in praise_text):
            f = os.popen('python ./botqq/function/praise.py','r')
            d = f.read() 
        return d

    def dnd_kaltsit(self):
        """跑团"""
        dnd_text = ['#读取','#初始化','#检定','#背包','#经验','.r']
        # package_mod = ['增加','减少','使用','查询']
        if self.text_list[0] in dnd_text:
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
        else:
            return None

    def map_weather(self):
        """地图 - 天气预报模块"""
        if self.text_list[0] not in ['#天气','#地图']:
            return
        if self.text_list[0] == '#地图':
            map = ForcastForTricks(self.msg_info)
            return map.orderToReturn()
        else:
            forcast = ForcastForTricks(self.msg_info)
            return forcast.orderToReturn()


    # def check_words(self):
    #     """核心功能/暴露接口"""
    #     a = self.__repeat()
    #     b = self.__prts()
    #     output_words = []
    #     if a:
    #         output_words.append(a)
    #     if b:
    #         output_words.append(b)    
    #     # if len(b)!=0:
    #     #     output_words.append(self.__w_cos())
        
    #     return ''.join(x for x in output_words)


if __name__ == "__main__":
    msg2 = {
        'id':'591016144',
        'text_jieba': ['我','是','老女人']
    }
    msg3 = {
        'id':'591016144',
        'text_split': ['#prts','桃金娘','技能专精']
    }
    # space_cut_tokenizer = ['我','是','老女人']
    # m3 = Monster3(msg2)
    # print(m3.check_words())

    ss = SweepSquad(msg3)
    print(ss.check_words())
