#! /usr/bin/env python3
# coding:utf-8
'''
提供凯尔希rogue的使用入口
'''

import sys
import os
sys.path.append(os.path.dirname(__file__))

from game.Move import Move
from game.Start import StartGame

class kalrogueService:
    ''' 
        流程读写器 - 核心驱动部分
        order_status
            0 : 启动 = 查询记录 - 有记录：加载/无记录：进入新建流程
            1 : 文本放送 = 查询剩余文本 - 发送 - 保存放送进度 - 至文本放送完毕
            2 : 
            3 : 选择 = 进入选择节点 - 接收选择 - 执行结果
            4 : 展示内容 = 群情况 包含默认存档、参与成员、进度、博士状态 并且关闭模块 【todo】
            5 : 筹信用 = 输入信用 - 汇入群信用池 【todo】
            6 : 设置默认存档 = 设置默认存档的尾数
            7 : 掷骰子 = 掷骰子节点的行动
            8 : 帮助 = 展示指令
            9 : 【管理员限定】作弊功能 = d + 数字 - 骰子 
    '''
    def __init__(self, msg_info) -> None:
        self.msg_info = msg_info
        self.group_id = msg_info["group_id"]
        self.member_id = msg_info["id"]
        pass

    
    def orderTrans(self):
        '''指令转换方法
        '''
        if self.msg_info['text_split'][1] == 'crd':
            return "5" # 信用筹集 
        elif self.msg_info['text_split'][1] == 'new':
            return "0" # 新游戏
        elif self.msg_info['text_split'][1] == 'go':
            return "1" # 进行文本内容
        elif self.msg_info['text_split'][1] == 'ch':
            return "3" # 选择
        elif self.msg_info['text_split'][1] == 'show':
            return "4" # 展示存档内容
        elif self.msg_info['text_split'][1] == 'sav':
            return "6" # 默认存档修改
        elif self.msg_info['text_split'][1] == 'd':
            return "7" # 掷骰子
        elif self.msg_info['text_split'][1] == 'help':
            return "8" # 展示指令
        elif self.msg_info['text_split'][1] == 'cheat':
            return "9" # 【作弊者】作弊功能
        elif self.msg_info['text_split'][1] == 'del':
            return "10" # 删除存档 - 暂不使用
        
        


    def run(self, order_status):
        start_obj = StartGame(self.msg_info)
        print('kaltsit rogue 执行群号:',str(start_obj.move_obj.group_id))
        '''
        行动前check 
            1. 是否在游玩用户名单中
            2. 信用池情况 - 某些行动需要消耗信用
        '''


        if order_status == '0':

            start_obj.start()
            return '创建存档成功'

        elif order_status == '1':
            # kr go
            start_obj.loadSave()
            current_node = start_obj.startCurrentNode()
            
            # 如果是刚刚建立的存档，第一步应该检查信用
            if current_node.node_name == 'home-intro' and len(start_obj.move_obj.read_save.story_node_list) == 1:
                if not start_obj.move_obj.isCreditisEnough(credit_type='start'):
                    return '存档信用不够，需要先筹集信用。'
            

            # 执行默认步骤
            if current_node.node_type == 'autotext':
                outtext = start_obj.move_obj.nextMoveAction(current_node)
                # 自动文档直接进入下一节点
                print('[下一节点]',current_node.next_node_id)
                start_obj.moveToNewNode(current_node.next_node_id)
            else:
                outtext = start_obj.move_obj.nextMoveAction(current_node)
            start_obj.saveNormalInDefaultSave()
            
            return outtext


        elif order_status == '3':
            # kr ch 0
            start_obj.loadSave()
            current_node = start_obj.startCurrentNode()

            # 传入选择
            if len(self.msg_info['text_split']) >= 3:
                # 信用
                credit_result, outtext_credit = start_obj.move_obj.normalMoveCreditCheckMove('choice') # 此处修改了信用
                if not credit_result: return outtext_credit # 若未能通过信用检查，则返回

                outtext, choice_result, choice_result_type = start_obj.move_obj.choiceMove(self.msg_info['text_split'][2], current_node)
                if choice_result_type == 'node_name':
                    # 传回的为节点名称
                    print('选择 ',choice_result,'节点')
                    start_obj.moveToNewNode(choice_result)
                
                outtext += '\n'
                outtext += outtext_credit
                return outtext


        elif order_status == '4':
            # kr show
            start_obj.loadSave()
            current_node = start_obj.startCurrentNode()

            outtext = start_obj.move_obj.toStringOutText()
            return outtext



        elif order_status == '5':
            # kr crd x
            start_obj.loadSave()
            current_node = start_obj.startCurrentNode()

            outtext = ''
            if len(self.msg_info['text_split']) >= 3 and str(self.msg_info['text_split'][2]).isdigit():
                # 进入筹集信用流程
                outtext = start_obj.move_obj.creditChangeMove(int(self.msg_info['text_split'][2]))
                # 保存
                start_obj.saveNormalInDefaultSave()
            else:
                outtext = '信用筹集失败，请检查输入。'
            
            return outtext
            


        elif order_status == '6':
            # kr sav (show)
            if len(self.msg_info['text_split']) >= 3:
                if self.msg_info['text_split'][2] == 'show':
                    return start_obj.move_obj.readDefaultSave()
                else:
                    start_obj.move_obj.setDefaultSave(self.msg_info['text_split'][2])
                    return '默认存档序号已变更为' + self.msg_info['text_split'][2]


        elif order_status == '7':
            # kr d
            start_obj.loadSave()
            current_node = start_obj.startCurrentNode()

            # 信用
            credit_result, outtext_credit = start_obj.move_obj.normalMoveCreditCheckMove('dice') # 此处修改了信用
            if not credit_result: return outtext_credit # 若未能通过信用检查，则返回

            # 传入骰子
            outtext, dice_result, dice_result_type = start_obj.move_obj.diceMove(current_node)
            if dice_result_type == 'node_name':
                # 传回的为节点名称
                start_obj.moveToNewNode(dice_result)

            outtext += '\n'
            outtext += outtext_credit
            return outtext



        elif order_status == '8':

            outtext = '【指令】罗德岛午夜逸闻 指令表\n'
            outtext += '查看指令 #kr help\n'
            outtext += '*新建存档 #kr new\n'
            outtext += '*继续前进 #kr go\n'
            outtext += '*展示存档 #kr show\n\n'
            
            outtext += '*进行选择[消耗50点]\n#kr ch 0[1,2,...]\n'
            outtext += '*进行掷骰子[消耗50点]\n#kr d\n'
            outtext += '*信用众筹x点 #kr crd x\n\n'

            outtext += '设置默认存档编号(变更当前存档) #kr sav 0[1,2,...]\n'
            outtext += '查看当前默认存档 #kr sav show\n'
            
            return outtext

        elif order_status == '9':
            '''【作弊者】
                #kr cheat 100
            '''
            start_obj.loadSave()
            current_node = start_obj.startCurrentNode()
            # 传入骰子
            if start_obj.move_obj.authCheck(self.member_id) and len(self.msg_info['text_split']) >= 3: # 检查gm
                outtext, dice_result, dice_result_type = start_obj.move_obj.diceCheatMove(current_node, self.msg_info['text_split'][2])
                if dice_result_type == 'node_name':
                    # 传回的为节点名称
                    start_obj.moveToNewNode(dice_result)
                return outtext
            else:
                return '没有船票还想登上我的船？杂鱼博士真是杂鱼透顶呢。'













if __name__ =='__main__':
    pass