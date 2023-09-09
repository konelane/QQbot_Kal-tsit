from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.exception import MessageTooLong
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.twilight import Twilight
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Plain, Image, Source
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import FullMatch, ArgumentMatch, RegexResult, RegexMatch, ArgResult
from graia.ariadne.model import Group, Member

import re
from os.path import basename
import requests

from core.config.BotConfig import BasicConfig
from core.decos import DisableModule, check_group, check_member, check_permitGroup
from core.MessageProcesser import MessageProcesser
from core.ModuleRegister import Module
from database.kaltsitReply import blockList, text_table

# 移植自 https://github.com/YanQian01/sagiri-bot

channel = Channel.current()

module_name = basename(__file__)[:-3]

Module(
    name='GithubInfo',
    file_name=module_name,
    author=["SAGIRI-kawaii"],
    usage='modules.GithubInfo',
).register()


class GithubInfo:

    def __init__(self, msg) -> None:
        self.msg = msg
        self.filename = BasicConfig().databaseUrl
        self.groupId = str(msg['group_id'])
        self.text = msg['text_split']
        pass

    def main(self, image: bool=False):
        keyword = self.text[1]
        url = "https://api.github.com/search/repositories?q="
        img_url = "https://opengraph.githubassets.com/c9f4179f4d560950b2355c82aa2b7750bffd945744f9b8ea3f93cc24779745a0/"
        resp = requests.get(url=url + keyword)
        try:
            result = (resp.json())["items"]
        except:
            result = None
        
        if not result:
            return "没有搜索到结果呢~"
        elif image:
            img_url += result[0]["full_name"]
            resp = requests.get(img_url)
            content = resp.read()
            return content
        else:
            result = result[0]
            print(result)
            name = result["name"]
            owner = result["owner"]["login"]
            description = result["description"]
            repo_url = result["html_url"]
            stars = result["stargazers_count"]
            watchers = result["watchers"]
            language = result["language"]
            forks = result["forks"]
            issues = result["open_issues"]
            repo_license = result["license"]["key"] if result["license"] else "无"
            text = ""
            text+=f"名称：{name}\n"
            text+=f"作者：{owner}\n"
            text+=f"描述：{description}\n"
            text+=f"链接：{repo_url}\n"
            text+=f"stars：{stars}\n"
            text+=f"watchers：{watchers}\n"
            text+=f"forks：{forks}\n"
            text+=f"issues：{issues}\n"
            text+=f"language：{language}\n"
            text+=f"license：{repo_license}"
            
            return text
        


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([RegexMatch(r'\#hub.*').flags(re.X)])
        ],
        decorators=[
            check_group(blockList.blockGroup), 
            check_member(blockList.blockID), 
            check_permitGroup(blockList.permitGroup), 
            DisableModule.require(module_name)
        ]
    )
)
async def github_info(app: Ariadne, message: MessageChain, group: Group, member: Member):
    

    slightly_inittext = MessageProcesser(message, group, member)
    msg_info_dict = slightly_inittext.text_processer()   

    if msg_info_dict['text_split'][0] not in ['#hub']:
        return 
    else:
        git = GithubInfo(msg_info_dict)
        msg = git.main()
        await app.send_group_message(group, MessageChain([
                Plain(msg)
            ]))