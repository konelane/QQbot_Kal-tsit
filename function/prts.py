#! /usr/bin/env python3
# coding:utf-8

## prts信息获取
## 更新于21.11.25

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
    prts_1 = Prts('桃金娘')
    print(prts_1.MasteryMetarialGet())
    # print(prts_1.EliteMetarialGet())
    # print(prts_1.BirthdayGet())
    # print(prts_1.LogisticsSkill())
    # print(prts_1.LogisticsSkillSearch())
