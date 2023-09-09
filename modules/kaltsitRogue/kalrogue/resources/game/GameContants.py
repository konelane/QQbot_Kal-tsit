#! /usr/bin/env python3
# coding:utf-8
'''
game contants 游戏设置常量
'''
from core.config.BotConfig import AdminConfig

# start_game_credit_consumption = 100 # 开启新游戏所需要的的信用值
START_GAME_CREDIT_CONSUMPTION = 0

HP_INIT = 10
# hp_init=10
#其他模式的初始属性
MODE_INIT_SET = {
    "story_or_mode_name":{
        "hp_init":1
    }
}

AUTH_USER_LIST = [
    AdminConfig().masterId
]
TEST_USER_LIST = [
    591016144

]

CREDIT_DICT = {
    'member_credit_limit':0,
    'start_consume':0,
    'dice_consume':0,
    'choice_consume':0
}