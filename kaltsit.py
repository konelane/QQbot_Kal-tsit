import pkgutil

from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.saya import Saya

from core.config.BotConfig import MAHConfig

saya = create(Saya)
app = Ariadne(
    connection=config(
        MAHConfig().account,  # 你的机器人的 qq 号
        MAHConfig().verifyKey,  # 填入你的 mirai-api-http 配置中的 verifyKey
        # 以下两行（不含注释）里的 host 参数的地址
        # 是你的 mirai-api-http 地址中的地址与端口
        # 他们默认为 "http://localhost:8080"
        # 如果你 mirai-api-http 的地址与端口也是 localhost:8080
        # 就可以删掉这两行，否则需要修改为 mirai-api-http 的地址与端口
        HttpClientConfig(host=MAHConfig().host),
        WebsocketClientConfig(host=MAHConfig().host),
    ),
)

with saya.module_context():
    saya.require("modules.Readme")
    saya.require("core.BotManager")
    saya.require("core.Botoff")
    saya.require("modules.Praise")
    saya.require("modules.Signin")
    saya.require("modules.Sweep")
    saya.require("modules.StoryDice")
    saya.require("modules.DatabaseSearch")
    saya.require("modules.Setu")
    saya.require("modules.Prts")
    saya.require("modules.Couplet")
    saya.require("modules.Homework")
    saya.require("modules.Nudge")
    saya.require("modules.ForcastForTricks")
    saya.require("modules.HusGet")
    saya.require("modules.Gacha")
    saya.require("modules.AkGuess")
    saya.require("modules.KHeart")
    # saya.require("modules.DiceKaltsit")
    saya.require("modules.kaltsitRogue")
    saya.require("modules.Train")
    saya.require("modules.GithubInfo")

app.launch_blocking()
