#! /usr/bin/env python3
# coding:utf-8

## 初始化角色
## 对角色各项属性进行初始化，并且建立初始化角色文档及其读写接口

import os

# from numpy.core.einsumfunc import _optimal_path
import story_xu as sx
import random 
import re


class doctor:
    """刀客塔生成器V1.0.1"""

    """
        最后修改时间2021年5月22日
        编辑人员：氦核
        介绍：建立初始属性，依次填写姓名，魅力，敏捷，体质，智力

        init_doctor函数:生成/覆盖文本，请勿轻易使用 # 实装前设置权限
        read_doctor函数:读取博士文件
        squads_recruit函数:roll指定职业干员，默认1人
        usage demo:
            hehe_doc = doctor('hehe',0,0,0,0)
            hehe_doc.init_doctor()
            hehe_doc.read_doctor()
            hehe_doc.squads_recruit('近卫，先锋',) # 逗号支持中英文

    """
    def __init__(
        self,name,charm_init,agile_init,strength_init,intelligence_init
        ) -> None:
        self.name = name
        self.charm_init = charm_init
        self.agile_init = agile_init
        self.strength_init = strength_init
        self.intelligence_init = intelligence_init
        self.filename = '.\\botqq\\' + self.name + '_doc.txt'
        pass

    def write_doc(self,doc_dict):
        with open(self.filename, 'w') as f:
            f.write('**********\n')
            f.write('doctor_name|'+doc_dict['doctor_name']+ '|\n')
            f.write('charm|'+      str(doc_dict['charm']) + '|\n')
            f.write('agile|'+      str(doc_dict['agile'])+ '|\n')
            f.write('strength|'+   str(doc_dict['strength'])+ '|\n')
            f.write('intelligence|'+str(doc_dict['intelligence'])+ '|\n')
            f.write('sanity|'+     str(doc_dict['sanity'])+ '|\n')
            f.write('LMB|'+        str(doc_dict['LMB'])+ '|\n')
            f.write('package|'+    str(doc_dict['package'])+ '|\n')
            f.write('squad|'+      str(doc_dict['squad'])+ '|\n')
            f.write('exp|'+        str(doc_dict['exp'])+ '|\n')
            f.write('Level|'+      str(doc_dict['Level'])+ '|\n')
            f.write('**********\n')



    def init_doctor(
        self,
        rollnk_charm = '1d6',
        rollnk_agile = '1d6',
        rollnk_strength = '1d6',
        rollnk_intelligence = '1d6'
    ):
        """
            初始化doctor文档
            会覆盖原始文档，慎重调用
            适用于编队信息未形成时
        
        """
        charm_init = self.charm_init
        agile_init = self.agile_init
        strength_init = self.strength_init
        intelligence_init = self.intelligence_init

        print('正在进行磨皮')
        charm = int(sx.roll(rollnk_charm).split('*************')[1].split('Total:')[1])
        print('正在安装脚底板')
        agile = int(sx.roll(rollnk_agile).split('*************')[1].split('Total:')[1])
        print('正在学习摸鱼')
        strength = int(sx.roll(rollnk_strength).split('*************')[1].split('Total:')[1])
        print('正在理解一切')
        intelligence = int(sx.roll(rollnk_intelligence).split('*************')[1].split('Total:')[1])
        print('正在钱本')

        sanity_upper = intelligence # 理智上限规则 【未设置

        LMB = 7500 # 起始资金 【未设置

        # print(charm,agile,strength)
        # 合成
        doc_dict = {
            'doctor_name':self.name,
            'charm':int(charm_init)+charm,
            'agile':int(agile_init) + agile,
            'strength':int(strength_init )+ strength,
            'intelligence':int(intelligence_init) + intelligence,
            'sanity':sanity_upper,
            'LMB': LMB,
            'package':['热水壶','行动前演说','测试测试 abc'],
            'squad':['能天使'],
            'exp':0,
            'Level':1}

        # 属性值存在博士名下的txt文件中
        self.write_doc(doc_dict)


    


    def read_doctor(self):    
        """
            读取doctor个人文档
            分为doctor信息、编队信息 【目前只计划写两部分

        """
        doc_dict ={
            'doctor_name':' ',
            'charm':0, # 魅力
            'agile':0, # 敏捷
            'strength':0, # 体质
            'intelligence':0, # 智力
            'sanity':0,
            'LMB':0, # 龙门币
            'package':[], # 背包
            'squad':[], # 干员/编队
            'exp':0, # 博士经验值
            'Level':1}

        list_type = ['package','squad'] # 列表类型储存的，读取时需转换成列表类型

        with open(self.filename, 'r') as f:
            for line in f.readlines():
                if line.split('|')[0] != '**********\n':
                    # 读取列表
                    if line.split('|')[0] in list_type:
                        linetemp = line.split('|')[1].split("'")[1::2]
                        # print(linetemp)
                        doc_dict[line.split('|')[0]] = linetemp

                    # 读取单值
                    else:
                        doc_dict[line.split('|')[0]] = line.split('|')[1]
                
        print(doc_dict)
        return doc_dict



    def squad_recruit(self,pick_type = None,pick_num = 1):
        """
            依然是不知道用途的玩意，先写下吧
            能跑就行.jpg
        """
        opt_list = sx.squads_roll(pick_type,pick_num)
        print('抽取干员',opt_list)
        ## 爬虫模块-接入数据 【待开发
        for opt in opt_list:
            self.__update_doc__('squad','增加 '+opt) # 调用更新方法

        self.read_doctor()



    def __update_doc__(self,dat_key,update_dat,admin = False):
        """
            手动更新博士的各项数值【不提供对外接口】
            当然，适用于活动后自动更新
            考虑复制文件进行操作，防止文档不可逆损坏【还没写】
            注意：建议使用标准【英文title】进行更新

            Usage demo:
                hehe_doc.__update_doc__('LMB','增加 2333')
                hehe_doc.__update_doc__('agile','更新 10',admin = True)
                
        """

        print('修改前：')
        doc_dict = self.read_doctor()

        if admin and (re.match('更新',update_dat)):
            try:
                doc_dict[dat_key] = update_dat.split('更新')[1] # 单值项可以直接替换，需要admin权限
            except:
                print('更新出错\n')
        else:
            
            try:
                if (dat_key == '敏捷')|(dat_key == 'agile'):
                    if re.match('增加', update_dat):
                        doc_dict['agile'] = int(doc_dict['agile']) + int(update_dat.split('增加')[1])
                    elif re.match('减少', update_dat):
                        doc_dict['agile'] = int(doc_dict['agile']) - int(update_dat.split('减少')[1])

                elif (dat_key == '魅力')|(dat_key == 'charm'):
                    if re.match('增加', update_dat):
                        doc_dict['charm'] = int(doc_dict['charm']) + int(update_dat.split('增加')[1])
                    elif re.match('减少', update_dat):
                        doc_dict['charm'] = int(doc_dict['charm']) - int(update_dat.split('减少')[1])

                elif (dat_key == '体质')|(dat_key == 'strength'):
                    if re.match('增加', update_dat):
                        doc_dict['strength'] = int(doc_dict['strength']) + int(update_dat.split('增加')[1])
                    elif re.match('减少', update_dat):
                        doc_dict['strength'] = int(doc_dict['strength']) - int(update_dat.split('减少')[1])

                elif (dat_key == '智力')|(dat_key == '理智')|(dat_key == 'intelligence' ):
                    if re.match('增加', update_dat):
                        doc_dict['intelligence'] = int(doc_dict['intelligence']) + int(update_dat.split('增加')[1])
                    elif re.match('减少', update_dat):
                        doc_dict['intelligence'] = int(doc_dict['intelligence']) - int(update_dat.split('减少')[1])

                elif (dat_key == '背包') |(dat_key == '道具')|(dat_key == 'package') :
                    if re.match('增加', update_dat):
                        doc_dict['package'].append(update_dat.split('增加')[1])
                    elif re.match('减少', update_dat):
                        doc_dict['package'].remove(update_dat.split('减少')[1])

                elif (dat_key == '理智') |(dat_key == 'sanity') :
                    if re.match('增加', update_dat):
                        doc_dict['sanity'].append(update_dat.split('增加')[1])
                    elif re.match('减少', update_dat):
                        doc_dict['sanity'].remove(update_dat.split('减少')[1])

                elif (dat_key == '编队') |(dat_key == '小队')|(dat_key == 'squad') :
                    if re.match('增加', update_dat):
                        doc_dict['squad'].append(update_dat.split('增加')[1])
                    elif re.match('减少', update_dat):
                        doc_dict['squad'].remove(update_dat.split('减少')[1])

                    # doc_dict['package'].append(update_dat)
                elif (dat_key == '龙门币' )|(dat_key == '金钱') |(dat_key == 'LMB') :
                    if re.match('增加', update_dat):
                        doc_dict['LMB'] = int(doc_dict['LMB']) + int(update_dat.split('增加')[1])
                    elif re.match('减少', update_dat):
                        doc_dict['LMB'] = int(doc_dict['LMB']) - int(update_dat.split('减少')[1])

                elif (dat_key == '经验' )|(dat_key == '经验值') |(dat_key == 'exp') :
                    if re.match('增加', update_dat):
                        doc_dict['exp'] = int(doc_dict['exp']) + int(update_dat.split('增加')[1])
                    elif re.match('减少', update_dat):
                        doc_dict['exp'] = int(doc_dict['exp']) - int(update_dat.split('减少')[1])
            except(ValueError):
                print('数字/字符格式错误')
                return

        self.write_doc(doc_dict)
        print('更新完毕：')
        self.read_doctor()


    def exp_check(self):
        """经验值检查"""
        doc_dict = self.read_doctor()
        exp = int(doc_dict['exp'])
        print(exp)
        return exp



    def relax(self):
        """
            休息恢复理智
        """

        pass

if __name__ == "__main__":
    hehe_doc = doctor('hehe',0,0,0,0)
    hehe_doc.init_doctor()
    # hehe_doc.read_doctor()
    # hehe_doc.squad_recruit('近卫，先锋')
    # hehe_doc.__update_doc__('LMB','增加 2333')
    # hehe_doc.__update_doc__('Level','更新 2',admin = True)
    hehe_doc.__update_doc__('exp','增加 200')

    hehe_doc.exp_check()
    pass

