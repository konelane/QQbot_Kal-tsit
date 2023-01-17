#! /usr/bin/env python3
# coding:utf-8

import sqlite3
from typing import Union
from kalrogue.utils.TextReceiver import TextReceiver
from kalrogue.utils.SaverLoader import SaverLoader
from kalrogue.game.Environment.GameSave import GameSave
from kalrogue.game.Environment.GameDoctor import GameDoctor
from kalrogue.game.Environment.GameTable import GameTable
from kalrogue.utils.DatabaseCheck import GameDatabase

from kalrogue.game.node import GameNode,ChoiceNode,DiceNode,HomeNode, EndNode
from kalrogue.utils.CreditDealer import CreditDealer
from kalrogue.resources.game.GameContants import (
    START_GAME_CREDIT_CONSUMPTION, AUTH_USER_LIST, TEST_USER_LIST, CREDIT_DICT)

class Move:
    ''' 基础行动类
    包含存档对象 与多个存档操作方法
    存档、故事节点结构 见resources/construct_readme.md

    '''
    def __init__(self, msg_dict) -> None:
        
        self.msg_dict = msg_dict
        self.group_id = msg_dict['group_id']
        self.save_list, self.save_length = self.searchGame()
        self.save_new_dir = "resources/saves/" + str(self.group_id) + "_" + str(self.save_length) + '.json' # 共有x个存档，则下一个存档为x号
        self.read_save_dir = "resources/saves/" + str(self.group_id) + "_" + str(max(0, self.save_length-1)) + '.json' # 默认最后一个存档
        self.newsave = GameSave()   # 保存的存档
        self.read_save = GameSave() # 读取的存档
        
        



    def saveSavesAuto(self, save_dir=None):
        '''存档
        默认存在最后一个已存在的文档中
        【CAUTION】若是新存档 一定要规定 save_dir
        @param
            save_dir : 文件名 "resources/saves/" 后面的.json
        '''
        if save_dir is None or save_dir == '':
            save_dir_full = self.read_save_dir
            save_length = self.save_length - 1
        else:
            save_dir_full = "resources/saves/" + save_dir
            saves, save_num = self.searchGame()
            if save_dir in saves:
                save_length = saves.index(save_dir)
            else:
                save_length = self.save_length - 1
        SaverLoader.jsonSaver(save_dir_full, self.read_save.toDict())
        self.setDefaultSave(save_length) # 默认最后一个为默认存档 更新sqlite
        
    
    def setDefaultSave(self, save_number):
        '''设置当前存档为默认存档
        @param
            save_number : 存档后面的数字, 长度-1
        '''
        save_dir = str(self.group_id) + "_" + str(save_number) + '.json'
        save_dict = GameDatabase.dataSearch(self.group_id)
        if save_dict is not None:
            save_dict['default_save'] = save_dir
        else:
            save_dict = {
                "changer_id":self.msg_dict['id'],
                "group_id":self.group_id,
                "default_save":save_dir,
                "creator_id":self.msg_dict['id'],
                "active_status":'ACTIVE'
            }    
        GameDatabase.dataSave(save_dict)
        



    def readDefaultSave(self):
        '''读取默认存档 - 与数据库交互'''
        save_dict = GameDatabase.dataSearch(self.group_id)
        if save_dict is None or self.save_list == []:
            print('save_dict is None OR self.save_list == []')
            return ''
        elif save_dict['default_save'] in self.save_list:
            print('[load]存档位于文件中', save_dict['default_save'], self.save_list)
            self.loadGame(self.save_list.index(save_dict['default_save']))
            return save_dict['default_save'] # 返回存档文件名
        elif save_dict['default_save'] not in self.save_list:
            print(save_dict['default_save'],'save_dict is not in self.save_list\n',self.save_list)
            self.loadGame(0) # 使用第0份存档
            self.setDefaultSave(0)
            return self.save_list[0]

        
    def saveNameOfDefaultSave(self):
        '''只返回默认存档的名称'''
        save_dict = GameDatabase.dataSearch(self.group_id)
        if save_dict is None or self.save_list == []:
            print('save_dict is None OR self.save_list == []')
            return ''
        elif save_dict['default_save'] in self.save_list:
            return save_dict['default_save'] # 返回存档文件名
        elif save_dict['default_save'] not in self.save_list:
            return self.save_list[0]


    def saveNewGame(self):
        '''建立新存档
        设置默认值 
        保存存档json
        设置默认存档为最后一个存档
        '''
        self.newsave.group_id = self.msg_dict['group_id']
        self.newsave.mode_list = ["normal"]   # TODO 待修改
        self.newsave.story_node_list = []
        self.newsave.credit_pool = 0
        self.newsave.is_end = 0
        self.newsave.endding_id = ""
        self.newsave.doctor_condition = GameDoctor().toDict()
        self.newsave.game_environment = GameTable().toDict()
        self.newsave.story_node_dict = {}

        SaverLoader.jsonSaver(self.save_new_dir, self.newsave.toDict())
        self.setDefaultSave(self.save_length) # 默认最后一个为默认存档 self.save_length 是保存前的，因此少1，正好
        

    def toStringOutText(self):
        '''将存档文件转化为展示文本'''
        save_dict = self.read_save.toDict()
        outtext = ''
        outtext += '[模组]' + ','.join(str(x) for x in save_dict["mode_list"])
        outtext += '\n[经过节点]' + ','.join(str(x) for x in save_dict["story_node_list"])
        outtext += '\n[信用池]' + str(save_dict["credit_pool"]) 
        outtext += '\n[神经连接者]' + ','.join(str(x) for x in save_dict["member_list"]) 
        outtext += '\n[故事是否结束]' + ('是, 结局编号为'+save_dict["endding_id"] if save_dict["is_end"]==1 else '否')
        outtext += '\n[生命值]' + str(save_dict["doctor_condition"]["hp"])
        outtext += '\n[背包]' + ','.join(
            save_dict["doctor_condition"]["bag_dict"][0][str(x)]["name"] for x in save_dict["doctor_condition"]["bag"]
        )
        outtext += '\n[同伴]' + ','.join(
            str(x) for x in save_dict["doctor_condition"]["friends"]
        )
        outtext += '\n[凯尔希怒气]' + str(save_dict["doctor_condition"]["kaltsit_anger"])
        return outtext







    def loadGame(self, save_number=None):
        '''读档-从文件读入内存
        默认-有存档
        如果没有输入save_number，则重新设置默认存档为0
        @param
            save_number : 文件后的数字
        '''
        if save_number is None or save_number == 0:
            read_save = SaverLoader.jsonReader(self.read_save_dir)
            self.setDefaultSave(0)
        else:
            self.read_save_dir = "resources/saves/" + str(self.group_id) + "_" + str(save_number) + '.json'
            read_save = SaverLoader.jsonReader(self.read_save_dir)
            # self.setDefaultSave(save_number)

        self.read_save.group_id = read_save['group_id']
        self.read_save.mode_list = read_save['mode_list']
        self.read_save.story_node_list = read_save['story_node_list']
        self.read_save.credit_pool = read_save['credit_pool']
        self.read_save.member_list = read_save['member_list']
        self.read_save.is_end = read_save['is_end']
        self.read_save.endding_id = read_save['endding_id']
        self.read_save.doctor_condition = read_save['doctor_condition']
        self.read_save.game_environment = read_save['game_environment']
        self.read_save.story_node_dict = read_save['story_node_dict']


    def searchGame(self):
        '''搜索存档'''
        save_list = SaverLoader.SaveChecker(self.msg_dict["group_id"])
        if save_list==[]: 
            return [], int(0)
        else:
            return save_list, len(save_list) # 返回存档数量


    def currentNode(self, node_name):
        '''建立当前节点的实例
        '''
        temp_node = GameNode(node_name)
        node_dict = temp_node.NodeLoader(node_name)
        if node_dict[node_name]['node_type'] == 'choice':
            return ChoiceNode(node_name)
        elif node_dict[node_name]['node_type'] == 'dice':
            return DiceNode(node_name)
        elif node_dict[node_name]['node_type'] == 'endding':
            return EndNode(node_name)
        else: 
            return GameNode(node_name)
        
    def getNodeNameofCurrent(self):
        '''返回最新的节点名称'''
        if len(self.read_save.story_node_list)>0:
            return self.read_save.story_node_list[-1]
        

    def updateNodeSave(self, node_obj: GameNode):
        '''根据node对象更新存档的story_node
        更新两处 story_node_dict与story_node_list
        更新规则: 
            1.节点名称未曾出现过 - 更新
            2. 节点名称出现过，但并非最近的节点 - 更新
            其他情况 - 不更新
        '''
        node_dict_save = node_obj.toDictSave()
        self.read_save.story_node_dict[node_obj.node_name] = node_dict_save
        if node_obj.node_name not in self.read_save.story_node_list:
            self.read_save.story_node_list.append(node_obj.node_name) # 如果不存在 再进行更新
        elif node_obj.node_name != self.read_save.story_node_list[-1]:
            self.read_save.story_node_list.append(node_obj.node_name) # 如果存在，只要不是上一个节点的相同节点 即更新
        self.read_save.story_node_dict[node_obj.node_name][node_obj.node_name]["position_save"] = node_obj.position
        

    def updateNodePositionCreate(self, node_obj: GameNode):
        '''根据存档更新node_obj的信息 - 必须已存在
        node_obj.position
        '''
        position_save = self.read_save.story_node_dict[node_obj.node_name][node_obj.node_name]["position_save"]
        node_obj.position = position_save
        node_obj.node_json[node_obj.node_name]['position_save'] = position_save
        return node_obj

    def nextMoveAction(self, node_obj: Union[ChoiceNode, DiceNode]):
        '''核心方法 读取并进行下一步动作 
        理论上应执行至需要Input的步骤停止
        
        '''
        outtext = ''
        while not node_obj.isNodeDone():
            # 获取next move
            next_move_order = node_obj.nextMove(self.read_save)
            print('执行node', node_obj.node_name, node_obj.node_json[node_obj.node_name]['node_type'])
            if next_move_order == 'choice':
                outtext += node_obj.specialText()
                break
            elif next_move_order == 'dice':
                outtext += node_obj.specialText()
                break 
            elif next_move_order == 'auto':
                outtext += node_obj.autoText()
                
                pass 
            elif next_move_order == 'rqmt':
                outtext += '===============\n【check】\n未达到check条件。'
                break

        # 阻断后当保存
        node_obj.updateNodePosition(max(0, node_obj.position)) # TODO
        print('[isRewardExist]',node_obj.isRewardExist(), node_obj.position)
        if node_obj.isRewardExist():
            if_reward_exist, reward_text, reward_type, self.read_save = node_obj.rewardMove(node_obj.rewardTypeCheck(), self.read_save)
            if reward_type =='endding':
                print("[END]游戏结局")
                self.checkIsEndding(node_obj) # 更改游戏结局情况
                end_json = SaverLoader.jsonReader("resources/enddings/"+reward_text+".json")
                
                outtext += end_json["content"]
                pass # 若为结局节点 - 单独执行一下结局文本（看看怎么设计 TODO
        self.checkIsEndding(node_obj) # 检查并更改游戏结局情况
        self.updateNodeSave(node_obj)

        return outtext

    
    def choiceMove(self, input_choice, node_obj: ChoiceNode):
        '''选择节点进行选择后的行动
        @param
            input_choice : 选择结果指令 "0"
            node_obj : 选择节点对象
        @out
            tuple[文本, 内容, 内容类型]
        '''
        if node_obj.nextMove(self.read_save) == 'choice':
            out_list = node_obj.inputChoice(input_choice, self.read_save) # out_list [choice结果, 结果的类型, 注释]
            node_obj.updateNodePosition()
            outtext = self.nextMoveAction(node_obj)
            return outtext, out_list[0], out_list[1]
        
        return '', None, 'None'


    def diceMove(self, node_obj: DiceNode):
        '''选择节点进行选择后的行动
        @param
            node_obj : 选择节点对象
        @out
            tuple[文本, 内容, 内容类型]
        '''
        
        if node_obj.nextMove(self.read_save) == 'dice':
            outtext, result_text, result_type= node_obj.inputDice(self.read_save)
            node_obj.updateNodePosition()
            outtext += self.nextMoveAction(node_obj)
            return outtext, result_text, result_type
        else:
            return '', None, 'None'
    

    def checkIsEndding(self, node_obj: GameNode):
        '''检查当前节点是否使游戏结束 + 修改节点与存档状态

        '''
        if self.read_save.is_end == 1:
            return True

        if node_obj.node_json[node_obj.node_name]["node_type"] == 'endding':
            self.read_save.is_end = 1 # 更改游戏结局情况
            self.read_save.endding_id = node_obj.updateEndding()  # 更新endding_id
            return True

        return False
        

    # =====================
    # 权限检验
    # =====================

    def authCheck(self, member_id, check_type='GM'):
        '''检查权限
        @param
            member_id : 进行权限检查的账号
            check_type : 
                1. GM 游戏挂壁权限 AUTH_USER_LIST
                2. TEST 游戏测试者权限 TEST_USER_LIST
        '''
        if check_type == 'GM':
            return member_id in AUTH_USER_LIST
        if check_type == 'TEST':
            return member_id in TEST_USER_LIST


    def diceCheatMove(self, node_obj: DiceNode, point_cheat):
        '''dice的作弊者行动
        @param
            node_obj : 选择节点对象
            point_cheat : 需要的点数
        @out
            tuple[文本, 内容, 内容类型]
        '''
        
        if node_obj.nextMove(self.read_save) == 'dice':
            outtext, result_text, result_type= node_obj.cheatDiceWithInput(self.read_save, point_cheat)
            
            node_obj.updateNodePosition()
            outtext += self.nextMoveAction(node_obj)
            return outtext, result_text, result_type
        else:
            return '', None, 'None'
    

    # =====================
    # 信用流程
    # =====================
    
    def creditDiff(self, credit_type='start'):
        '''求当前信用池与设定的需要值差距 feiqi'''
        if credit_type == 'start':
            return self.read_save.game_environment["credit_pool_need"] - self.read_save.credit_pool
        
        
    def isCreditisEnough(self, credit_type='start'):
        '''信用 是否足够'''
        if credit_type == 'start':
            return START_GAME_CREDIT_CONSUMPTION <= int(self.read_save.credit_pool)
        elif credit_type == 'dice':
            return CREDIT_DICT['dice_consume'] <= int(self.read_save.credit_pool)
        elif credit_type == 'choice':
            return CREDIT_DICT['choice_consume'] <= int(self.read_save.credit_pool)
        

    def ifPlayerInMemberList(self):
        '''检查玩家是否存在于member_list'''
        print('[check]检查玩家',self.msg_dict["id"])
        return self.msg_dict["id"] in self.read_save.member_list or int(self.msg_dict["id"]) in self.read_save.member_list


    def creditChangeMove(self, credit_change: int):
        '''众筹行动 修改信用值 [不含保存]
        0. 校验是否满足条件 管理员or足够的信用
        1. 修改玩家信用
        2. 修改总信用池
        @param
            credit_change : 传入的信用值 必须为int值。
        '''
        outtext = ''
        if credit_change >= CREDIT_DICT['member_credit_limit'] or self.authCheck(self.msg_dict["id"], 'TEST') :
            if not self.authCheck(self.msg_dict["id"], 'TEST'):
                # 消耗非测试玩家信用
                credit_dealer = CreditDealer(self.msg_dict)
                credit_dealer.CreditAction(credit_change) # #kr cr 20 指消耗20信用
                outtext += '**GUEST**'
            # 修改存档信用池
            self.read_save.credit_pool += credit_change
            outtext += '信用筹集成功。'
            # 若当前玩家不在操作者名单中
            if not self.ifPlayerInMemberList():
                self.read_save.member_list.append(self.msg_dict["id"])
                print('[神经连接]',self.read_save.member_list)
                outtext += '\n已添加至神经连接列表。'
                
        else:
            # 消耗玩家信用
            credit_dealer = CreditDealer(self.msg_dict)
            credit_dealer.CreditAction(int(credit_change)) # #kr crd 20 指消耗20信用
            # 为存档信用池添加信用
            self.read_save.credit_pool += int(credit_change)
            outtext += '信用筹集成功。' 

        return outtext


    def normalMoveCreditCheckMove(self, move_type='choice'):
        '''普通行动(非众筹)中的信用 检查 与 修改 [不含保存]
        @param
            move_type : 行动类型 - 根据行动类型进行信用收取
                    dice - dice_consume
                    choice - choice_consume
        @output
            False/True, outtext
        '''
        outtext = ''

        if not self.ifPlayerInMemberList() and not self.authCheck(self.msg_dict["id"], 'TEST'):
            member_credit_limit = CREDIT_DICT['member_credit_limit']
            outtext = f'博士，你需要一次性支付{str(member_credit_limit)}信用才能参与故事决策行动。'
            return False, outtext
        
        if move_type == 'dice':
            credit_consume = CREDIT_DICT['dice_consume']
        elif move_type == 'choice':
            credit_consume = CREDIT_DICT['choice_consume']

        if not self.authCheck(self.msg_dict["id"], 'TEST'):
            # 检查信用池是否充足
            if not self.isCreditisEnough(move_type):
                outtext = '本群当前存档信用池已不足下一次行动，需要筹集信用。'
                return False, outtext
            else:
                # 从存档信用池 减少信用
                self.read_save.credit_pool -= int(credit_consume)
                outtext = f'****本次行动信用消耗{str(credit_consume)}，已自动支付****'
                return True, outtext

        else:
            # 测试账号权限
            outtext = f'****本次行动信用消耗{str(credit_consume)}，已自动支付****'
            return True, outtext