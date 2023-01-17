import sqlite3

class GameDatabase:
    
    filename = './bot/database/' # 数据库位置
    table_head = ["changer_id", "group_id", "default_save", "creator_id", "active_status"]
        
    @classmethod
    def __connectSqlite(cls):
        """连接数据库"""
        con = sqlite3.connect(cls.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return (con,cur)


    @classmethod
    def dataSave(cls, data_dict):
        """保存当前群组默认存档数据-实时"""
        con,cur = cls().__connectSqlite()
        cur.execute(f"REPLACE INTO `KaltsitRogue` ( \
            changer_id, group_id, default_save, creator_id, active_status \
            ) VALUES(?,?,?,?,?)",(
                data_dict[cls.table_head[0]], data_dict[cls.table_head[1]], data_dict[cls.table_head[2]], 
                data_dict[cls.table_head[3]], data_dict[cls.table_head[4]]
            )
        )
        con.commit()
        con.close()


    @classmethod
    def dataSearch(cls, group_id):
        """查询实时数据"""
        dict_of_text = None
        con,cur = cls().__connectSqlite()
        try:
            cur.execute("SELECT * FROM `KaltsitRogue` WHERE group_id = ? ",(group_id,))
            test = list(cur.fetchall()[0])
            dict_of_text = dict(zip(cls.table_head, test))
        except:
            print('未查到记录')
        finally:
            con.commit()
            con.close()

        return dict_of_text