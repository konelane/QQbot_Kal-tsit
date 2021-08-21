#! /usr/bin/env python3
# coding:utf-8

## prts信息获取

from selenium import webdriver
from time import sleep

import re
from PIL import Image
from io import BytesIO


class prts:

    def __init__(self,name) -> None:
        self.name = name
        pass


    def init_chrome(self,load = 1):
        option = webdriver.ChromeOptions()
        # 加载图片
        prefs = {
                    'profile.default_content_setting_values': {
                        'images': load,
                    }
                } # 2是不加载，1是加载
        option.add_experimental_option('prefs', prefs)
        option.add_experimental_option('excludeSwitches', ['enable-logging'])#禁止打印日志 # 没用
        option.add_experimental_option('excludeSwitches', ['enable-automation'])#实现了规避监测
        option.add_argument('log-level=3')#INFO = 0 WARNING = 1 LOG_ERROR = 2 LOG_FATAL = 3 default is 0
        option.add_argument('headless')#“有头”模式，即可以看到浏览器界面，若要隐藏浏览器，可设置为 "headless"
        dr0 = webdriver.Chrome(chrome_options = option)#得到操作对象
        return dr0

    ## 待开发
    def MasteryPicGet(self):
        """获取专精材料图片位置【待开发】"""
        dr0 = self.init_chrome()
        name = self.name
        try:
            dr0.maximize_window()
            dr0.get(f'http://prts.wiki/w/{name}')
            dr0.execute_script("document.body.style.transform='scale(0.5)'")
            dr0.get(f'http://prts.wiki/w/{name}#.E6.8A.80.E8.83.BD.E5.8D.87.E7.BA.A7.E6.9D.90.E6.96.99')
            print('加载中')
            dr0.refresh()
            sleep(3)
            # dr0.get(f'http://prts.wiki/w/{name}#.E6.8A.80.E8.83.BD.E5.8D.87.E7.BA.A7.E6.9D.90.E6.96.99')
            # dr0.execute_script("document.body.style.zoom='0.9'")
        except:
            print('干员输入错误/没有技能可专精')
            return 1
        screenshot1 = dr0.get_screenshot_as_png()
        screenshot2 = Image.open(BytesIO(screenshot1))
        left, top, right, bottom = 150, 0, 800, 600
        cathch = screenshot2.crop((left, top, right, bottom))
        cathch.save('./botqq/temp.png')
        return 

    ## 
    def __MessageGet(self):
        """获得信息文字源代码"""
        dr0 = self.init_chrome(load = 2) # 设置为不加载图片
        dr0.get(f'http://prts.wiki/index.php?title={self.name}&action=edit')
        message_all = ''.join(x for x in dr0.find_element_by_xpath('//*[@id="wpTextbox1"]').text.split('\n')).split('==')
        opt_dict = dict()
        for i in range(int(len(message_all)/2)):
            opt_dict[message_all[2*i+1]] = message_all[2*i+2]
        dr0.close()
        return opt_dict

    def MasteryMetarialGet(self):
        """based on MessageGet - 获得专精材料信息"""
        opt_dict = self.__MessageGet()
        upgrade_me = opt_dict['技能升级材料'].split('}}|')

        def __text_deal(text):
            text2 = re.sub('}} {{',',',text)
            text2 = re.sub('{{','',text2)
            text2 = re.sub('}}','',text2)
            text2 = re.sub('材料消耗\|','',text2)
            text2 = re.sub('技能升级材料\|','',text2)
            return text2
        print('专精材料获取完毕')
        return list(map(__text_deal,upgrade_me))

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
            text2 = re.sub('材料消耗\|','',text2)
            text2 = re.sub('精2','',text2)
            text2 = re.sub('精英化材料\|','',text2)
            return text2
        return list(map(text_deal,upgrade_me))[1:]

    def BirthdayGet(self):
        """based on MessageGet - 获得干员生日"""
        opt_dict = self.__MessageGet()
        return opt_dict['干员档案'].split('生日=')[1].split('|')[0]

    def LogisticsSkill(self):
        """based on MessageGet - 获得后勤技能名称信息"""
        opt_dict = self.__MessageGet()
        return opt_dict['后勤技能'].split('}}')[0].split('|')[1:]
    
    ## 萌百-访问可能被拒绝，需要验证码
    def BaseInfoGet(self):
        """干员基本信息 - 来自萌娘百科"""
        dr0 = self.init_chrome(load = 2)
        dr0.get(f'https://zh.moegirl.org.cn/明日方舟:{self.name}')
        text = dr0.find_element_by_xpath('/html/body/div[3]/div[3]/div[4]/div/div[5]/table/tbody').text.split('\n')
        dr0.close()
        return text


    


if __name__ == "__main__":
    prts_1 = prts('苏苏洛')
    # print(prts_1.MasteryMetarialGet())
    # prts_1.MasteryPicGet()
    # print(prts_1.LogisticsSkill())
