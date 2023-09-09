import sqlite3
from uuid import uuid4
import time

from core.config.BotConfig import BasicConfig


class DataTableInstall:
    def __init__(self) -> None:
        self.filename = BasicConfig().databaseUrl # 数据库位置 需修改，在上层目录执行
        pass

    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return (con,cur)

    def gachaTableCreate(self):
        '''resource: gacha
        十连数据表： gachaData
        表头 - 用户昵称 | qq | 抽卡次数 | 六星 | 六星率 | 五星 | 五星率 | 四星 | 四星率 | 三星 | 三星率 | 最后抽卡时间 |
        表头 - u_name  | id | gacha_num| six | six_r  | five| five_r | four | four_r | three| three_r | last_gacha_time |
        '''
        con,cur = self.__connectSqlite()
        cur.execute("CREATE TABLE IF NOT EXISTS `gachaData` (  \
                id INTEGER PRIMARY KEY NOT NULL,  u_name TEXT, gacha_num INTEGER, \
                six INTEGER, six_r FLOAT, five INTEGER, five_r FLOAT, \
                four INTEGER, four_r FLOAT, three INTEGER, three_r FLOAT, last_gacha_time TEXT \
            )")
        cur.execute(f"REPLACE INTO `gachaData` ( id, u_name, gacha_num, six, six_r, \
            five, five_r, four, four_r, three, three_r, last_gacha_time ) VALUES(?,?,?,?,?, ?,?,?,?,?, ?,?)",(
            591016144,  '凯尔希初始化', 10, 9, 0.9, 
            1, 0.1, 0, 0.0, 0,  0.0, time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime())
            )
        )
        con.commit()
        con.close()
        print('建表成功')


    def kheartTableCreate(self):
        """建表 数据库表
        rule_id, rule_uid, creator_id, first_group, keyword, reply, change_id, change_group, start_date, end_date, dp
        """
        con,cur = self.__connectSqlite()
        cur.execute("CREATE TABLE IF NOT EXISTS `kheart` (  \
                rule_id INTEGER, rule_uid TEXT PRIMARY KEY NOT NULL, creator_id INTEGER, first_group INTEGER, \
                keyword TEXT, reply TEXT, change_id INTEGER, change_group INTEGER, \
                start_date TEXT, end_date TEXT, dp TEXT \
            )")
        cur.execute(f"REPLACE INTO `kheart` ( rule_id, rule_uid, creator_id, first_group, keyword, reply, change_id,  \
            change_group, start_date, end_date, dp ) VALUES(?,?,?,?,?, ?,?,?,?,?,?)",(
            1, str(uuid4()),  591016144, 114514, '催更', '催更', 
            1919810, 114514, time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime()), '4712/12/31-23:59:59', 'ACTIVE'
            )
        )
        con.commit()
        con.close()
        print('建表成功')


    def kaltsitRogueTableCreate(self):
        """建表 数据库表
        changer_id, group_id, default_save, creator_id, active_status
        """
        con,cur = self.__connectSqlite()
        cur.execute("CREATE TABLE IF NOT EXISTS `KaltsitRogue` (  \
                changer_id INTEGER, group_id INTEGER PRIMARY KEY NOT NULL,  \
                default_save TEXT, creator_id INTEGER, active_status INTEGER \
            )")
        cur.execute(f"REPLACE INTO `KaltsitRogue` ( changer_id, group_id, default_save, creator_id,  \
                active_status \
             ) VALUES(?,?,?,?,?)",(
            2238701273, 114514,  "114514_0.json", 2238701273, 0
            )
        )
        con.commit()
        con.close()
        print('建表成功')



if __name__ =='__main__':
    msg_dict = {
        'id':591016144,
        'name': 'hehe',
        'group_id':114514,
        'text_ori':'#抽卡',
    }
    table_create_obj = DataTableInstall()
    table_create_obj.gachaTableCreate()
    table_create_obj.kheartTableCreate()
    table_create_obj.kaltsitRogueTableCreate()