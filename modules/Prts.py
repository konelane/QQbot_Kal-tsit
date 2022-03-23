#! /usr/bin/env python3
# coding:utf-8
import os
import re
from os.path import basename

import requests
from bs4 import BeautifulSoup as bs
from core.decos import DisableModule, check_group, check_member
from core.MessageProcesser import MessageProcesser
from core.ModuleRegister import Module
from core.Text2Img import generate_img
from database.kaltsitReply import blockList
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
    name='Prts',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.Prts',
).register()



class Prts:

    def __init__(self,name) -> None:
        self.name = name
        pass

    ## 
    def __MessageGet(self):
        """获得信息文字源代码"""
        url = f'http://prts.wiki/index.php?title={self.name}&action=edit'
        page = requests.get(url)
        soup = bs(page.content, 'html.parser')  #解析网页
        kk = str(soup.find_all("",class_="mw-editfont-monospace")[0]).split('==')#找到每个网页内容中的文字取出来
        opt_dict = dict()
        for i in range(int(len(kk)/2)):
            opt_dict[kk[2*i+1]] = kk[2*i+2]
        return opt_dict

    def MasteryMetarialGet(self):
        """based on MessageGet - 获得专精材料信息"""
        opt_dict = self.__MessageGet()
        # print('opt_dict',opt_dict)
        upgrade_me = opt_dict['技能升级材料'].split('}}|')

        def __text_deal(text):
            text2 = re.sub('}} {{',',',text)
            text2 = re.sub('{{','',text2)
            text2 = re.sub('}}','',text2)
            text2 = re.sub('材料消耗\|','',text2)
            text2 = re.sub('技能升级材料\|','',text2)
            return text2
        print('专精材料获取完毕')
        return '\n'.join(x for x in list(map(__text_deal,upgrade_me))[0].split('\n')[1:-2])

    def AttributeGet(self):
        """based on MessageGet - 获得干员属性信息"""
        opt_dict = self.__MessageGet()
        upgrade_me = opt_dict['属性'].split('|')
        return upgrade_me[1:-2]

    def EliteMetarialGet(self):
        """based on MessageGet - 获得精英化材料"""
        opt_dict = self.__MessageGet()
        upgrade_me = opt_dict['精英化材料'].split('=')
        def text_deal(text):
            text2 = re.sub('}} {{',',',text)
            text2 = re.sub('{{','',text2)
            text2 = re.sub('}}','',text2)
            # text2 = re.sub('\n','',text2)
            text2 = re.sub('材料消耗\|','',text2)
            text2 = re.sub('精2','',text2)
            text2 = re.sub('精英化材料\|','',text2)
            return text2
        return list(map(text_deal,upgrade_me))[1:]

    def BirthdayGet(self):
        """based on MessageGet - 获得干员生日"""
        opt_dict = self.__MessageGet()
        return opt_dict['干员档案'].split('生日=')[1].split('|')[0][:-1]

    def LogisticsSkill(self):
        """based on MessageGet - 获得后勤技能名称信息"""
        dict_temp = self.__LogisticsSkillSearch() # 名称字典
        opt_dict = self.__MessageGet()
        # print(opt_dict['后勤技能'])
        base_skill = opt_dict['后勤技能'].split('}}')[0].split('|')[1:]

        logistic_dict = dict()
        for item in base_skill:
            temp = item.split('=')[1]
            temp = re.sub('\n','',temp)
            
            if temp in dict_temp.keys():

                logistic_dict[temp] = dict_temp[temp]
                
        # print(logistic_dict)

        return '\n'.join(x for x in list(logistic_dict.values()))



        # return base_skill
        # def text_deal(text):
        #     text2 = re.sub('\n','',text)
        #     return text2
        # return list(map(text_deal,base_skill))
    
    def __LogisticsSkillSearch(self):
        
        url2 = 'https://prts.wiki/index.php?title=%E5%90%8E%E5%8B%A4%E6%8A%80%E8%83%BD%E4%B8%80%E8%A7%88&action=edit'
        page = requests.get(url2)
        soup = bs(page.content, 'html.parser')  #解析网页
        # print(soup)
        kk = str(soup.find_all("",class_="mw-editfont-monospace")[0]).split('技能名=')[1::]#找到每个网页内容中的文字取出来
        def text_dealer(text):
            
            text2 = re.sub('|-','',text)
            text2 = re.sub('\|','',text2)
            text2 = re.sub('{{','',text2)
            text2 = re.sub('}}','',text2)
            text2 = re.sub('房间','',text2)
            text2 = re.sub('技能描述','',text2)
            text2 = re.sub('color|#\w\w\w\w\w\w','',text2)
            
            text2 = text2.split('\n')
            text2 = text2[:-2:]
            text2[2] = ''
            return text2[0], '\n'.join(x for x in text2[1::] if x.startswith('=') and not x.startswith('=='))
        dict_temp = dict(map(text_dealer, kk))
        
        # print(dict_temp['悲歌'])
        return dict_temp
        

    def TodayBirthday(self):
        """
        待更新：
         - 1.无干员生日时
         - 2.多干员生日时
        """
        url = "https://prts.wiki/w/%E9%A6%96%E9%A1%B5/%E4%BA%AE%E7%82%B9%E5%B9%B2%E5%91%98/%E4%BB%8A%E5%A4%A9%E7%94%9F%E6%97%A5" # https://prts.wiki/w/首页/亮点干员/今天生日
        page = requests.get(url)
        soup = bs(page.content, 'html.parser')
        ansss = soup.find_all("",class_="mp-operators-icons")
        if not ansss:
            return("谢谢你的关心博士，不过今日没有干员过生日") 
        else:
            ansss_str = str(ansss[0])
            idx = re.search('title="', ansss_str).span()[1]
            name_birth = ansss_str[idx:].split('\"')[0]
            return (f"今天过生日的干员是{name_birth}")



@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'#prts ')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), DisableModule.require(module_name)],
    )
)
async def Prts_app(
    app: Ariadne, 
    message: MessageChain,
    group: Group,
    member: Member 
):
    pass    
    """prts查询功能"""
    prts_mod = ['技能专精','晋升材料','属性','后勤','生日','今日生日']
    exception_squad = ['凯尔希']

    slightly_inittext = MessageProcesser(message,group,member)
    msg_info_dict = slightly_inittext.text_processer()
    text_list = msg_info_dict['text_split']
    
    if len(text_list)<= 2:
        return None
    if text_list[1] in exception_squad:
        outtext = '我的情况由我自己判断，各位应该把注意力放在其他需要帮助的感染者身上。'
        await app.sendGroupMessage(group, MessageChain.create(
            Plain(outtext)
        ))
    if text_list[2] not in prts_mod:
        return None
    else:
        prts_1 = Prts(text_list[1])
        if text_list[2] == '技能专精':
            out_list = prts_1.MasteryMetarialGet()
        if text_list[2] == '晋升材料':
            out_list = prts_1.EliteMetarialGet()
        if text_list[2] == '属性':
            out_list = prts_1.AttributeGet()
        if text_list[2] == '后勤':
            out_list = prts_1.LogisticsSkill()
        if text_list[2] == '生日':
            out_list = '这位干员的生日是' + prts_1.BirthdayGet()
        if text_list[2] == '今日生日':
            out_list = prts_1.TodayBirthday()

        generate_img([''.join(x for x in out_list)]) 
        img_name = 'bot/database/temp_prts.jpg'  # 自定义临时文件的保存名称
        img_path = os.path.join(img_name)
        await app.sendGroupMessage(group, MessageChain.create(
            Image(path=img_path)
        ))
