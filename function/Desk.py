#! /usr/bin/env python3
# coding:utf-8

import sqlite3
from datetime import datetime


class kaltsitDesk:
    """漂流瓶功能
    
    私信接收-识别+处理
    群聊提取-
    
    """
    def __init__(self, msg) -> None:
        # self.msg_type = msg_type
        self.filename = './botqq/database/'
        self.msg = msg
        # self.groupId = str(msg['group_id'])
        self.pub_time = datetime.now()
        pass
    
    
    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return (con,cur)


    def databaseInit(self):
        """建表"""
        con,cur = self.__connectSqlite()
        cur.execute(f"DROP TABLE `Drifting_bottle`")
        cur.execute(f"CREATE TABLE IF NOT EXISTS `Drifting_bottle` (id_K INTEGER PRIMARY KEY AUTOINCREMENT, pub_time TEXT, text TEXT, pub_id TEXT, status TEXT)")
        con.commit()# 事务提交，保存修改内容。
        con.close()
        con,cur = self.__connectSqlite()
        cur.execute(f"REPLACE INTO 'Drifting_bottle' (pub_time, text, pub_id, status) VALUES(?,?,?,?)",(
            'timeheader', '办公桌空空如也……', '123456789', '-1' # status 0是未读，1是已读,-1是防止空值保障
            )
        )
        con.commit()# 事务提交，保存修改内容。
        con.close()
        # self.__dataSave() # 保存消息内容


    def __dataSave(self):
        """存数据
        输入#投/#投10086 调用
        """
        texttwopart = self.msg['text_ori'].split()
        if len(texttwopart[0]) == 2:
            con,cur = self.__connectSqlite()
            cur.execute(f"REPLACE INTO 'Drifting_bottle' (pub_time, text, pub_id, status) VALUES(?,?,?,?)",(
                self.pub_time, self.msg['text_ori'][2::], self.msg['id'], '0'
                )
            )
            con.commit()# 事务提交，保存修改内容。
            con.close()

            # 查询序号
            con,cur = self.__connectSqlite()
            cur.execute("SELECT COUNT(*) FROM 'Drifting_bottle' ")
            temp = cur.fetchall()[0]
            con.commit()# 事务提交，保存修改内容。
            con.close()

            return f'我桌子动了我不玩了[消息投出 ID-{temp[0]}]'
        else:
            
            con,cur = self.__connectSqlite()
            cur.execute(f"SELECT * FROM `Drifting_bottle` WHERE `id_K`=='{str(texttwopart[0][2::])}' ORDER BY random() LIMIT 1")
            temp = cur.fetchall()
            if temp == []:
                # print(temp)
                return '博士，你在干什么？[您被投出]'
            else:
                check_result = list(temp[0])
                savetext = check_result[2] +'\n\n——reply：\n'+ ' '.join(x for x in texttwopart[1::])

                cur.execute(f"REPLACE INTO 'Drifting_bottle' (id_K, pub_time, text, pub_id, status) VALUES(?,?,?,?,?)",(
                    int(texttwopart[0][2::]), self.pub_time, savetext, self.msg['id'], '0'
                    )
                )
                con.commit()# 事务提交，保存修改内容。
                con.close()
                return '[回信投出]'


    def __dataGet(self):
        """捞数据-注意此行为发生在群聊中
        """
        con,cur = self.__connectSqlite()
        cur.execute(f"SELECT * FROM `Drifting_bottle` WHERE `status`!='-1' ORDER BY random()  LIMIT 1")
        temp = cur.fetchall()
        if temp != []:
            print(temp)
            check_result = list(temp[0])
        # print('抽取结果',check_result)
        else: 
            cur.execute("SELECT * FROM `Drifting_bottle` WHERE `status`=='-1' ORDER BY random() LIMIT 1")
            check_result = list(cur.fetchall()[0])
        
        # 修改已读状态status

        out_text = f'[桌中摸索到了……ID-{check_result[0]}]\n' + check_result[2]

        if check_result[4] != '-1':
            cur.execute(f"REPLACE INTO 'Drifting_bottle' (id_K, pub_time, text, pub_id, status) VALUES(?,?,?,?,?)",(
                check_result[0], check_result[1], check_result[2], check_result[3], '1' # id_K必须要加上,不然会多一条数据
                )
            )
            con.commit()# 事务提交，保存修改内容。
            con.close()
            return out_text
        
        # 回复功能提示
        out_text += '\n[回复方式：输入#投ID 内容]'
        return out_text


    def __dataGetID(self):
        """捞指定瓶子"""
        texttwopart = self.msg['text_ori'].split()
        con,cur = self.__connectSqlite()
        cur.execute(f"SELECT * FROM `Drifting_bottle` WHERE `id_K`=='{str(texttwopart[0][2::])}' ORDER BY random() LIMIT 1")
        temp = cur.fetchall()
        if temp == []:
            # print(temp)
            return '博士，你在干什么？[您被投出]'
        else:
            check_result = list(temp[0])
            return f'熟悉的位置摸出了……[指定摸索 ID-{texttwopart[0][2::]}]\n' + check_result[2]
        con.close()
        pass


    def kaltsitDeskApi(self):
        """接口"""

        if self.msg['text_ori'].startswith('#捞'):
            temp = self.msg['text_ori'].split()
            if len(temp[0]) == 2:
                return self.__dataGet()
            else:
                # 捞指定瓶子
                return self.__dataGetID()
            
        elif self.msg['text_ori'].startswith('#投'):
            return self.__dataSave()
            
        else:
            return


if __name__ == "__main__":
    
    msg_person = {
        'id':987654321,
        # 'group_id':group.id,
        'text_ori':'#投12 漂流瓶补话测试一下',                                # 21.11.26 添加复读打断功能时加入
        'type':'person'
    }
    desk1 = kaltsitDesk(msg_person)
    desk1.databaseInit()
    # print(desk1.kaltsitDeskApi())

    # msg_group = {
    #     'id':2238701273,
    #     'group_id':444555666,
    #     'text_ori':'#捞12',                                # 21.11.26 添加复读打断功能时加入
    #     'type':'group'
    # }
    # desk2 = kaltsitDesk(msg_group)
    # print(desk2.kaltsitDeskApi())

    # print(msg_person['text_ori'][0:2])