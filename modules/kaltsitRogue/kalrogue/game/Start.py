#! /usr/bin/env python3
# coding:utf-8
'''
    start game
        1. 检查信用池，启动信用收集器【暂不开发】
        
        3. 载入mode【暂不开发 默认normal】

        9. 建立新存档 - 初始化存档
        
'''
from kalrogue.game.Environment.GameDoctor import GameDoctor
from kalrogue.resources.game.GameContants import (
    HP_INIT, MODE_INIT_SET, START_GAME_CREDIT_CONSUMPTION )
from kalrogue.game.Environment.GameSave import GameSave
from kalrogue.utils.SaverLoader import SaverLoader
from kalrogue.game.Move import Move
from kalrogue.utils.CreditDealer import CreditDealer


class StartGame:
    def __init__(self, msg_info) -> None:
        self.msg_info = msg_info
        self.start_game_credit_consumption = START_GAME_CREDIT_CONSUMPTION  # 信用消耗为常量
        self.group_id = msg_info["group_id"]    # 群号
        self.id = msg_info["id"]          # 创建人id
        self.mode_list = []  # 模组
        self.credit_pool = 0
        self.doctor = GameDoctor().toDict()
        self.credit_dealer = CreditDealer(msg_info)
        self.move_obj = Move(msg_info)
        
        pass





    def CollectCredit(self):
        '''收集信用 - 总信用放入存档中'''
        if self.move_obj.isCreditisEnough():
            pass
            
            
        else:
            # todo 要写一个结局来着
            pass 


    def isExistSaves(self):
        '''检查是否存在存档
        @output
            saves : list of save files
            bool : T | F
        '''
        # 检查有无存档
        saves, save_num = self.move_obj.searchGame()
        if save_num == 0:
            
            return [] , False
        else:
            # 选择默认存档
            # save_filename = self.move_obj.readDefaultSave()
            return saves, True


    def initDoctor(self, game_init_dict=None, game_mode='normal'):
        '''更新博士情况 - Environment.GameDoctor
        '''
        if game_mode=='normal':
            self.doctor['hp'] = HP_INIT
            # self.doctor.setFriend
        else:
            self.doctor['hp'] = MODE_INIT_SET[game_mode]['hp_init']


    def newSave(self):
        '''建立新存档 新游戏专用'''
        self.move_obj.saveNewGame()
        
    def loadSave(self):
        '''读取存档'''
        self.move_obj.readDefaultSave() # 更新了self.move_obj.read_save


    def saveTheSave(self, save_filename=None):
        '''进行存档 - 不用检查有无存档 
        只需根据save_filename是否为空即可
        默认初次创建保存在0结尾的json文件里
        @param
            save_filename : json文件名
        '''
        if save_filename is not None:
            self.move_obj.saveSavesAuto(save_filename)
            print('StartGame 存档成功', save_filename)
        else:
            self.move_obj.saveSavesAuto()
            print('StartGame 初存档成功')


    def startNewNode(self):
        '''创建新intro节点 ChoiceNode
        指定的intro节点 类型为choice
        '''
        node_name = 'home-intro'
        homeNode = self.move_obj.currentNode(node_name) # 节点实例ChoiceNode

        self.move_obj.updateNodeSave(homeNode) # 更新存档
        return homeNode


    def startCurrentNode(self):
        '''根据存档创建新node类
        '''
        node_name = self.move_obj.getNodeNameofCurrent()
        current_node = self.move_obj.currentNode(node_name)
        current_node = self.move_obj.updateNodePositionCreate(current_node)
        return current_node



    def start(self):
        '''启动新游戏 创建存档
        检查有无存档 有无-两种新建方式
        '''
        
        # 启动游戏
        self.newSave() # 保存新存档
        home_node = self.startNewNode()
        self.initDoctor()
        self.move_obj.updateNodeSave(home_node)

        self.saveNewWithCheckDefaultSave()



    def moveToNewNode(self, node_name):
        '''移动至新节点 并保存
        有保存！保存！
        '''
        # 传回的为节点名称
        new_story_node = self.move_obj.currentNode(node_name) # 节点实例
        self.move_obj.updateNodeSave(new_story_node) # 更新存档
        
        self.saveNormalInDefaultSave()


    def saveNormalInDefaultSave(self):
        '''默认档 存档入口'''
        save_dir = self.move_obj.saveNameOfDefaultSave()
        if save_dir != '':
            print('默认档 ', save_dir)
            self.saveTheSave(save_dir)
        else:
            print('新档')
            self.saveTheSave()


    def saveNewWithCheckDefaultSave(self):
        '''新档 更新新存档入口'''
        save_list, is_exist_saves = self.isExistSaves()
        if is_exist_saves:
            save_json_dir = str(self.group_id) + "_" + str(len(save_list)-1) + '.json'
            print('新档 ', save_json_dir)
            self.saveTheSave(save_json_dir)
        else:
            print('新档 存档入口')
            self.saveTheSave() # 创建新存档 - 需要检查默认存档情况


    