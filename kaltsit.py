import asyncio

from graia.ariadne.app import Ariadne
from graia.ariadne.model import MiraiSession
from graia.broadcast import Broadcast
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour

loop = asyncio.new_event_loop()
bcc = Broadcast(loop=loop)
app = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host="http://localhost:8082",
        verify_key="KOneLaneKaltsit",
        account=591016144,  # 2256896694
    ),
)
saya = Saya(bcc)
saya.install_behaviours(BroadcastBehaviour(bcc))

with saya.module_context():
    saya.require("modules.Readme")
    saya.require("core.BotManager")
    saya.require("core.Botoff")
    saya.require("modules.Praise")
    saya.require("modules.Signin")
    saya.require("modules.Sweep")
    saya.require("modules.FourMemberTeam")
    saya.require("modules.StoryDice")
    saya.require("modules.DatabaseSearch")
    # saya.require("modules.StopRepeat")
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

app.launch_blocking()