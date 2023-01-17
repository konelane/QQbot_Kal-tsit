from kalrogue.resources.game.GameContants import (
    START_GAME_CREDIT_CONSUMPTION )

class GameTable:
    '''游戏场景状态'''
    def __init__(self) -> None:
        self.credit_consume = 0      # 是否设置在此处
        self.gametime = '18:00' 
        self.credit_pool_need = START_GAME_CREDIT_CONSUMPTION    # 模组需求信用池

    def timeSet(self, status = 'add', time_diff = 0):
        '''时间修改
        @param
            status:
                add - 前进
                back - 后退
            time_diff:
                time 变化值 - 单位min
        '''
        

    def toDict(self):
        return {
            "credit_consume":self.credit_consume,
            "gametime":self.gametime,
            "credit_pool_need":self.credit_pool_need
        }