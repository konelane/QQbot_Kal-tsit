
# 结构设计

## 故事节点结构

故事节点json, story-keeping-unit结构

```python
{
    '''
    story-keeping-unit:  # 最小行动单元 仅包含最小的一段行动 中途无法存档
            - for save 保存与读取使用
            - set 设置写好
    '''
    
    "story_node_id":{
        "node_id":"amiya_story_line1",                          # 节点故事线 set
        "choice_made":[],                                       # 做出的选择 for save
        "node_type":"choice",   # choice | story | dice |       # 节点类型 set
        "story_text_file_name":"amiya_story_line",              # 文本文件夹名称 set
        "choice_maker":591016144,                               # 做出选择者 for save   
        "position_save":1,                                      # 已进行到的位置 for save
        "node_amount":5,                                        # 节点总共步数(故事长度) set
        "is_done":0,            # 0 未完成                       # 当前故事节点是否已全部完成 for save  TODO:"检查"方法
        "game_time_pass":"17:00",                               # 经过时游戏时间
        "dice_position_list":[2],                               # 骰子位置 set
        "dice_position":{                                                 
            2:"1, 6, 0"         # 1d6 + 0                       # 骰子位置对应内容 set
        },                                                              
        "dice_result":[5],                                      # 骰子结果 for save
        "choice_result":1,                                      # 选择结果 for save
        "next_node_id":"amiya_story_line2",                     # 下一节点 set
        "rqmt_node_list":[1,3],                                 # 节点依赖卡控节点列表 set
        "rqmt_node_dict":{                                             
            1:["amiya", "operator","lock"],                     # set 依赖内容, 【依赖类型 operator | item | event 】, 未达成时状态 分支节点
            2:["60", "dice", "amiya_story_line1-2"])            # set 依赖内容, 【依赖类型 dice】, 未达成时状态 分支节点
            3:["kaltsit-coffee-cup", "item", "hurt"]            # set 依赖内容, 依赖类型, 【未达成时状态 lock | hurt | dice】
        },
        "rqmt_got_list":[1, 0],                                 # set 1 已具备 0 未具备  TODO:"检查"方法
        "reward_list":[4],                                      # set 带有奖励的节点 TODO:"检查"方法
        "reward":{                                                         
            4:("amiya", "operator", "finish_step")              # set 达成奖励内容, 奖励类型 operator | item, 奖励发放条件 finish_step | finish_node
        },
    }
}
```

故事节点文件夹结构

>resources/story  
>|---- story_line_name  
>|----|---- story_line_name_1.json  
>|----|---- story_line_name_1-2.json  
>|----|---- story_line_name_2.json  
>|----|---- dir_story_line_name_1  
>|----|----|---- 0.txt  
>|----|----|---- 1.txt  
>|----|---- dir_story_line_name_1-2  
>|----|----|---- 0.txt  
>|----|----|---- 1.txt  
>|----|---- dir_story_line_name_2  
>|----|----|---- 0.txt  
>|----|----|---- 1.txt  


## 存档结构

```python
{
    '''
    save-unit:  # 存档
            - for save 保存与读取使用
            - set 设置写好
    '''

    "group_id":114514,                                              # 群号
    "mode_list":["mode_name1", "mode_name2"],                       # 游玩的模组
    "story_node_list":["story_node_id1", "story_node_id2"],         # 经历过的故事清单
    "credit_pool":1919,                                             # 信用池 for save
    "is_end":0,                                                     # 是否结局 1 已结局
    "endding_id":-1,                                                # 结局编号
    "doctor_condition":{                                            # 博士状态 待变更
        "hp" : 0,
        "coc5":{
            "str":60,  # 力量
            "dex":60,  # 敏捷
            "pow":60,  # 意志
            "con":60,  # 体质
            "app":60,  # 外貌
        },
        "bag" : ["origin_cash"],
        "bag_dict":{
            "origin_cash":{             # eg.源石锭
                "name":"精炼源石锭",     # 名称
                "amt":0,                # 数量
                "type":"consumption",   # 类型 消耗品
            }, 
        },
        "friends": [],
        "friends_dict":{
            "kaltsit":{
                "reliance":0,           # 信赖
                "anger":0,              # 怒气【特殊属性存放于干员json中】
                "san_point":100,        # san值
                "position":"medician",  # 职业
            }
        },
        "kaltsit_anger": 0,
    }, 
    "game_environment":{                                            # 游戏状态记录
        "game_time":'18:00'                                         # 游戏内时间
    },

    "story_node_dict":{

        "story_node_id1":{
            "略 见上文":0,
        },
        "story_node_id2":{
            "略 见上文":0,
        },
    },
    
}
```

存档文件夹结构

>resources/saves  
>|---- group_id_221105_0.json  
>|---- group_id_221104_1.json  


## 干员信息结构

用于描述干员信息，可能在部分环节进行检测或调用。可弹性增删。

```python

"kaltsit":{
    "reliance":0,           # 信赖
    "anger":0,              # 怒气【特殊属性存放于干员json中】
    "san_point":100,        # san值
    "position":"medician",  # 职业
    "item":["Mon3tr"],      # 携带道具
    "item_dict":{
        "Mon3tr":{},        # 根据需要设计
    },
    
}

```


## 