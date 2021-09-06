# QQbot_Kal'tsit
明日方舟qq聊天机器人Kal'tsit【绝赞开(mo)发(yu)中】

作者：KOneLane

聊天机器人基于Graia、mirai、Saya等库，面向对象【python工程初体验】，站在巨人的肩膀上。源码真的很美，慢慢学习中！

## 更新 21.09.06

#### 1.优化bot文件目录
> |---MessageProcessor # 消息标准化处理中心  
> |---bot2             # bot主体启动文件  
> |---AuthSet          # 权限系统  
> |---story_xu         # 核心函数  
> |---readme           # 代码介绍  
> |---database:   
> |---|---Kal-tsit.db  # 数据库  
> |---|---beijing.pkl  # 地图文件  
> |---|---temp.png     # 缓存  
> |---function：  
> |---|---prts                 # prts功能  
> |---|---ForcastForTricks     # 天气预报功能  
> |---|---DarkTemple           # 消息处理器  
> |---|---squads_init          # 初始化干员  
> |---|---operator_rollbox_bot # 群作业系统  
  
### 2.添加/修改了功能

- 权限系统  
- 天气/地图查询  
- jieba分词器  
- prts查询爬虫  

**21.09.06 by KOneLane**


# 原始文档
## 1.功能实现

- 复读【？】
- 随机彩虹屁【你\*\*真的很\_\_\_\_】
- 每日轮换群作业系统
- 跑团属性初始化与变更记录
- 群成员战斗力【这个由Texas实现了】

最重要功能：跑团。由于现有机器人通常不实现数据存储，需要DM手动记录，计算也较为麻烦，于是开发了本地存储功能【不可以偷偷改数据！我是一个有职业修养的统计人！】。

## 2.安装简略步骤
需要事先配置好mirai-console，设置账号与authkey。

配置mirai完成后，在powershell里运行mcl，并且在终端中运行bot2.py，即可。在bot2.py中进行功能取舍，之后会开发功能管理配置文件【大概

>版本  
>mcl==2.6.7【稳定，更新后问题已修复】  
>graia-application-mirai==0.19.0  
>graia-broadcast==0.8.11  
>graia-saya==0.0.9
>graia-scheduler==0.0.4  
>DnD4PY==1.0.5  
>其他库版本影响不大

安装mirai-console这一步，大概会难倒一片人qwq

[graia文档](https://graia-document.vercel.app/docs/guides/installation), [mirai论坛](https://mirai.mamoe.net/)，[DnD4py一些小操作](https://github.com/bacook17/DnD4py/)

如果只是想看看，可以加个好友※，591016144。

## 3.其他
依然在不断编辑中，但是时间实在太少了，由于对具体规则的不了解，开发迟迟难以推进。

数据库(database.xlsx)亟需丰富，部分代码冗余比较高……边写边学吧。

欢迎有跑团经验的朋友带我玩/测试！可以做不同内容的适配。

2021.08.19
