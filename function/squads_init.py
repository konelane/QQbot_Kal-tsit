#! /usr/bin/env python3
# coding:utf-8
import random
import story_xu as sx
import re
import numpy as np


class operator:
    """
        将编队干员各属性记录新的小队文档
        初始化干员文档

        方法介绍：
        write_opt 写入文档【依然是可怕的覆盖
        init_opt 初始化干员各项参数
        read_opt 读取干员文档
        __update_opt__ 更新文档字段
        opt_upgrade 干员升级加点
        fight_action 攻击与受击行为 【需要数据库
        use_equip_package_change 使用与装备【只有个空架子，底层没写

    """
    def __init__(
        self,name,charm_init,agile_init,strength_init,intelligence_init
        ) -> None:
        self.name = name
        self.charm_init = charm_init
        self.agile_init = agile_init
        self.strength_init = strength_init
        self.intelligence_init = intelligence_init
        self.filename = '.\\botqq\\' + self.name + '_opt.txt'
        pass

    def write_opt(self,opt_dict):
        with open(self.filename, 'w') as f:
            f.write('**********\n')
            f.write('name|'+            opt_dict['name']+ '|\n')
            f.write('ethnic|'+      str(opt_dict['ethnic']) + '|\n')
            f.write('level|'+       str(opt_dict['level'])+ '|\n')
            f.write('exp|'+         str(opt_dict['exp'])+ '|\n')

            f.write('birthplace|'+      str(opt_dict['birthplace'])+ '|\n')
            f.write('group|'+       str(opt_dict['group'])+ '|\n')
            f.write('id|'+          str(opt_dict['id'])+ '|\n')
            f.write('ideal|'+       str(opt_dict['ideal'])+ '|\n')
            f.write('bound|'+       str(opt_dict['bound'])+ '|\n')
            f.write('unique|'+      str(opt_dict['unique'])+ '|\n')
            f.write('shortcoming|'+ str(opt_dict['shortcoming'])+ '|\n')

            f.write('charm|'+       str(opt_dict['charm']) + '|\n')
            f.write('agile|'+       str(opt_dict['agile'])+ '|\n')
            f.write('strength|'+    str(opt_dict['strength'])+ '|\n')
            f.write('intelligence|'+str(opt_dict['intelligence'])+ '|\n')
            f.write('sanity|'+      str(opt_dict['sanity'])+ '|\n')
            f.write('sanity_upper|'+str(opt_dict['sanity_upper'])+ '|\n')
            f.write('hp|'+          str(opt_dict['hp'])+ '|\n')
            f.write('hp_upper|'+    str(opt_dict['hp_upper'])+ '|\n')
            
            f.write('occupation|'+  str(opt_dict['occupation'])+ '|\n')
            f.write('sub_occupation|'+  str(opt_dict['sub_occupation'])+ '|\n')
            f.write('LMB|'+         str(opt_dict['LMB'])+ '|\n')
            f.write('infected|'+    str(opt_dict['infected'])+ '|\n')
            # 比博士多两行
            f.write('skill|'+       str(opt_dict['skill'])+ '|\n')
            f.write('package|'+     str(opt_dict['package'])+ '|\n')
            f.write('equip|'+       str(opt_dict['equip'])+ '|\n')
            f.write('condition|'+   str(opt_dict['condition'])+ '|\n')
            f.write('gift|'+        str(opt_dict['gift'])+ '|\n')
            f.write('skillful|'+    str(opt_dict['skillful'])+ '|\n')
            f.write('**********\n')

    def init_opt(
        self,
        rollnk_charm = '1d6',
        rollnk_agile = '1d6',
        rollnk_strength = '1d6',
        rollnk_intelligence = '1d6',
        # 特别信息
        
        opt_ethnic = None,

        opt_birthplace = None,
        opt_group = None,
        opt_id = None,
        opt_ideal = None,
        opt_bound = None,
        opt_unique = None,
        opt_shortcoming = None,

        opt_occupation = None,
        opt_LMB = None,
        opt_infected:int = None,
        opt_gift = [],
        opt_skillful = [],
        opt_skill = {}
        ):
        """
            建立干员文档
            为doctor文档的第二部分，在初始化doc文档化后添加进去 【思路05.22废弃】
            编队信息为字典，key为干员名，value为干员信息字典

        """
        
        charm_init = self.charm_init
        agile_init = self.agile_init
        strength_init = self.strength_init
        intelligence_init = self.intelligence_init

        # 人物背景部分
        if not opt_ethnic:
            print('正在随机种族')
            opt_ethnic = sx.roll_born('ethnic')[0]
        else:
            if sx.check_enthnic(opt_ethnic):
                print('正在设定出生')
                opt_ethnic = opt_ethnic
            else:
                print('种族鉴定失败，请重新填写！')
                return
                
        if not opt_infected:
            print('正在化验血样')
            opt_infected = random.randint(0,3)
        else:
            if opt_infected in [0,1,2,3]:
                print('正在设定感染者身份')
                opt_infected = opt_infected
            else:
                print('感染者身份鉴定失败，请重新填写！')
                return

        if not opt_birthplace:
            print('正在随机出生地')
            opt_birthplace = ''.join(x for x in sx.roll_born('birthplace'))
        if not opt_group:
            print('正在随机阵营')
            opt_group = sx.roll_born('group')[0]
        if not opt_id:
            print('正在随机身份')
            opt_id = sx.roll_born('identity')[0]
        if not opt_ideal:
            print('正在选择信仰')
            opt_ideal = sx.roll_born('ideal')[0]
        if not opt_bound:
            print('正在回想羁绊')
            opt_bound = sx.roll_born('bound')[0]
        if not opt_unique:
            print('正在逐渐独特')
            opt_unique = sx.roll_born('unique')[0]
        if not opt_shortcoming:
            print('正在调点毛病')
            opt_shortcoming = sx.roll_born('shortcoming')[0]
        if not opt_LMB:
            print('正在取出血汗钱')
            opt_LMB = random.randint(0,1000)
        

        # 列表类型
        if not opt_gift:
            print('正在觉醒天赋')
            opt_gift = sx.roll_born('gift')
        if not opt_skillful:
            print('正在熟练起来')
            opt_skillful = sx.roll_born('skillful')
        if not opt_skill:
            print('正在学习技能')
            opt_skill = {str(sx.roll_born('skill')[0]):1}


        if not opt_occupation:
            print('正在分配职业')
            opt_occupation = ['先锋','狙击','医疗','术师','近卫','重装','辅助','特种'][random.randint(0,7)]

        print('正在进行磨皮')
        charm = int(sx.roll(rollnk_charm).split('*************')[1].split('Total:')[1])
        print('正在安装脚底板')
        agile = int(sx.roll(rollnk_agile).split('*************')[1].split('Total:')[1])
        print('正在学习摸鱼')
        strength = int(sx.roll(rollnk_strength).split('*************')[1].split('Total:')[1])
        print('正在理解一切')
        intelligence = int(sx.roll(rollnk_intelligence).split('*************')[1].split('Total:')[1])


        # 带有计算规则的指标：
        sanity_upper = intelligence*5 + int(sx.roll('1d'+str(intelligence)).split('*************')[1].split('Total:')[1]) # 【规则没仔细想
        hp_upper = strength*5 + int(sx.roll('1d'+str(strength)).split('*************')[1].split('Total:')[1])
        # 初始化时看种族抗性：
        defence_point = 0 # 【护甲
        against_point = 0 # 【魔抗
        # mp_upper = intelligence*5 + int(sx.roll('1d'+str(intelligence)).split('*************')[1].split('Total:')[1])


        # 合成
        opt_dict= {
            'name':self.name,
            'ethnic':opt_ethnic,
            'level':1,
            'exp':0,

            'birthplace':opt_birthplace,
            'group':opt_group,
            'id':opt_id,
            'ideal':opt_ideal,
            'bound':opt_bound,
            'unique':opt_unique,
            'shortcoming':opt_shortcoming,

            'charm':int(charm_init)+charm,
            'agile':int(agile_init)+agile,
            'intelligence':int(intelligence_init)+intelligence,
            'strength':int(strength_init)+strength,
            'sanity':sanity_upper,
            'sanity_upper':sanity_upper,
            'hp':hp_upper,
            'hp_upper':hp_upper,

            'occupation':opt_occupation,
            'sub_occupation':'',
            'LMB':opt_LMB,
            'infected':opt_infected,

            'skill':opt_skill,
            # 'skill_level':['1'], # 长度应与skill一致
            'package':{},
            'equip':{},
            'condition':{},
            'gift':opt_gift,
            'skillful':opt_skillful

        } # 将干员数据设置为字典
        self.write_opt(opt_dict)



    def read_opt(self):    
        """
            读取operator个人文档
        """
        
        opt_dict= {
            'name':self.name,
            'ethnic':'',
            'level':1,
            'exp':0,

            'birthplace':'',
            'group':'',
            'id':'',
            'ideal':'',
            'bound':'',
            'unique':'',
            'shortcoming':'',

            'charm':0,
            'agile':0,
            'intelligence':0,
            'strength':0,
            'sanity':0,
            'hp':0,

            'occupation':' ',
            'sub_occupation':' ',
            'LMB':0,
            'infected':0,

            'skill':{},
            # 'skill_level':[], # 长度应与skill一致
            'package':{},
            'equip':{},
            'condition':{},
            'gift':[],
            'skillful':[]

        }

        dict_type = ['package','skill','equip','condition'] # 字典类型储存的，读取时需转换成列表类型

        list_type = ['gift','skillful']
        with open(self.filename, 'r') as f:
            for line in f.readlines():
                if line.split('|')[0] != '**********\n':

                    # 读取列表
                    if line.split('|')[0] in list_type:
                        linetemp = line.split('|')[1].split("'")[1::2]
                        # print(linetemp)
                        opt_dict[line.split('|')[0]] = linetemp
                    
                    elif line.split('|')[0] in dict_type:
                        # print(line.split('|')[1])
                        # if not line.split('|')[1]:
                        # print(line.split('|')[1:-1:])
                        linetemp = eval(line.split('|')[1:-1:][0])
                        # print(linetemp)
                        opt_dict[line.split('|')[0]] = linetemp
                        pass
                    # 读取单值
                    else:
                        opt_dict[line.split('|')[0]] = line.split('|')[1]
                
        # print(opt_dict)
        return opt_dict



    def __update_opt__(self,dat_key,update_dat,admin = False):
        """
            手动更新干员的各项数值【不提供对外接口】
            当然，适用于活动后自动更新
            考虑复制文件进行操作，防止文档不可逆损坏【还没写】
            注意：只能使用标准【英文title】进行更新 # 程序员累了

            Usage demo:
                hehe_opt.__update_opt__('sanity','增加 1') # 增加一个1级技能
                hehe_opt.__update_opt__('agile','减少 1') # 剔除1技能等级
                hehe_opt.__update_opt__('skill','更新普通一拳|2') # 更新指定名字技能为2级
                
        """
        single_list = [ 'agile','name','level','exp','charm','agile','intelligence','strength','sanity','sanity_upper','hp','hp_upper','LMB','infected']
        list_list = ['gift','skillful']
        dict_list = ['package','skill','equip','condition']

        opt_dict = self.read_opt()
        if admin and (re.match('更新',update_dat)):
            try:
                opt_dict[dat_key] = update_dat.split('更新')[1] # 单值项可以直接替换，需要admin权限
            except:
                print('更新出错\n')
        else:
            try:
                # 单值
                if dat_key in single_list:
                    if re.match('增加', update_dat):
                        opt_dict[dat_key] = int(opt_dict[dat_key]) + int(update_dat.split('增加')[1])
                    elif re.match('减少', update_dat):
                        opt_dict[dat_key] = int(opt_dict[dat_key]) - int(update_dat.split('减少')[1])

                # 列表：
                elif dat_key in list_list:
                    if re.match('增加', update_dat):
                        opt_dict[dat_key].append(update_dat.split('增加')[1])
                    elif re.match('减少', update_dat):
                        opt_dict[dat_key].remove(update_dat.split('减少')[1])

                # 字典
                elif dat_key in dict_list :
                    # try:
                    if re.match('更新', update_dat):
                        index = update_dat.split('更新')[1].split('|')[0] # 【index可以设置为文字，务必精确
                        opt_dict[dat_key][index] = str(update_dat.split('更新')[1].split('|')[1])
                    elif re.match('增加', update_dat):
                        index = str(update_dat.split('增加')[1])
                        # print(index)
                        # print(sx.check_normal(opt_dict,'single_item',index))
                        opt_dict[dat_key][index] = dict(number =  1)
                        df_item = sx.check_normal(opt_dict,'single_item',index)
                        for k in df_item.columns:
                            if k == index: pass
                            # if np.isnan(df_item[k].values) :
                            #     opt_dict[dat_key][index][k] = -1
                            #     pass
                            # 【数据库内容不能为空，否则无法读入
                            opt_dict[dat_key][index][k] = list(df_item[k].values)

                    elif re.match('减少', update_dat):
                        index = str(update_dat.split('减少')[1])
                        opt_dict[dat_key].pop(index)
                    else:
                        print('不会')
                    # except:
                    #     print('【更新】大概是打错字了')

            except(ValueError):
                print('【更新】数字/字符格式错误')
                return

        self.write_opt(opt_dict)
        # print('更新完毕：')
        # print(self.read_opt())


    def opt_upgrade(self):
        """干员升级检测与更新"""
        opt_dict = self.read_opt()
        levelnow = sx.check_normal(opt_dict,'exp')
        if opt_dict['level'] != levelnow:
            diff = int(levelnow) - int(opt_dict['level'])
            print('等级变化为：',levelnow)
            print('等级增加了',diff,'级')
            opt_dict['level'] = levelnow
            # 属性变化
            
            upgrade_list = sx.check_normal(opt_dict,'upgrade')
            charm_p = int(upgrade_list['魅力成长'])
            intel_p = int(upgrade_list['智力成长'])
            agile_p = int(upgrade_list['敏捷成长'])
            stren_p = int(upgrade_list['体质成长'])
            
            print('升级属性变化：\n',
                'charm',opt_dict['charm'],'+',charm_p*diff,'\n',
                'agile',opt_dict['agile'],'+',agile_p*diff,'\n',
                'intelligence',opt_dict['intelligence'],'+',intel_p*diff,'\n',
                'strength',opt_dict['strength'],'+',stren_p*diff,'\n',
                'hp_upper',opt_dict['hp_upper'],'+',stren_p*5*diff,'\n',
                'sanity_upper',opt_dict['sanity_upper'],'+',intel_p*5*diff,'\n'
            )
            opt_dict['charm'] = int(opt_dict['charm'])+charm_p*diff
            opt_dict['agile'] = int(opt_dict['agile'])+agile_p*diff
            opt_dict['intelligence'] = int(opt_dict['intelligence'])+intel_p*diff
            opt_dict['strength'] = int(opt_dict['strength'])+stren_p*diff
            opt_dict['hp_upper'] = int(opt_dict['hp_upper']) + stren_p*5*diff
            opt_dict['sanity_upper'] = int(opt_dict['sanity_upper']) + intel_p*5*diff
            self.write_opt(opt_dict)
            # print(hehe_opt.read_opt())
        
    

    def against_action(self,part_,skillful_ = 0,object_dict = None):
        """
            攻击与受击行为【默认发生环境是完成非战斗检定后(如先攻)，某攻击行为的伤害计算
            感觉……得先写好npc的类
            part_: 需要鉴定的属性 'agile'
            object_dict: 对方的类【至少比对的项目要有值
            skillful_: 熟练加值 【有则1
        """
        opt_dict = self.read_opt()
        try:
            input_ = opt_dict[part_]
            if not object_dict:
                input2_ = 0
                _against = 0
            else:
                input2_ = object_dict[part_]
                _against = sx.defence_checks(input2_,object_dict['level'])
        except:
            print('错误')

        if skillful_ != 0:
            _point = sx.ability_checks(input_,skillful_ = opt_dict['level'])    
        else:
            _point = sx.defence_checks(input_)

         # obj类的还没写

        if _point > _against:
            print('主体动作成功')
        else:
            print('主体动作失败')

        return _point,_against
        


    def use_equip_package_change(self,order_,obj):
        """
            背包变化函数，附加查询object的效果
        """
        opt_dict = self.read_opt()
        if order_ =='use':
            message = sx.check_normal(opt_dict,'items')
            print(message)

            if message[obj]['消耗'][0] == '是':
                sx.activate(obj)
                del opt_dict['package'][obj]
            # elif message[obj]['消耗'] == '限制次数':
            #     sx.activate(obj)
            # 【有点难，又得加东西，先放着，要不把package做成字典好了……
            elif message[obj]['消耗'][0] == '否':
                sx.activate(obj)

        elif order_ == 'lookup':
            message = sx.check_normal(opt_dict,'items')
            print(message[obj])

        elif order_ == 'equip':
        # 目前先不考虑装备……
            message = sx.check_normal(opt_dict,'items')
            sx.equip(obj)
            print(message[obj])
        
        elif order_ == 'single_item':
            message = sx.check_normal(opt_dict,'single_item',obj)
            print(message[obj])
        
    
    def atk_point_compute(self):
        """
            计算攻击力【
            = 武器属性(atk_base) + 属性调整值(modified_point) + 熟练加值(skillful_point)
        """
        

        pass


    def def_point_compute(self):
        """
            计算防御点数【这刀，我没有破防
            = 护甲属性(def_base) + 属性调整值(modified_point) + 特殊减免(forgive_point)
        
        """
        
        
        pass

# class nonplayer_charactor:
#     def __init__(self,npc_type) -> None:
#         self.npc_type = npc_type
#         pass
#     def npc_monster_init(self,diffculty):
#         """
#             刷怪器【怪起来了
#         """
#         pass


if __name__ == "__main__":
    hehe_opt = operator('hehe2',0,0,0,0)
    hehe_opt.init_opt()
    # hehe_opt.read_opt()
    # print(hehe_opt.read_opt())

    # hehe_opt.__update_opt__('package','增加热水壶')
    # hehe_opt.use_equip_package_change('use','热水壶')
    # hehe_opt.use_equip_package_change('lookup','热水壶') # 有bug

    # hehe_opt.__update_opt__('skill','更新普通一拳|2')

    hehe_opt.__update_opt__('exp','增加 10000')
    hehe_opt.opt_upgrade()

    pass
