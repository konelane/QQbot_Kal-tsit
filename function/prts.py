#! /usr/bin/env python3
# coding:utf-8

## prts信息获取

import requests
from bs4 import BeautifulSoup as bs
import re


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
        return list(map(__text_deal,upgrade_me))[0].split('\n')[1:-2]

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
            text2 = re.sub('\n','',text2)
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
        opt_dict = self.__MessageGet()
        base_skill = opt_dict['后勤技能'].split('}}')[0].split('|')[1:]
        def text_deal(text):
            text2 = re.sub('\n','',text)
            return text2
        return list(map(text_deal,base_skill))
    
    # ## 萌百-访问可能被拒绝，需要验证码
    # def GengInfoGet(self):
    #     """干员基本信息 - 来自萌娘百科"""
    #     dr0 = self.init_chrome(load = 2)
    #     dr0.get(f'https://zh.moegirl.org.cn/明日方舟:{self.name}')
    #     text = dr0.find_element_by_xpath('/html/body/div[3]/div[3]/div[4]/div/div[5]/table/tbody').text.split('\n')
    #     dr0.close()
    #     return text


    


if __name__ == "__main__":
    pass
    # prts_1 = Prts('苏苏洛')
    # print(prts_1.MasteryMetarialGet())
    # print(prts_1.EliteMetarialGet())
    # print(prts_1.BirthdayGet())
    # print(prts_1.LogisticsSkill())
