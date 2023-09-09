from kalrogue.game.Environment.GameDoctor import GameDoctor
from kalrogue.game.Environment.GameTable import GameTable


class GameSave:
    # 群号
    group_id = 0
    # 游玩的模组
    mode_list = ["normal"]
    # 经历过的故事清单
    story_node_list = []
    # 捐赠信用的玩家列表
    member_list = []
    # 信用池 for save
    credit_pool = 0
    # 是否结局 1 已结局
    is_end = 0
    # 结局编号
    endding_id = ""
    # 博士类初始化
    doctor_condition = GameDoctor().toDict()
    # 游戏属性类初始化
    game_environment = GameTable().toDict()
    # 故事节点初始化
    story_node_dict = {}

    def __init__(self) -> None:
        pass


    def toDict(self):
        return {
            "group_id": self.group_id,  # 群号
            "mode_list": self.mode_list,  # 游玩的模组
            "member_list": self.member_list,  # 捐赠信用的玩家列表
            "story_node_list": self.story_node_list,  # 经历过的故事清单
            "credit_pool": self.credit_pool,  # 信用池 for save
            "is_end": self.is_end,  # 是否结局 1 已结局
            "endding_id": self.endding_id,  # 结局编号
            "doctor_condition": self.doctor_condition,
            "game_environment": self.game_environment,
            "story_node_dict": self.story_node_dict
        }
