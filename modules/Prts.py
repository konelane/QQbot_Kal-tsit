#! /usr/bin/env python3
# coding:utf-8
import os
import random
import re
from os.path import basename

import requests
from bs4 import BeautifulSoup as bs
from core.decos import DisableModule, check_group, check_member, check_permitGroup
from core.MessageProcesser import MessageProcesser
from core.ModuleRegister import Module
from core.Text2Img import generate_img
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


    def ModuleSearch(self):
        """
        模组
        """
        url = f"https://prts.wiki/w/{self.name}#模组" # https://prts.wiki/w/干员名#模组
        page = requests.get(url)
        soup = bs(page.content, 'html.parser')
        soup_list = soup.find_all("", class_="wikitable nodesktop")


        def textDealer(textIn):
            textOut = re.sub('\n<td colspan="3">', "", textIn)
            textOut = re.sub(' <span style="color:#00B0FF;">', "", textOut)
            textOut = re.sub('<span style="color:#00B0FF;">', "", textOut)
            textOut = re.sub('</span>\n</td></tr>\n<tr>\n', "", textOut)
            
            textOut = re.sub('<div style="zoom:70%;display:inline-block;"><svg style="vertical-align:top;width:130px;height:78px;width:!important;height:!important" viewbox="0 0 130 78" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><defs><rect fill="#27a6f3" height="22" id="1" width="22"></rect><rect fill="none" height="20" id="2" stroke="gray" stroke-width="2" width="20"></rect></defs><use x="2" xlink:href="#2" y="2"></use><use x="28" xlink:href="#2" y="2"></use><use x="54" xlink:href="#2" y="2"></use><use x="80" xlink:href="#2" y="2"></use><use x="2" xlink:href="#2" y="28"></use><use x="27" xlink:href="#1" y="27"></use><use x="54" xlink:href="#2" y="28"></use><use x="80" xlink:href="#2" y="28"></use><use x="106" xlink:href="#2" y="28"></use><use x="2" xlink:href="#2" y="54"></use><use x="28" xlink:href="#2" y="54"></use><use x="54" xlink:href="#2" y="54"></use><use x="80" xlink:href="#2" y="54"></use></svg></div>', '', textOut)
            textOut = re.sub('\n</td></tr>\n<tr><i class="fa-plus-circle fas" style="font-size:;height:;color:;"></i>', "\n",textOut)
            textOut = re.sub('<tr><i class="fa-chevron-circle-up fas" style="font-size:;height:;color:;"></i>', ' *', textOut)
            textOut = re.sub('<span style="color: #FF6237;"><i class="fa- fas" style="font-size:;height:;color:;"></i>', ' & ', textOut)
            textOut = re.sub('<span style="color: #0098DC;"><i class="fa-arrow-alt-circle-up fas" style="font-size:;height:;color:;"></i>', '', textOut)
            textOut = re.sub('<span style="color: #0098DC;"><i class="fa-arrow-alt-circle-down fas" style="font-size:;height:;color:;"></i>', '', textOut)
            textOut = re.sub('<span data-size="350" style="display:none">', '', textOut)
            textOut = re.sub('<span class="mc-tooltips"><span class="term" style="text-decoration:underline #222;white-space:nowrap;text-shadow: 0 0 1px;">', '', textOut)
            textOut = re.sub('<span style="color:#0098DC;">', "",textOut)
            textOut = re.sub('"4"><i class="fa-chevron-right fas" style="font-size:;height:;color:;"></i> ', " *",textOut)
            
            
            textOut = re.sub(r'<a class="mw-redirect" href="/w/[A-Z]{0,1}[0-9]{1,2}-[0-9]{1,2}" "[A-Z]{0,1}[0-9]{1,2}-[0-9]{1,2}">', "",textOut)
            textOut = re.sub('<td colspan=', "",textOut)
            textOut = re.sub('</span>\xa0', "",textOut)
            textOut = re.sub('</td></tr>', "",textOut)
            textOut = re.sub('</span>', "",textOut)
            textOut = re.sub('\xa0', "",textOut)
            textOut = re.sub('<tr>', "",textOut)
            textOut = re.sub('<br/>', ":",textOut)
            textOut = re.sub('<b>', "",textOut)
            textOut = re.sub('</b>', "", textOut)
            textOut = re.sub('</a>', "", textOut)
            textOut = re.sub('\n', "",textOut)
            
            return textOut

        def metarialTextDealer(textIn):
            return textIn.split(';">')[1].split('</span></div>')[0]
            

        abc = re.split('title=|<th colspan="1">|<th colspan="2">|<th colspan="4">|<th rowspan="2">|<th rowspan="3">|><img alt=|<th>|\n</th></tr>\n<tr>\n<td colspan=|</th>', str(soup_list[0]))
        if soup_list == []:  return ''
        module_dict = {
            'name': abc[2].split(' <span class="mc-tooltips">')[0],
            'effect_lv1': textDealer(abc[6]),
            'effect_lv2': textDealer(abc[8]),
            'effect_lv3': textDealer(abc[10]),
            'unlock_task': textDealer(abc[12] + abc[13]),
            'unlock_metarial':  textDealer(
                abc[16]+':'+metarialTextDealer(abc[17])+';'+
                abc[18]+':'+metarialTextDealer(abc[19])+';'+
                abc[20]+':'+metarialTextDealer(abc[21])
            ),
            'levelup1_metarial': textDealer(
                abc[25]+':'+metarialTextDealer(abc[26])+';'+
                abc[27]+':'+metarialTextDealer(abc[28])+';'+
                abc[29]+':'+metarialTextDealer(abc[30])+';'+
                abc[31]+':'+metarialTextDealer(abc[32])
            ),
            'levelup2_metarial': textDealer(
                abc[34]+':'+metarialTextDealer(abc[35])+';'+
                abc[36]+':'+metarialTextDealer(abc[37])+';'+
                abc[38]+':'+metarialTextDealer(abc[39])+';'+
                abc[40]+':'+metarialTextDealer(abc[41])
            ),
        }
        outtext = ''
        zh_dict = {
            'name': '【模组名称】',
            'effect_lv1': '【模组lv1】',
            'effect_lv2': '【模组lv2】',
            'effect_lv3': '【模组lv3】',
            'unlock_task': '【解锁任务】',
            'unlock_metarial':  '【解锁材料】',
            'levelup1_metarial': '【升级材料1】',
            'levelup2_metarial': '【升级材料2】',
        }

        for key,val in (module_dict.items()):
            outtext += zh_dict[key] + val + '\n'

        return outtext


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'#prts ')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
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
    prts_mod = ['技能专精','晋升材料','属性','后勤','生日','今日生日','模组']
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
        return 
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
        if text_list[2] == '模组':
            out_list = prts_1.ModuleSearch()
        # 模组系统
        if out_list != '' and out_list != []:
            generate_img([''.join(x for x in out_list)]) 
            img_name = 'bot/database/temp_prts.jpg'  # 自定义临时文件的保存名称
            img_path = os.path.join(img_name)
            await app.sendGroupMessage(group, MessageChain.create(
                Plain(random.sample(text_table,1)[0]),
                Image(path=img_path)
            ))
