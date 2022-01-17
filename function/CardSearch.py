import sqlite3

class CardSearch:
    def __init__(self,card_name):
        self.name = card_name
        self.filename = './botqq/database/' # 初始化权限文件路径
        self.cardTextHeader = [
            # '_id','id','japName','name','enName','sCardType','CardDType','tribe','package','element','level',
            # 'infrequence','atkValue','atk','defValue','def','effect','ban','cheatcode','adjust','cardCamp','oldName',
            # 'shortName','pendulumL','pendulumR'
            'id','name','desc'
        ] # 整张表的表头
        self.cardDatasHeader = [
            'id','ot','setcode','type','atk','def','level','race','attribute','category'
        ]

        self.showHeader = [
            # 'name','sCardType','CardDType','tribe','package','element','level',
            # 'atk','def','effect','ban'
            'name',#'atk','def','level','race', # 其他好像有问题
            'desc'
        ] # 需要字段的表头

    def __connectSqlite(self):
        """连接数据库"""
        con = sqlite3.connect(self.filename + 'Kal-tsit.db')
        cur = con.cursor()
        return (con,cur)

    def __searchCard(self):
        (con,cur) = self.__connectSqlite()
        cur = con.cursor()

        try:
            cur.execute("SELECT * FROM cardTexts WHERE name = ?",(self.name,))
            test = list(cur.fetchall()[0])
            dict_of_text = dict(zip(self.cardTextHeader,test))

            cur.execute("SELECT * FROM cardDatas WHERE id = ?",(dict_of_text['id'],))
            test = list(cur.fetchall()[0])
            dict_of_text.update(dict(zip(self.cardDatasHeader,test)))
            print(dict_of_text)
            return dict_of_text
        except:
            print(self.name)
            return 'error'

    def cardTextReturn(self):
        msg_dict = self.__searchCard() # 拿到数据字典
        if msg_dict == 'error':
            cardText = '查无此卡'
        else:
            cardText = '\n'.join([str(x)+':'+str(msg_dict[x]) for x in self.showHeader if msg_dict[x]]) # 只返回非空值
        return cardText
        

if __name__ == "__main__":
    testclass = CardSearch('元素英雄 新星主')
    print(testclass.cardTextReturn())