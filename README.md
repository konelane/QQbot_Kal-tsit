# QQbot_Kal'tsit
明日方舟qq聊天机器人Kal'tsit【绝赞开(mo)发(yu)中】

作者：KOneLane

杰出贡献青年(?)：JesseZhu

功能文档请[查看链接](https://konelane.github.io/QQbot_Kal-tsit/#/)

聊天机器人基于Graia、mirai、Saya等库，面向对象【python工程初体验】，站在巨人的肩膀上。源码真的很美，慢慢学习中！

## 更新 22.02.23

首先，更新了框架！！

现在bot使用的是Graia-Ariadne框架，真的很舒服！推荐

优化了一些逻辑、代码结构等等……调整了部分文字小细节。

更新了星际争霸的突变查询功能，更新了四人牌桌车队组建功能。

2022年2月22日星期二，本二次元的小努力总算没有白费。



## 更新  22.02.13

试图为凯尔希加一个文档页面~

## 更新 22.01.17

发生了不可逆事故，腾讯开始对bot进行风控，服务器运行卡顿，mcl更换消息码……一系列事情之下，可能需要更换凯尔希的框架咯。

因此，先把最近的更新放上来……咸鱼氦核还是更新了不少东西的！

> 更新记录 21.12.18  
> 优化bot文件目录  
> |---MessageProcessor # 消息标准化处理中心  
> |---bot2       # bot主体启动文件  
> |---AuthSet      # 权限系统  
> |---story_xu     # 核心函数  
> |---readme      # 项目介绍-帮助  
> |---database:  
> |---|---Kal-tsit.db    # 数据库  
> |---|---beijing.pkl    # 地图文件  
> |---|---temp.png     # 缓存图片   
> |---|---stopRepeat.jpg  # 打断复读使用的图片  
> |---|---adventureMap.pkl # 生成的地下城地图  
> |---function：  
> |---|---prts         # prts功能  
> |---|---ForcastForTricks   # 天气预报功能  
> |---|---DarkTemple      # 消息处理器-功能核心组件  
> |---|---squads_init      # 初始化干员  
> |---|---praise        # 夸夸   
> |---|---CardSearch      # ygo查卡功能  
> |---|---couplet        # 对对子，出对！  
> |---|---operator_rollbox_bot # 自限作业抽取  
> |---|---adventure       # 肉鸽迷宫  
> |---|---stopRepeat      # 打断复读  

打眼一看文件目录，是不是发现比上一版多了好多功能？那么为什么半天没有更新呢……因为懒，哈哈。还有一些功能没有单独放一个文件，譬如凯尔希的办公桌（漂流瓶），以及每个bot都少不了的抽瑟图功能之类……

首先还是老样子，几个带图片的功能用不成：地图、打断复读、抽se图（这也是本次更新的缘由……）

个人比较满意的是地下城（adventure.py）和复读打断功能！太喜欢了以至于经常自己刷五句话哈哈哈。

database里会保存每个群的聊天记录（复读超过五句只会保存一句），同时还解包了YGO的app，把卡面数据丢进去了（写好之后就没更新过……已经落后版本了哈哈）。

对对子功能也很好玩，喜欢谜语的大家一定要试试。模型是跑了四天的lstm……但是依然谜语（

其他的功能没什么好介绍的了。这次腾讯出手，真是难受了。不知道凯尔希能不能挺住。群里有大佬推荐更换框架，有时间就试试吧……优先级在todolist上不是很靠前，大概是看透了凯尔希被很多人只当做抽图工具这一事实【捂脸






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
