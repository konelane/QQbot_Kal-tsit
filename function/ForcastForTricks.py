#! /usr/bin/env python3
# coding:utf-8

import requests
from bs4 import BeautifulSoup as bs
# from .. AuthSet import AuthSet
import re # 字符处理
import datetime
import pandas as pd
import os
# 外部包 + 网络环境
import pygal
from pygal.style import LightColorizedStyle as LCS,LightenStyle as LS

import geopy
from geopy.geocoders import Nominatim
import osmnx as ox
import pickle


# class ForcastForTricks(AuthSet):
class ForcastForTricks():
    def __init__(self,msgout) -> None:
        # super().__init__(msg) # 权限系统，用不用再说……
        """
        lon, lat – 指定地点的经纬度，必须是浮点数。
        output – 可设定为internal（图表输出）、xml或json（程序API）。
        product – 为程序API选择产品，应为astro, civil, civillight, meteo或two。

        ac – 高度改正，只对天文用途预报有效。可取0（默认）、2或7。不适用于程序API。
        lang – 语言。对气象用途产品及程序API无效。
        unit – 公制或英制。对程序API无效
        tzshift – 时区微调，可取0、1或-1。对程序API无效。
        """
        self.msgout = msgout
        self.output = 'json'
        self.product = 'astro' # 天文用途
        self.text = msgout['text_split']
        self.lon = 116.391
        self.lat = 39.907

    def __location_get(self):
        """获取指定地名的经纬度 并更新类变量"""
        geolocator = Nominatim(user_agent="kal-tsit")
        location = geolocator.geocode(self.text[1])
        if not location:
            return
        else:
            self.lon = location.longitude
            self.lat = location.latitude
            return 'updated'

    def __url_sky_get(self):
        """天气json数据获取"""
        self.__location_get() # 先更新
        url= f'https://www.7timer.info/bin/api.pl?lon={str(self.lon)}&lat={str(self.lat)}&product={self.product}&output={self.output}'#存储API调用的URL
        r=requests.get(url) #获得URL对象
        # print("Status code:",r.status_code) #判断请求是否成功（状态码200时表示请求成功）
        response_dict=r.json() 
        
        return response_dict

    def __map_get(self):
        """画地图"""
        if self.__location_get():
        # G = pickle.load(open('database/beijing.pkl','rb'))
        # loc_node = ox.get_nearest_node(G, (self.lat,self.lon))
        # 联网条件
            G = ox.graph_from_point((self.lat,self.lon), dist=int(self.text[2]), network_type='all')
            if os.path.exists('C:/Users/Administrator/botqq/database/temp.png'):
                os.remove('C:/Users/Administrator/botqq/database/temp.png')
            ox.plot_graph(G,show=False,save=True,filepath='C:/Users/Administrator/botqq/database/temp.png')
            return 'map'
        else:
            return '地点不存在'
    

    def __weather_text_processor(self,dict_of_data):
        """
        timepoint: 时间
        cloudcover: 云量八分图，蓝色代表晴天所占的比例，白色代表云所占的比例，从左到右的云量从0%递增到100%。
        seeing: 视宁度，<0.5", 0.5"-0.75", 0.75"-1", 1"-1.25", 1.25"-1.5", 1.5"-2", 2"-2.5", >2.5"。简单地说，越小视宁度越好。
        transparency: 透明度，<0.3, 0.3-0.4, 0.4-0.5, 0.5-0.6, 0.6-0.7, 0.7-0.85, 0.85-1, >1（单位为星等每大气质量）。
        lifted_index: 稳定性LI，大气不稳定度，从左到右分别代表抬升指数介于0至-3，-3至-5，以及小于-5。
        rh2m: 相对湿度
        wind10m: {
            direction: 风向
            speed: 风速
        }
        temp2m: 气温
        prec_type: 大风预警
        """
        dict_out = {
            '时窗':dict_of_data['timepoint'],
            '云量':dict_of_data['cloudcover'],
            '视宁':dict_of_data['seeing'],
            '透明':dict_of_data['transparency'],
            '湿度':dict_of_data['rh2m'],
            '气温':dict_of_data['temp2m'],
            '风向':dict_of_data['wind10m']['direction'],
            '风速':dict_of_data['wind10m']['speed'],
            # '风10m':dict_of_data['wind10m'],
            '稳定':dict_of_data['lifted_index'],
            '预警':dict_of_data['prec_type']
        }
        

        def level_text_append(dict_out):
            if int(dict_out['云量']) <= 1:
                dict_out['云量'] = '**' + str(dict_out['云量']) # 少云天气
            if (int(dict_out['稳定']) <= -3 )and (int(dict_out['稳定']) > -5):
                dict_out['稳定'] = '*' + str(dict_out['稳定'])
            elif (int(dict_out['稳定']) <= -5 ):
                dict_out['稳定'] = '**' + str(dict_out['稳定'])
            if int(dict_out['风速']) >= 10:
                dict_out['风速'] = '*' + str(dict_out['风速']) # 大风天气
            return dict_out

        dict_out = level_text_append(dict_out)

        def text_dealer(text):
            text = re.sub("\'",'',text)
            text = re.sub("\{",'',text)
            text = re.sub("\}",'',text)
            text = re.sub("none",'无',text)
            text = re.sub("rain",'雨',text)
            text += '\n'
            return text
        return text_dealer(str(dict_out))


    def __astro_phenomenon(self):
        """爬取天象预报"""
        url = 'https://interesting-sky.china-vo.org' # 网址是
        page = requests.get(url)
        soup = bs(page.content, 'html.parser')  #解析网页
        ans = []
        for i in soup.find_all("",class_='widget widget_text'):
            ans.append(i.text)

        def find_news(texta):
            # 似乎还不支持自定义月份
            month = datetime.datetime.now().month
            if texta.startswith(str(month) + '月'):
                return texta
        res = list(filter(None, list(map(find_news,ans[0].split('\n')))))
        return res


    def orderToReturn(self):
        """根据指令返回"""
        if self.text[0] == '#地图':
            return self.__map_get()
        if self.text[0] == '#天气':
            if self.text[2] in ['今天','1','今日','一日']:
                ans_dict = self.__url_sky_get()
                output = '\n'.join(self.__weather_text_processor(x) for x in ans_dict['dataseries'][:8])
                
            return output
    #     ans_dict,week_day_report = self.__sevenDaysWeather()
    #     if self.order in ['今天','1','一日']:
    #         day_weather = self.__findDaysInWeek(0,week_day_report)
    #         hour_weather = ans_dict['0']
    #         return str(pd.DataFrame(day_weather)) + str(pd.DataFrame(hour_weather))
    #     elif self.order in ['明天']:
    #         day_weather = self.__findDaysInWeek(1,week_day_report)
    #         hour_weather = ans_dict['1']
    #         return str(pd.DataFrame(day_weather)) + str(pd.DataFrame(hour_weather))
    #     elif self.order in ['2','两日']:
    #         ans_text = ''
    #         day_weather = self.__findDaysInWeek(0,week_day_report)
    #         hour_weather = ans_dict['0']
    #         ans_text += str(pd.DataFrame(day_weather)) + str(pd.DataFrame(hour_weather))
    #         # 第二天的
    #         day_weather = self.__findDaysInWeek(1,week_day_report)
    #         hour_weather = ans_dict['1']
    #         ans_text += str(pd.DataFrame(day_weather)) + str(pd.DataFrame(hour_weather))
    #         return ans_text


if __name__ == '__main__':
    msg2 = {
        'id':'591016144',
        'text_split':['#天气','昌平','今天'],
        'text_jieba':['#','天气','北京','今天']
    }
    msg3 = {
        'id':'591016144',
        'text_split':['#地图','北京清河站','700'],
        'text_jieba':['#','地图','清河站','700']
    }
    forcast = ForcastForTricks(msg2)
    print(forcast.orderToReturn())

    