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
        host="http://localhost:8080",
        verify_key="yourAutherKey",
        account=123456789,
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
    saya.require("modules.StopRepeat")
    saya.require("modules.Setu")
    saya.require("modules.Prts")


app.launch_blocking()