#! /usr/bin/env python3
# coding:utf-8
"""
节点类

"""
import os

from kalrogue.game.Environment.MoveAction import MoveAction
from kalrogue.utils.SaverLoader import SaverLoader
from kalrogue.utils.Dice import StoryDice
from kalrogue.utils.TextReceiver import TextReceiver
from kalrogue.game.Environment.GameSave import GameSave
from kalrogue.game.Environment.GameDoctor import GameDoctor


class GameNode:
    """basic node class, offer basic function"""

    def __init__(self, node_name) -> None:
        self.node_json: dict = self.NodeLoader(node_name)[node_name]
        self.node_name = node_name
        self.node_type = self.node_json["node_type"]
        self.next_node_id = self.node_json["next_node_id"]
        self.position = 0

    def NodeStoryExchanger(self, node_name):
        """节点与故事线 对应"""
        story_line_dir = '/resources/story/story-node.json'
        story_line = SaverLoader.jsonReader(story_line_dir)[node_name]
        return story_line

    def NodeChecker(self, node_name):
        """检查故事线文件json"""
        story_line_dir = '/resources/story/' + self.NodeStoryExchanger(node_name) + '/'
        filenames = os.listdir(SaverLoader.get_project_path() + story_line_dir)
        search_list = list(filter(None, map(lambda x: x if x.endswith('.json') else None, filenames)))
        return search_list

    def NodeLoader(self, node_name):
        """加载节点json"""
        story_dir = '/resources/story/' + self.NodeStoryExchanger(node_name) + '/' + node_name + '.json'
        return SaverLoader.jsonReader(story_dir)

    def autoText(self):
        """根据当前位置返回自动化文本 + 更新位置"""
        if self.isNodeDone():
            return
        out_text = TextReceiver.textRead(self.node_name, self.NodeStoryExchanger(self.node_name), self.position)
        self.updateNodePosition(self.position + 1)
        return out_text

    def specialText(self):
        """特殊dice|choice部分的文本 - 不更新position"""
        if self.isNodeDone():
            return
        out_text = TextReceiver.textRead(self.node_name, self.NodeStoryExchanger(self.node_name), self.position)

        return out_text

    # ========================
    # 更新方法
    # ========================

    def updateNodePosition(self, position=None):
        """更新节点行进位置"""
        if position is None:
            self.position += 1
        else:
            self.position = position
        self.node_json['position_save'] = self.position

    def updateNodeMsg(self, save_dict, node_name):
        """根据存档更新节点信息 - 创建完节点一定要根据存档更新
        @param
            save_dict : 存档dict
        """
        if node_name in list(save_dict['story_node_dict'].keys()):
            self.node_json['story_node_dict'].update(save_dict['story_node_dict'][node_name])
            self.node_json['story_node_list'].append(node_name)

    def nextMove(self, save_dict: GameSave):
        """读取下一步行动
        @param
            save_dict : 存档类
        """
        current_position = self.node_json['position_save']
        print('[nextMove]current_position: ',
              current_position,
              self.node_json['dice_position_list'], self.node_json['choice_position_list'],
              self.node_json['rqmt_node_list'])

        if current_position in self.node_json['dice_position_list']:
            print('[nextMove]current_position - go into: dice')
            return 'dice'
        elif current_position in self.node_json['choice_position_list']:
            print('[nextMove]current_position - go into: choice')
            return 'choice'
        # 先进dice和choice 再检查rqmt
        elif current_position in self.node_json['rqmt_node_list']:
            print('[nextMove]current_position - go into: rqmtResultMove')
            return self.rqmtResultMove(save_dict)
        else:
            print('[nextMove]current_position - go into: auto')
            return 'auto'

    def isNodeDone(self):
        """node是否执行完毕
        根据当前执行位置检查
        """
        if self.position >= self.node_json["node_amount"]:
            # 位置处于最后一个节点时不算完成 一定要大于才能算完成
            self.node_json["is_done"] = 1

        return self.node_json["is_done"] == 1

    # ========================
    # 需求类方法集合
    # ========================
    def isRqmtExist(self):
        """当前position是否存在rqmt"""
        current_position = self.node_json['position_save']
        return int(current_position) in self.node_json['rqmt_node_list']

    def rqmtTypeCheck(self):
        """当前position存在的rqmt类型 operator | item """
        current_position = self.node_json['position_save']
        return self.node_json['rqmt_node_dict'][str(current_position)][1]

    def rqmtCheck(self, check_type, save_dict: GameSave = None):
        """执行节点前 - 检查需求是否具备
        注意 掷骰结果也在此判断！
        @param
            check_type : rqmt_node_dict的第二项 dice | operator | item
            save_dict : 存档类
        """
        # 检查是否有需求
        current_position = self.node_json['position_save']
        if self.isRqmtExist():
            check_dict = self.node_json['rqmt_node_dict'][str(current_position)]
            if check_type == 'dice':
                # dice_dict : ["60", "dice", {
                #       "check_type": "GREATER_THAN",
                #       "node_name": node1
                # }, 注释]
                print('[DiceRqmtCheck]', check_dict)
                # current_position 是int类型 key必须是str类型
                if str(current_position) in list(self.node_json['dice_result'].keys()):
                    dice_result = int(self.node_json['dice_result'][str(current_position)])
                    if check_dict[2]['check_type'] == "GREATER_THAN":
                        return dice_result > int(check_dict[0])
                    elif check_dict[2]['check_type'] == "GREATER_THAN_EQUAL":
                        return dice_result >= int(check_dict[0])
                    elif check_dict[2]['check_type'] == "LESS_THAN":
                        return dice_result < int(check_dict[0])
                    elif check_dict[2]['check_type'] == "LESS_THAN_EQUAL":
                        return dice_result <= int(check_dict[0])
                else:
                    return False
            elif check_type == 'operator':
                return check_dict[0] in save_dict.doctor_condition['friends']
            elif check_type == 'item':
                return check_dict[0] in save_dict.doctor_condition['bag']
            elif check_type == 'no_operator':
                return check_dict[0] not in save_dict.doctor_condition['friends']

    def rqmtResultMove(self, save_dict: GameSave):
        """需求检查后 根据结果执行后续步骤
        只用于默认流程
        @param
            save_dict : 存档类
        """
        # TODO
        if self.isRqmtExist():
            if self.rqmtCheck(self.rqmtTypeCheck(), save_dict):
                print('auto')
                return 'auto'
            else:
                print('rqmt')
                return 'rqmt'
        else:
            print('auto2')
            return 'auto'

    # def rqmtFailNode(self):
    #     """当前node需求检查 【未通过】时，返回的node节点名称"""
    #     outtext = ''
    #     current_position = self.node_json['position_save']
    #     if self.isRqmtExist():
    #         # out_list 是存档中dice_position的内容
    #         rqmt_out_list = self.node_json['rqmt_node_dict'][str(current_position)]
    #         print('[RqmtFail]', rqmt_out_list)
    #         rqmt_process_dict = rqmt_out_list[2]
    #         if rqmt_process_dict['rqmt_type'] == 'lock':
    #             # 封锁节点，返回node_name的节点
    #
    #             node_name_out = rqmt_process_dict['node_name']
    #             return outtext, node_name_out, 'node_name'

    # ========================
    # 奖励类方法集合
    # ========================
    def isRewardExist(self):
        """当前position是否存在Reward"""
        current_position = self.node_json['position_save']
        return str(current_position) in self.node_json['reward_list']

    def rewardTypeCheck(self):
        """当前position存在的reward类型"""
        current_position = self.node_json['position_save']
        return self.node_json['reward'][str(current_position)][1]

    def rewardMove(self, check_type, save_dict: GameSave = None):
        """执行节点中 - 检查奖励
        @param
            check_type : reward 列表的第二项 endding | operator | item
            save_dict : 存档类
        @out
            有无奖励[bool], 内容名称, 内容类型, 更新的存档
            True
        """

        current_position = self.node_json['position_save']
        if self.isRewardExist() and str(current_position) in list(self.node_json['reward'].keys()):

            check_dict = self.node_json['reward'][str(current_position)]
            if check_type == 'endding':
                # 奖励为结局 - 我觉得应该把结局存在表里 TODO
                save_dict.is_end = 1
                return True, check_dict[0], 'endding', save_dict  # 返回结局编号
            elif check_type == 'operator':
                if check_dict[0] not in save_dict.doctor_condition['friends']:
                    new_doctor = GameDoctor(save_dict.doctor_condition)
                    new_doctor.setFriend(check_dict[0])
                    save_dict.doctor_condition = new_doctor.toDict()
                    # save_dict.doctor_condition['friends'].append(check_dict[0])
                    # save_dict.doctor_condition['friends_dict'][0][check_dict[0]] = operator_dict["operator"][check_dict[0]]
                return True, check_dict[0], 'operator', save_dict
            elif check_type == 'item':
                if check_dict[0] not in save_dict.doctor_condition['bag']:
                    new_doctor = GameDoctor(save_dict.doctor_condition)
                    new_doctor.setBag(check_dict[0])
                    save_dict.doctor_condition = new_doctor.toDict()
                    # save_dict.doctor_condition['bag'].append(check_dict[0])
                    # save_dict.doctor_condition['bag_dict'][0][check_dict[0]] = item_dict["item"][check_dict[0]]
                return True, check_dict[0], 'item', save_dict
            return False, check_dict[0], check_dict[1], save_dict
        return False, None, None, save_dict

    ##########################
    def toDictSave(self):
        """保存用 将实例化的node转化为dict"""
        return {
            self.node_name: {
                "node_id": self.node_name,
                "node_info": self.node_json['node_info'],
                "choice_made": self.node_json['choice_made'],
                "node_type": self.node_json['node_type'],
                "story_text_file_name": self.node_json['story_text_file_name'],
                "choice_maker": self.node_json['choice_maker'],
                "position_save": self.node_json['position_save'],
                "node_amount": self.node_json['node_amount'],
                "is_done": self.node_json['is_done'],
                "game_time_pass": self.node_json['game_time_pass'],
                "dice_position_list": self.node_json['dice_position_list'],
                "dice_position": self.node_json['dice_position'],
                "dice_result": self.node_json['dice_result'],
                "choice_position_list": self.node_json['choice_position_list'],
                "choice_position": self.node_json['choice_position'],
                "choice_result": self.node_json['choice_result'],
                "next_node_id": self.node_json['next_node_id'],
                "rqmt_node_list": self.node_json['rqmt_node_list'],
                "rqmt_node_dict": self.node_json['rqmt_node_dict'],
                "rqmt_got_list": self.node_json['rqmt_got_list'],
                "reward_list": self.node_json['reward_list'],
                "reward": self.node_json['reward']
            }
        }


class DiceNode(GameNode):
    """掷骰节点"""

    def __init__(self, node_name) -> None:
        super().__init__(node_name)
        self.choice_maker = -1  # 掷骰子的人的id
        self.dice_position_list = self.node_json['dice_position_list']
        self.dice_position = self.node_json['dice_position']

    def setChoiceMaker(self, id_in=-1):
        self.choice_maker = id_in

    # 掷骰方法
    def diceMake(self, save_dict: GameSave):
        """id=-1时为系统
        @output:
            (单骰list[11, 33, 40], 额外点数 100)
        """

        if self.nextMove(save_dict) == 'dice':
            current_position = self.node_json['position_save']

            dice_text_in = self.dice_position[str(current_position)][0].split(",")
            dice_text = str(dice_text_in[0]) + "d" + str(dice_text_in[1]) + "+" + str(dice_text_in[2])
            # 单骰list 额外点数
            print('[dice_text]', dice_text)
            return StoryDice.dice_basic(dice_text)

    def diceText(self, save_dict: GameSave):
        """掷骰子 + 将掷骰子结果保存在node信息里 + 转为文字
        需要current_position为掷骰子位置
        """
        dice_list, add_point = self.diceMake(save_dict)
        sum_result = sum(dice_list) + add_point
        current_position = self.node_json['position_save']
        self.node_json['dice_result'][str(current_position)] = sum_result  # 规则比较简单 可修改
        outtext = '掷骰子的结果为' + '|'.join(str(x) for x in dice_list) + '，以及额外的' + str(
            add_point) + '点，共计：' + str(sum_result)
        print('[diceText]', outtext)
        return outtext

    def inputDice(self, save_dict: GameSave):
        """根据dice结果返回节点内容与文本"""
        outtext = self.diceText(save_dict)
        current_position = self.node_json['position_save']
        if self.isRqmtExist():
            # out_list 是存档中dice_position的内容
            fail_list = self.node_json['dice_position'][str(current_position)]
            print(fail_list)
            if fail_list[2] == 'node_name':
                if self.rqmtCheck('dice', save_dict):
                    # 如果满足条件 则执行 rqmt字典中的节点
                    node_name_out = self.node_json['rqmt_node_dict'][str(current_position)][2]['node_name']
                    print(node_name_out)
                    return outtext, node_name_out, 'node_name'
                else:
                    # 【不】满足条件则执行next_node_id
                    return outtext, fail_list[1], 'node_name'

    def cheatDiceWithInput(self, save_dict: GameSave, point_cheat):
        """根据【传入的作弊dice】结果返回节点内容与文本"""

        current_position = self.node_json['position_save']
        self.node_json['dice_result'][str(current_position)] = int(point_cheat)
        outtext = '作弊骰子！看在杂鱼博士的份上就让你骰出' + str(point_cheat) + '点吧~'

        current_position = self.node_json['position_save']
        if self.isRqmtExist():
            fail_list = self.node_json['dice_position'][str(current_position)]  # 检定失败的信息列表
            print(fail_list)
            if fail_list[2] == 'node_name':
                if self.rqmtCheck('dice', save_dict):
                    # 同diceInput
                    node_name_out = self.node_json['rqmt_node_dict'][str(current_position)][2]['node_name']
                    print(node_name_out)
                    return outtext, node_name_out, 'node_name'
                else:
                    return outtext, fail_list[1], 'node_name'


class ChoiceNode(GameNode):
    """用于选择的节点
    - 选择节点可以移动到多个不同的node 根据选项决定
    """

    def __init__(self, node_name) -> None:
        super().__init__(node_name)
        self.choice_maker = -1  # 做选择的人的id
        self.choice_position_list = self.node_json['choice_position_list']
        self.choice_position = self.node_json['choice_position']
        pass

    # 选择方法 - 输入接收器
    def inputChoice(self, choice_order, save_dict: GameSave):
        """传入选择结果 更新node对象+读取选择结果
        @param
            choice_order : 单纯的选择结果-str类型
            - 隐含input
                self.node_json["choice_position"][str(current_position)][choice_order]
                [内容, 类型标识, 特殊文本, 注释]
                - ["kaltsit-main-line1", "node_name", "", "选择移动到新节点"]
                - [{"require":"1, 100, 0", "check":"60"}, "dice", {
                        "check_type": "GREATER_THAN",
                        "node_name": node1,
                        "node_name_another_rules": node2 ...
                    }, "选择是个骰子行动"]
        @out
            out_list : [内容, 类型标识, 注释]
        """
        if self.nextMove(save_dict) == 'choice':
            current_position = self.node_json['position_save']
            if choice_order in list(self.node_json["choice_position"][str(current_position)].keys()):
                out_list = self.node_json["choice_position"][str(current_position)][choice_order]
                self.node_json['choice_result'] = choice_order
                if out_list[1] == 'node_name':
                    out_story_node_name = out_list[0]
                elif out_list[1] == 'dice':
                    # TODO 需要重写
                    ''' 选择了一个掷骰子行动 
                        - 那么out_list[2]表示 没满足、满足骰子要求时应该移动到的node_name [node1, node2]
                        - out_list[0]表示 骰子的类型与要求达到的点数 格式["1d100", 60]
                    '''
                    dice_list, add_point = StoryDice.dice_basic(out_list[0][0])
                    sum_result = sum(dice_list) + add_point
                    outtext = '掷骰子的结果为' + '|'.join(str(x) for x in dice_list) + '，以及额外的' + str(
                        add_point) + '点，共计：' + str(sum_result)
                    result_to_compare = int(out_list[0][1])
                    if result_to_compare <= sum_result:
                        return [outtext, out_list[2][1], "node_name"]  # 第二个是满足dice的
                    else:
                        return [outtext, out_list[2][0], "node_name"]  # 没满足dice

                return out_list


class HomeNode(ChoiceNode):
    """开始的node-特殊类型"""

    def __init__(self) -> None:
        super().__init__()
        self.choice_maker = -1  # 做选择的人的id
        self.choice_position_list = self.node_json['choice_position_list']
        self.choice_position = self.node_json['choice_position']

        self.home_story_line = 'home'
        self.node_name = 'home-intro'


class EndNode(GameNode):
    """结局node-特殊类型"""

    def __init__(self, node_name) -> None:
        super().__init__(node_name)
        self.node_amount = self.node_json["node_amount"]
        try:
            endding_list = self.node_json["reward"][str(self.node_amount - 1)]
            self.endding_id = endding_list[0]
        except:
            self.endding_id = ""

    def updateEndding(self):
        """最后一个节点为endding - 更新endding_id并返回"""
        endding_list = self.node_json["reward"][str(self.node_amount - 1)]
        self.endding_id = endding_list[0]
        return self.endding_id


class AutoNode(GameNode):
    """自动文本node - 切换至下一个节点"""

    def __init__(self, node_name) -> None:
        super().__init__(node_name)


class AutoCheck(GameNode):
    """
    自动检查节点 约等于autotext文本模式
    通常用于选择节点之后，检查是否具有相应通过条件。
    """

    def __init__(self, node_name) -> None:
        super().__init__(node_name)
