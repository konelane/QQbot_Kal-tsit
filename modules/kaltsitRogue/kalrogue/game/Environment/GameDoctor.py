#! /usr/bin/env python3
# coding:utf-8
from kalrogue.utils.SaverLoader import SaverLoader
from kalrogue.resources.game.GameContants import *

class GameDoctor:
    '''博士状态'''
    def __init__(self) -> None:
        self.hp = HP_INIT
        self.coc5={
            "str":60,  # 力量
            "dex":60,  # 敏捷
            "pow":60,  # 意志
            "con":60,  # 体质
            "app":60,  # 外貌
        },
        self.bag = ["kaltsit-coffee-cup"]
        self.bag_dict={
            "origin_cash":{             # eg.源石锭
                "name":"精炼源石锭",     # 名称
                "amt":0,                # 数量
                "type":"consumption",   # 类型 消耗品
            }, 
            "kaltsit-coffee-cup" :{
                "name":"凯尔希的咖啡杯",
                "amt":1,                # 数量
                "type":"keyitem",   # 类型 消耗品
            }
        },
        self.friends = ["amiya"]
        self.friends_dict={
            "amiya":{
                "reliance":0,           # 信赖
                "anger":0,              # 怒气【特殊属性存放于干员json中】
                "san_point":100,        # san值
                "position":"术师",      # 职业
            },
            
        },
        self.kaltsit_anger = 0
        
        
        
    def setCoc5(self, coc5_dict):
        '''设定coc5值
        @param coc5_dict: 
            {
                "str":60,  # 力量
                "dex":60,  # 敏捷
                "pow":60,  # 意志
                "con":60,  # 体质
                "app":60,  # 外貌
            }
        '''
        self.coc5.update(coc5_dict)
        return self.coc5


    def setFriend(self, opt_name, opt_dict=None, opt_type="new"):
        '''修改朋友'''
        if opt_type=='new':

            self.friends.append(opt_name)
            self.friends_dict[opt_name] = SaverLoader.jsonReader('resources/elements/operators.json')["operator"][opt_name]

        elif opt_type=='update' and opt_dict is not None:
            self.friends_dict.update(opt_dict) # 更新干员list

    
    def setBag(self, item_name, item_dict=None, item_type="new"):
        '''修改背包'''
        if item_type=='new':

            self.friends.append(item_name)
            self.friends_dict[item_name] = SaverLoader.jsonReader('resources/elements/item.json')["item"][item_name]

        elif item_type=='update' and item_dict is not None:
            self.friends_dict.update(item_dict) # 更新干员list


    def toDict(self):
        return {
            "hp":self.hp,
            "coc5":self.coc5,
            "bag":self.bag,
            "bag_dict":self.bag_dict,
            "friends":self.friends,
            "friends_dict":self.friends_dict,
            "kaltsit_anger":self.kaltsit_anger
        }