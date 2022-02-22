'''
Author: KOneLane
Date: 2021-09-14 13:00:02
LastEditors: KOneLane
LastEditTime: 2022-02-13 22:57:17
Description: 
version: V
'''
#! /usr/bin/env python3
# coding:utf-8


## 对个对联吧
from selenium import webdriver # 性能不足
from time import sleep
from selenium.webdriver.common.keys import Keys

# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.wait import WebDriverWait

class couplet_api:
    def __init__(self,text) -> None:
        self.text = text
        pass

    def __init_chrome(self,load = 1):
        option = webdriver.ChromeOptions()
        # 加载图片
        prefs = {
                    'profile.default_content_setting_values': {
                        'images': load,
                        'permissions.default.stylesheet': 2
                    }
                } # 2是不加载，1是加载
        option.add_experimental_option('prefs', prefs)
        option.add_experimental_option('excludeSwitches', ['enable-logging'])#禁止打印日志 # 没用
        option.add_experimental_option('excludeSwitches', ['enable-automation'])#实现了规避监测
        option.add_argument('log-level=3')#INFO = 0 WARNING = 1 LOG_ERROR = 2 LOG_FATAL = 3 default is 0
        option.add_argument('headless')#“有头”模式，即可以看到浏览器界面，若要隐藏浏览器，可设置为 "headless"
        option.add_argument('--disable-javascript')
        dr0 = webdriver.Chrome(chrome_options = option)#得到操作对象
        return dr0

    def CoupletGet(self):
        """获得信息文字源代码"""
        dr0 = self.__init_chrome(load = 2) # 设置为不加载图片
        dr0.get(f'https://ai.binwang.me/couplet/')
        
        dr0.find_element_by_class_name('couplet-input').send_keys(self.text)
        dr0.find_element_by_class_name('couplet-input').send_keys(Keys.ENTER)
        # dr0.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div[3]/button[1]').click()
        sleep(3)
        # '/html/body/div/div[1]/div[2]/div[1]/div[2]'
        # WebDriverWait(dr0,10).until(EC.visibility_of_element_located(dr0.find_element_by_css_selector('#app > div.page > div.content > div.couplet-text.couplet-text_down > div.couplet-bd')))
        return_text = dr0.find_element_by_xpath('/html/body/div/div[1]/div[2]/div[2]/div[2]').text

        # dr0.quit()

        return return_text

# from time import time
if __name__ == "__main__":
    # time0 = time()
    prts_1 = couplet_api('神经网络听不懂')
    print(prts_1.CoupletGet())
    # print(time() - time0)