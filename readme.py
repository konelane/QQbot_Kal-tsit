#! /usr/bin/env python3
# coding:utf-8

######### Readme Document #########
### arknights homework bot V2.1 ###
###      Author: KOneLane       ###
###    Engine&Support: Mirai    ###
###   Latest Update: 21.09.06   ###


print("博士，你好，我是Kal'tsit")
print()
print('别紧张，我只是碰巧路过你的办公室。')
print('【帮助】输入#help可以查看所有可用的命令') # 即 运行当前文档
print('【作业】输入#hw可以抽取一次群作业，今天的工作也很繁忙。')
print('【表扬】输入#praise大概可以被机器人关爱，你不会这么无聊的对吧。')
# print('')
# print('-----------跑团-----------')
# print('这种麻烦事以后别来找我，可露希尔或许会感兴趣。')
# print('【车卡】干员初始化请输入#初始化 姓名 魅力 敏捷 强度 智力')
# print('demo:#初始化 doctor 1 2 3 4')
print('【掷骰】请输入.r ndx，其中n是骰子数量，x是骰子面数。')
# print('demo:.r 3d8')
# print('【读取】干员/博士数据请输入#读取 干员/博士名称')
# print('demo:#读取 doctor')
# print('【检定】请输入#检定 姓名 项目【项目包括:charm(魅力),agile(敏捷),strength(强度),intelligence(智力)】')
# print('demo:#检定 doctor agile')
# print('【背包操作】请输入#背包 姓名 操作内容【操作内容包括:增加 xx,减少 xx,使用 xx,查询 xx(xx为物品名称)】')
# print('demo:#背包 doctor 查询 热水壶')
# print('【经验增加】请输入#经验 姓名 数值')
# print('demo:#经验 doctor 1000')
# print()
print('-----------PRTS-----------')
print('我可以帮你查一些简单的信息……但请不要依赖这一点，我很忙。')
print('【PRTS查询】输入#prts 干员名称 项目【包括：技能专精,晋升材料,属性,后勤,生日】')
print('demo:#prts 德克萨斯 技能专精')
print('【天气】输入#天气 龙门 今日【目前开放了今日】')
print('【地图】输入#地图 龙门 500【500表示显示周围500范围】')
# print('--------cos干员--------')
# print('权限系统、爬虫性能优化、建立数据库')
print('-----最新更新于0906-----')
print('项目地址:https://github.com/konelane/QQbot_Kal-tsit')
# print('权限系统【已配置未实装】、爬虫性能优化【done！】')
# print('建立数据库【done！】、天文爱好者天气/星象预报【开发中】、优化功能触发模块【未开始】')
print('-----------EOF--生日21.05.12-----------')

## 更新记录 21.09.06
## 优化bot文件目录
# |---MessageProcessor # 消息标准化处理中心
# |---bot2             # bot主体启动文件
# |---AuthSet          # 权限系统
# |---story_xu         # 核心函数
# |---readme           # 代码介绍
# |---database: 
# |---|---Kal-tsit.db  # 数据库
# |---|---beijing.pkl  # 地图文件
# |---|---temp.png     # 缓存
# |---function：
# |---|---prts                 # prts功能
# |---|---ForcastForTricks     # 天气预报功能
# |---|---DarkTemple           # 消息处理器
# |---|---squads_init          # 初始化干员
# |---|---operator_rollbox_bot # 群作业系统
# 
# 愿世界永葆和平。