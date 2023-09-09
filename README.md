## 明日方舟凯尔希bot

作者：氦核

鸣谢：JesseZhu，赔老子的机甲

交流群 607148401

邀请/添加凯尔希好友前请先加群艾特群主。

当前暂不开放bot好友申请。


## 功能一览

[功能文档](https://konelane.github.io/Docs_of_Kal-tsit/)，[更新日志](https://konelane.github.io/Docs_of_Kal-tsit/Changelog.html)

[罗德岛午夜逸闻功能介绍](https://konelane.github.io/Docs_of_Kal-tsit/KaltsitRogue.html)

可能更新不及时。见谅。

## 部署自己的凯尔希

首先说明，凯尔希代码已经开源，作者无义务解答任何关于部署的问题。

你需要：

 - 一台联网的电脑，一个qq小号。
 - python基础和mirai框架使用基础，数据库增删改查简单能力。
 - 提问的智慧。

>如果你不曾学习过任何python，建议食用[社区文档](https://graiax.cn/)。

### 部署步骤：

1. 安装mirai-console并登陆mirai。请自行搜索方案。[mirai社区](https://mirai.mamoe.net/)    
2. 安装python环境。公共凯尔希py版本`3.11.2`  
3. 安装依赖`-r requirements.txt`，selenium爬虫库使用也需要使用chrome与对应chromedriver，请自行搜索。  
4. 安装graia-ariadne环境，参考[社区文档](https://graiax.cn/)，建议full安装省心。  
5. 设置各个`core/config/`目录下的json文件，包括管理员账号号码、机器人账号密码与mah的端口、Auth key，保证host端口无占用。以及数据库父目录地址。  
6. 登陆mirai后，在命令行里进入项目父目录，运行`python 你的目录/kaltsit.py`。  


### 几个配置可能用到的文件介绍

```text
kaltsit.py -- 控制模组全局开关
database/table_install.py -- 数据库建表文件 首次运行时使用。

database/kaltsitReply.py -- 凯尔希回复与权限配置 白名单群 黑名单群等
core/config/kaltsit_config.json -- 基本设置
core/config/modules.json -- 控制各个群的模组使用
core/config/text2img.json -- 生成文字图片的配置 可以不用更改

update/update.sh -- 用于更新干员信息与图片，更新抽卡和猜干员两个功能的数据。
```



所有游戏资源内容，为上海鹰角网络版权所有。来自项目[yuanyan3060/Arknights-Bot-Resource](https://github.com/yuanyan3060/Arknights-Bot-Resource)。

项目仅供学习交流。遵循[AGPL 3.0 Licensed](https://github.com/konelane/QQbot_Kal-tsit/blob/main/LICENSE)。