#! /usr/bin/env python3
# coding:utf-8

import os
import re  # 字符处理
from os.path import basename
import random

import osmnx as ox
import json

from core.config.BotConfig import AdminConfig
from core.decos import DisableModule, check_group, check_member, check_permitGroup
from core.MessageProcesser import MessageProcesser
from core.ModuleRegister import Module
from core.Text2Img import generate_img
from database.kaltsitReply import blockList, text_table
from geopy.geocoders import Nominatim  # 20230618超时问题无法解决
from geopy.geocoders import GoogleV3
import requests
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, Plain
from graia.ariadne.message.parser.twilight import RegexMatch, Twilight
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from prettytable import PrettyTable

channel = Channel.current()

module_name = basename(__file__)[:-3]

Module(
    name='ForcastForTricks',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.ForcastForTricks',
).register()



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

    def __location_get_aborted(self):
        """获取指定地名的经纬度 并更新类变量"""
        geolocator = Nominatim(user_agent="kal-tsit")
        location = geolocator.geocode(self.text[1])
        if not location:
            return
        else:
            self.lon = location.longitude
            self.lat = location.latitude
            return 'updated'

    def __location_get(self):
        """使用高德api获取经纬度，限制5000次1天"""
        url = 'https://restapi.amap.com/v3/geocode/geo?' + 'key=' + AdminConfig().GAODE_KEY + '&address=' + self.text[1]
        res = requests.get(url)
        if res.content is not None:
            location = json.loads(res.content)['geocodes'][0]['location'].split(',')
            self.lon = float(location[0])
            self.lat = float(location[1])
            return 'updated'
        return



    def __url_sky_get(self):
        """天气json数据获取"""
        # try:
        self.__location_get() # 先更新
        url= f'https://www.7timer.info/bin/api.pl?lon={str(self.lon)}&lat={str(self.lat)}&product={self.product}&output={self.output}&tzshift=8'#存储API调用的URL
        # print(url, self.lon, self.lat)
        r=requests.get(url) #获得URL对象
        # print("Status code:",r.status_code) #判断请求是否成功（状态码200时表示请求成功）
        response_dict=r.json()

        return response_dict
        # except:
        #     return 'timeout'

    def __map_get(self):
        """画地图"""
        if self.__location_get():
        # G = pickle.load(open('database/beijing.pkl','rb'))
        # loc_node = ox.get_nearest_node(G, (self.lat,self.lon))
            inputnum = int(self.text[2])
            if inputnum > 1000:
                inputnum = 1000
        # 联网条件
            G = ox.graph_from_point((self.lat,self.lon), dist=inputnum, network_type='all')
            if os.path.exists('C:/Users/Administrator/bot/database/temp_map.png'):
                os.remove('C:/Users/Administrator/bot/database/temp_map.png')
            ox.plot_graph(G,show=False,save=True,filepath='C:/Users/Administrator/bot/database/temp_map.png')
            return 'map'
        else:
            return '地点不存在'



    def machine_read_picture(self, dict_of_data):
        '''API返回的指标值对应的气象标签 - need package PrettyTable'''
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
        level_dict = {
            'cloudcover':{
                '1':'0-6%',
                '2':'6-19%',
                '3':'19-31%',
                '4':'31-44%',
                '5':'44-56%',
                '6':'56-69%',
                '7':'69-81%',
                '8':'81-94%',
                '9':'94-100%'
            },
            'seeing':{
                '1':	'<0.5"',
                '2':	'0.5"-0.75"',
                '3':	'0.75"-1"',
                '4':	'1"-1.25"',
                '5':	'1.25"-1.5"',
                '6':	'1.5"-2"',
                '7':	'2"-2.5"',
                '8':	'>2.5"'
            },
            'transparency':{
                '1':	'<0.3',
                '2':	'0.3-0.4',
                '3':	'0.4-0.5',
                '4':	'0.5-0.6',
                '5':	'0.6-0.7',
                '6':	'0.7-0.85',
                '7':	'0.85-1',
                '8':	'>1'
            },
            'rh2m':{
                '-4'	:'0-5%',
                '-3'	:'5-10%',
                '-2'	:'10-15%',
                '-1'	:'15-20%',
                '0'	    :'20-25%',
                '1'	    :'25-30%',
                '2'	    :'30-35%',
                '3'	    :'35-40%',
                '4'	    :'40-45%',
                '5'	    :'45-50%',
                '6'	    :'50-55%',
                '7'	    :'55-60%',
                '8'	    :'60-65%',
                '9'	    :'65-70%',
                '10'	:'70-75%',
                '11'	:'75-80%',
                '12'	:'80-85%',
                '13'	:'85-90%',
                '14'	:'90-95%',
                '15'	:'95-99%',
                '16'	:'100%'
            },
            'wind10m_speed':{
                '1'	:'Below 0.3m/s',
                '2'	:'0.3-3.4m/s',
                '3'	:'3.4-8.0m/s',
                '4'	:'8.0-10.8m/s',
                '5'	:'10.8-17.2m/s',
                '6'	:'17.2-24.5m/s',
                '7'	:'24.5-32.6m/s',
                '8'	:'Over 32.6m/s'
            },
            'lifted_index':{
                '-10'	:'Below -7',
                '-6'	:'-7 to -5',
                '-4'	:'-5 to -3',
                '-1'	:'-3 to 0',
                '2'	    :'0 to 4',
                '6'	    :'4 to 8',
                '10'	:'8 to 11',
                '15'	:'Over 11'
            }
        }
        x = PrettyTable(['时间','云量','视宁','透明','湿度'])
        x.padding_width = 1  # 填充宽度
        for forcast_dict in dict_of_data:
            x.add_row([
                int(forcast_dict['timepoint']/2),
                level_dict['cloudcover'][str(forcast_dict['cloudcover'])],
                level_dict['seeing'][str(forcast_dict['seeing'])],
                level_dict['transparency'][str(forcast_dict['transparency'])],
                level_dict['rh2m'][str(forcast_dict['rh2m'])],

            ])

        # y = PrettyTable(['时间','湿度','温度','风向'])
        # y.padding_width = 1  # 填充宽度
        # for forcast_dict in dict_of_data:
        #     y.add_row([
        #         forcast_dict['timepoint'],
        #         level_dict['rh2m'][str(forcast_dict['rh2m'])],
        #         forcast_dict['temp2m'],
        #         forcast_dict['wind10m']['direction'],
        #     ])

        z = PrettyTable(['时间','温度','风向','风速','稳定','预警'])
        z.padding_width = 1  # 填充宽度
        for forcast_dict in dict_of_data:
            z.add_row([
                int(forcast_dict['timepoint']/2),
                forcast_dict['temp2m'],
                forcast_dict['wind10m']['direction'],
                level_dict['wind10m_speed'][str(forcast_dict['wind10m']['speed'])],
                level_dict['lifted_index'][str(forcast_dict['lifted_index'])],
                forcast_dict['prec_type']
            ])


        return x,z



    def orderToReturn(self):
        """根据指令返回"""
        # add_text = '时间: 距现在小时'

        if self.text[0] == '#地图':
            return self.__map_get()
        if self.text[0] == '#天气':
            if self.text[2] in ['今天','1','今日','一日']:
                ans_dict = self.__url_sky_get()
                if ans_dict == 'timeout':
                    return 'timeout'
                else:
                    outputx,outputz = self.machine_read_picture(ans_dict['dataseries'][1:17:2])
                    generate_img(
                        [str(self.text[1]) + '的天气预测如下：','\n',str(outputx),'\n',str(outputz)],
                        img_path = os.path.join('bot/database/temp_forcast.jpg')#,
                        # img_type = 'forcast'
                    )
                    return



@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'\#天气.*|\#地图.*').flags(re.X)])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def Forcast_app(
    app: Ariadne,
    message: MessageChain,
    group: Group,
    member: Member
):

    slightly_inittext = MessageProcesser(message,group,member)
    msg_info_dict = slightly_inittext.text_processer()
    text_list = msg_info_dict['text_split'] # 做判断用的
    if len(text_list) == 3 and text_list[0] == '#天气':


        forcast = ForcastForTricks(msg_info_dict)
        abc = forcast.orderToReturn()
        # print(abc)
        if abc == None:
            img_path = os.path.join('bot/database/temp_forcast.jpg')

            await app.send_group_message(group, MessageChain(
                Plain(random.sample(text_table,1)[0]),
                Image(path=img_path)
            ))
        elif abc == 'timeout':
            await app.send_group_message(group, MessageChain(
                Plain('终端连接超时了，博士，过会再试试。')
            ))

    elif len(text_list) == 3 and text_list[0] == '#地图':
        forcast = ForcastForTricks(msg_info_dict)
        abc = forcast.orderToReturn()

        if abc == 'map':

            await app.send_group_message(group, MessageChain(
                Plain(random.sample(text_table,1)[0]),
                Image(path='C:/Users/Administrator/bot/database/temp_map.png')
            ))
        elif abc == '地点不存在':
            await app.send_group_message(group, MessageChain([
                Plain('数据库中没有记录，你或许可以试试更加古老的方式。')
            ]))

