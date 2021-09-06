#! /usr/bin/env python3
# coding:utf-8

import os
from numpy.core.numeric import NaN
import pandas as pd
import random
import re

"""
    为bot的工具文件
    基于dnd4py的一些基础方法
    文件需要联网条件运行
"""


def roll(n):
    f = os.popen('roll ' + n,'r')
    d = f.read()
    print(d)
    return d

def lookup(type, name):
    if type:
        f = os.popen('lookup5e --' +type +' '+ name,'r')
    else:
        f = os.popen('lookup5e ' + name,'r')
    d = f.read()
    print(d)
    return d

def monster5e(name):
    f = os.popen('monster5e ' + name,'r')
    d = f.read()
    print(d)
    return d

def spell5e(name):
    f = os.popen('spell5e ' + name,'r')
    d = f.read()
    print(d)
    return d


def roll_born(key,k=1):
    """
        选择k个种族
        返回一个列表
    """
    df = pd.read_excel('./botqq/database.xlsx', sheet_name=key,header = 0)
    # print(df['种族'])
    if key == 'ethnic':
        listk = random.sample(list(df['种族']),k)
    elif key == 'gift':
        listk = random.sample(list(df['天赋']),k)
    elif key == 'identity':
        listk = random.sample(list(df['身份']),k)
    elif key == 'ideal':
        listk = random.sample(list(df['理想']),k)
    elif key == 'group':
        listk = random.sample(list(df['阵营']),k)
    elif key == 'bound':
        listk = random.sample(list(df['牵绊']),k)
    elif key == 'unique':
        listk = random.sample(list(df['特点']),k)
    elif key == 'shortcoming':
        listk = random.sample(list(df['缺点']),k)
    elif key == 'skill':
        listk = random.sample(list(df['技能']),k)
    elif key == 'skillful':
        listk = random.sample(list(df['熟练']),k)
    elif key == 'birthplace':
        listk = random.sample(list(df['出生地']),k) # .join(random.sample(list(df['细节']),k)) 
    # print(listk)
    return listk


def check_enthnic(name):
    """检验输入的种族名是否在数据库中【没卵用"""
    df = pd.read_excel('./botqq/database.xlsx', sheet_name='ethnic',header = 0)

    # print(name in list(df['种族']))
    return (name in list(df['种族']))


def ability_checks(
    input_:int = None,
    check = None,
    skillful_:int = None
    ):
    """
        检定
        = 未做特殊说明时，进行1d20的检定 + 关键属性调整值 + 熟练项加值
        __input 属性值【查询调整值
        skillful_ 有无熟练加值 【有的话请输入等级
        check 更换随机骰子，如 '3d8'
    """
    if not input_:
        # 计算调整值
        df = pd.read_excel('./botqq/database.xlsx', sheet_name='modifier',header = 0)
        i = 0
        while input_ > int(list(df['属性下限'])[i]):
            i += 1
        modified_point = int(list(df['调整值'])[i-1])
    else:
        modified_point = 0

    if not check:
        check_point = int(roll('1d20').split('*************')[1].split('Total:')[1])
    else:
        check_point = int(roll(str(check)).split('*************')[1].split('Total:')[1])

    if skillful_:
        print(skillful_)
        skillful_df = pd.read_excel('./botqq/database.xlsx', sheet_name='level',header = 0)
        skillful_point = int(skillful_df['熟练加值'][skillful_df['level']==int(skillful_)])
    else:
        skillful_point = 0
        
    ability_check_point = check_point + modified_point + skillful_point
    if check_point == 20:
        print('检定大成功')
    return ability_check_point

    

def defence_checks(
    input_:int = None,
    check = None,
    skillful_:int = None
    ):
    """
        对抗检定/豁免
        = 1d20随机值 + 属性调整值 + 熟练加值
        input_ 属性值【查询调整值
        skillful_ 有无熟练加值 【有的话请输入等级
        check 更换随机骰子，如 '3d8'
    """

    if not check:
        check_point = int(roll('1d20').split('*************')[1].split('Total:')[1])
    else:
        check_point = int(roll(str(check)).split('*************')[1].split('Total:')[1])

    # 属性调整值
    if not input_:
        df = pd.read_excel('./botqq/database.xlsx', sheet_name='modifier',header = 0)
        i = 0
        while input_ > int(list(df['属性下限'])[i]):
            i += 1
        modified_point = int(list(df['调整值'])[i-1])
    else:
        modified_point = 0

    # 熟练【如果有

    if skillful_:
        skillful_df = pd.read_excel('./botqq/database.xlsx', sheet_name='level',header = 0)
        skillful_point = int(skillful_df['熟练加值'][skillful_df['level']==skillful_])
    else:
        skillful_point = 0


    defence_check_point = check_point + modified_point + skillful_point
    return defence_check_point


        
def squads_roll(pick_type = None,pick_num = 1):

    """
        抽取pick_num位干员,根据职业pick六星干员，每种职业默认一个人
        现在不知道规则，先建立函数吧

        参数：
            pick_type: 职业，逗号分隔

        Usage demo:
            hehe_doc.squads_roll('近卫，先锋') # 逗号支持中英文

    """

    jobs = ['先锋','狙击','医疗','术师','近卫','重装','辅助','特种']
    operator_dict = {
        '浊心斯卡蒂':'辅助','凯尔希':'医疗','歌蕾蒂娅':'特种','异客':'术师','灰烬':'狙击','夕':'术师',
        '嵯峨':'先锋','空弦':'狙击','山':'近卫','迷迭香':'狙击','泥岩':'重装','瑕光':'重装',
        '史尔特尔':'近卫','森蚺':'重装','棘刺':'近卫','铃兰':'辅助','W':'狙击','温蒂':'特种',
        '早露':'狙击','傀影':'特种','风笛':'先锋','刻俄柏':'术师','年':'重装','阿':'特种',
        '煌':'近卫','莫斯提马':'术师','麦哲伦':'辅助','赫拉格':'近卫','黑':'狙击','陈':'近卫',
        '斯卡蒂':'近卫','银灰':'近卫','塞雷娅':'重装','星熊':'重装','夜莺':'医疗','闪灵':'医疗',
        '安洁莉娜':'辅助','艾雅法拉':'术师','伊芙利特':'术师','推进之王':'先锋','能天使':'狙击',
        '幽灵鲨':'近卫'
    }
    if not pick_type:
        pick_type = random.sample(jobs,pick_num)
    else:
        pick_type = re.sub(',','，',pick_type)
        pick_type = pick_type.split('，') # 支持中英文逗号分隔
        print(pick_type)

    opt_list = []
    
    for type in pick_type:
        p=0;type_opt_all = []
        # 根据职业pick六星干员，每种职业一个人
        for i in list(map(lambda x:x==type,list(operator_dict.values()))):
            if i:
                type_opt_all.append(list(operator_dict.keys())[p])
            p += 1
        opt_list.append(random.sample(type_opt_all, 1)[0])

    return opt_list


def check_normal(__dict,check_type,single_item = None):
    """
        在一项行为后，检查所有变动
        如检查经验值，武器数据，天赋数据等……
        参数：
            __dict 参数字典【文档
            check_type 检查类型
    """
    data_file = 'C:/Users/ASUS/botqq/database.xlsx'
    # 查询经验值是否升级，并返回等级
    if check_type=='exp':
        key_ = 'exp'
        exp_df = pd.read_excel(data_file, sheet_name='level',header = 0)
        if __dict[key_]:
            i = 0
            while int(exp_df['exp'][i]) < int(__dict[key_]):
                i += 1
            return int(exp_df['level'][i-1])
        else:
            return 0

    # 检查升级的成长点数
    elif check_type == 'upgrade':
        key_ = 'occupation'
        occupation = pd.read_excel(data_file, sheet_name='occupation',header = 0)
        upgrade_list = occupation[occupation['职业']==__dict[key_]]
        return upgrade_list

    # 查询背包的武装信息
    elif check_type == 'package_equipment':
        key_ = 'package'
        equipment_df = pd.read_excel(data_file, sheet_name='equipment',header = 0)
        pac_equ_message = {}
        for item in __dict[key_]:
            if item in list(equipment_df['物品']):
                pac_equ_message[item] = equipment_df[equipment_df['物品']==item]

        return pac_equ_message
    
    # 查询装备的武装信息
    elif check_type == 'equiped_equipment':
        key_ = 'package'
        equipment_df = pd.read_excel(data_file, sheet_name='equipment',header = 0)
        equ_equ_message = {}
        for item in __dict[key_]:
            if item in list(equipment_df['物品']):
                equ_equ_message[item] = equipment_df[equipment_df['物品']==item]

        return equ_equ_message    

    # 背包的物品
    elif check_type == 'items':
        key_ = 'package'
        items_df = pd.read_excel(data_file, sheet_name='items',header = 0)
        item_message = {}
        for item in __dict[key_].keys():
            if item in list(items_df['物品']):
                item_message[item] = items_df[items_df['物品']==item]

        return item_message

    if (check_type =='single_item'):
        """只支持查道具"""
        items_df = pd.read_excel(data_file, sheet_name='items',header = 0)
        item_message = items_df[items_df['物品']==single_item]

        return item_message


def activate(item):
    """
        启动某种效果【没想好，打算等装备database建立完成再写，或许还需要对每个物品搞一个方法
        激活字典里的activate的值
        装备效果：常驻/状态激活
        物品效果：常驻/使用激活
    """
    print('触发',item,'的效果')

    pass

def equip(equipment):
    """
        目前的想法：
        装备前需要 
        1.鉴定，
        2.检查属性是否合格
        3.检查原位置有无同类装备，是否矛盾，更换装备
        4.宣告装备并触发效果
    """
    print('装备了',equipment)
    # activate(equipment)
    pass

def condition_change(condition_opt):
    """
        即时效果与触发式效果检查
    """
    for condition in condition_opt:
        activate(condition)
    pass


if __name__ == "__main__":
    # roll('3d8 + 1d6 + 10')
    # monster5e('goblin')
    # spell5e('fireball')
    # roll_enthnic(1)
    # check_enthnic('鲁珀')
    # ability_checks(15,'3d8')
    # ability_checks(15)
    pass