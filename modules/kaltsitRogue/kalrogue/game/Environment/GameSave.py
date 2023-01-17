from kalrogue.game.Environment.GameDoctor import GameDoctor
from kalrogue.game.Environment.GameTable import GameTable

class GameSave:
    def __init__(self) -> None:
        self.group_id=0                                   # 群号
        self.mode_list=["normal"]                         # 游玩的模组
        self.story_node_list=[]                           # 经历过的故事清单
        self.member_list = []                             # 捐赠信用的玩家列表
        self.credit_pool=0                                # 信用池 for save
        self.is_end=0                                     # 是否结局 1 已结局
        self.endding_id=""                                # 结局编号
        self.doctor_condition=GameDoctor().toDict()
        self.game_environment=GameTable().toDict()
        self.story_node_dict={
        }


    def toDict(self):
        return {
            "group_id":self.group_id,                     # 群号
            "mode_list":self.mode_list,                   # 游玩的模组
            "member_list":self.member_list,               # 捐赠信用的玩家列表
            "story_node_list":self.story_node_list,       # 经历过的故事清单
            "credit_pool":self.credit_pool,               # 信用池 for save
            "is_end":self.is_end,                         # 是否结局 1 已结局
            "endding_id":self.endding_id,                 # 结局编号
            "doctor_condition":self.doctor_condition,
            "game_environment":self.game_environment,
            "story_node_dict":self.story_node_dict
        }
    