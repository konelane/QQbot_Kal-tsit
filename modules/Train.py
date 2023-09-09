#! /usr/bin/env python3
# coding:utf-8

import time
from os.path import basename
from time import sleep
import re

from core.decos import (DisableModule, check_group, check_member,
                        check_permitGroup)
from core.MessageProcesser import MessageProcesser
from core.ModuleRegister import Module
from database.kaltsitReply import blockList
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.twilight import RegexMatch, Twilight
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from selenium import webdriver  # 性能不足
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from xpinyin import Pinyin

channel = Channel.current()

module_name = basename(__file__)[:-3]

Module(
    name='Train',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.Train',
).register()


class TrainTong:
    '''
    查询火车信息
    - 隐藏功能
    1. 车站电报码
        #ttt code xx站
    2. x日车票
        #ttt tic 始发站-终点站-20230115
    3. 列车时刻
        #ttt timing xx次列车

    '''
    def __init__(self, msg_dict) -> None:
        self.msg_dict = msg_dict

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


    def __getStationList(self, station, code_input = False):
        '''
        @param
            station: 站名 中文
            code_input: 如果是code查询，则为精确查询
        @output
            List: 宝鸡 西安铁路局 陕 -BJY bji 39629
        '''
        if not code_input:
            stationstring = station.encode("unicode-escape").decode().replace('\\', '%')
            url = f'https://moerail.ml/#{stationstring}'
            dr0 = self.__init_chrome(load = 2) # 设置为不加载图片
            dr0.get(url)
            station_list_text = dr0.find_element(by='id',value = 'station-list').text
            
            out_list = list(filter(lambda x : x.split(' ')[0]==station or x.split(' ')[1]==station if len(x.split(' '))>1 else False, station_list_text.split('\n')))[0].split(' ')
            dr0.quit() 
            
        else:
            url = f'https://moerail.ml/#{str(station)}'
            dr0 = self.__init_chrome(load = 2) # 设置为不加载图片
            dr0.get(url)
            station_list_text = dr0.find_element(by='id',value = 'station-list').text
            
            out_list = list(filter(lambda x : station in x.split(' '), station_list_text.split('\n')))[0].split(' ')
            dr0.quit() 
        return out_list



    
    def __codeGet(self, station):
        '''特殊操作 - 用于获得电报码'''
        out_list = self.__getStationList(station)
        if out_list != []:
            if out_list[0] == station:
                return out_list[3][1:]
            else:
                return out_list[4][1:]


    def getTrainUrl(self):
        '''获取12306对应网址'''
        p = Pinyin() 
        sta1 = '宝鸡'
        sta1 = sta1.encode("unicode-escape").decode().replace('\\', '%')

        sta2 = '北京'
        sta2 = sta2.encode("unicode-escape").decode().replace('\\', '%')
        sta1_pinyin = p.get_pinyin('宝鸡','') 
        sta2_pinyin = p.get_pinyin('北京','') 
        url12306 = f'https://www.12306.cn/en/left-ticket.html?fs={sta1_pinyin}%28{sta1}%29,BJP&ts={sta2_pinyin}%28{sta2}%29,BJY&date=2023-01-19'
        return url12306


    
    def search_left_ticket(self, fs, ts, train_date):
        '''缓慢查询 余票'''
        left_ticket_url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc'  # 车次余票
        driver = self.__init_chrome(load = 2)
        driver.get(left_ticket_url)
        # 出发地
        from_station_input = driver.find_element('id','fromStation')
        from_station_code = self.__codeGet(fs)
        driver.execute_script('arguments[0].value="%s"' % from_station_code, from_station_input)

        # 目的地
        to_station_input = driver.find_element('id','toStation')
        to_station_code = self.__codeGet(ts)
        driver.execute_script('arguments[0].value="%s"' % to_station_code, to_station_input)

        # 出发日期
        train_date_input = driver.find_element('id','train_date')
        driver.execute_script('arguments[0].value="%s"' % train_date, train_date_input)

        # 执行查询
        search_btn = driver.find_element('id','query_ticket')
        search_btn.click()

        # 解析车次信息
        WebDriverWait(driver, 1000).until(
            EC.presence_of_element_located((By.XPATH, '//tbody[@id="queryLeftTable"]/tr'))
        )
        # 获取tr标签 把含有datatran的tr标签过滤掉  [not(@datatran)]
        train_trs = driver.find_elements('xpath','//tbody[@id="queryLeftTable"]/tr[not(@datatran)]')
        save_list = []
        header = [
        '车次','发站',
        '到站','发时',
        '到时','历时','达日','商务座',
        '特等座','一等座','二等座',
        '二等包座','高级',
        '软卧','软卧',
        '一等卧','动卧','硬卧',
        '二等卧','软座','硬座','无座','其他','备注'
            ]
        save_list.append('|'.join(str(x) for x in header))
        for train_tr in train_trs:
            infos = train_tr.text.replace('\n', ' ').split(' ')
            # number = infos[0]  # 车次
            for keyword in infos:
                if keyword=='复':
                    infos.remove('复')
            
            save_list.append('|'.join(str(x) for x in infos))
        # print(save_list)
        return save_list


    def orderService(self):
        '''根据指令进行调用'''
        order_text = self.msg_dict['text_split']
        if order_text[0] !='#ttt':
            return 
        if len(order_text)>= 3:
            if order_text[1] == 'code':
                station_list = self.__getStationList(order_text[2]) # 传入车站名
                if station_list != []: return ','.join(str(x) for x in station_list)

            if order_text[1] == 'tic':
                fs, ts, dateraw = order_text[2].split('-')
                timeArray = time.strptime(dateraw, "%Y%m%d")
                otherStyleTime = time.strftime("%Y-%m-%d", timeArray)

                save_list = self.search_left_ticket(fs,ts,otherStyleTime)
                if save_list != []:
                    return '\n'.join(str(x) for x in save_list)
                
            if order_text[1] == 'sta':
                station_list = self.__getStationList(order_text[2], True) # 传入车站名
                if station_list != []: return ','.join(str(x) for x in station_list)




@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'\#ttt.*').flags(re.X)])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def Train(
    app: Ariadne, 
    message: MessageChain,
    group: Group,
    member: Member 
):

    slightly_inittext = MessageProcesser(message,group,member)
    msg_info_dict = slightly_inittext.text_processer()

    trainTong = TrainTong(msg_info_dict)
    if msg_info_dict['text_split'][0] !='#ttt': return 
    outtext = trainTong.orderService()

    if outtext != '' or outtext is not None:
        await app.send_group_message(group, MessageChain(
            Plain(outtext)
        ))


