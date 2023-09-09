import random
import re
from os.path import basename

from selenium.webdriver.common.by import By

from core.decos import check_group, check_member, DisableModule, check_permitGroup
from core.ModuleRegister import Module
from core.MessageProcesser import MessageProcesser
from database.kaltsitReply import blockList

from graia.ariadne.message.parser.twilight import RegexMatch
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At
from graia.ariadne.message.parser.twilight import Twilight
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from selenium import webdriver # 性能不足
from time import sleep
from selenium.webdriver.common.keys import Keys

'''骰子功能'''

channel = Channel.current()

module_name = basename(__file__)[:-3]

Module(
    name='Couplet',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.Couplet',
).register()


class couplet_api:
    def __init__(self,text) -> None:
        self.text = text
        pass

    def __init_chrome(self,load = 1):
        option = webdriver.ChromeOptions()
        # 加载图片
        prefs = {
                    'profile.default_content_setting_values': {
                        'images': load,
                        'permissions.default.stylesheet': 2
                    }
                } # 2是不加载，1是加载
        option.add_experimental_option('prefs', prefs)
        option.add_experimental_option('excludeSwitches', ['enable-logging'])#禁止打印日志 # 没用
        option.add_experimental_option('excludeSwitches', ['enable-automation'])#实现了规避监测
        option.add_argument('log-level=3')#INFO = 0 WARNING = 1 LOG_ERROR = 2 LOG_FATAL = 3 default is 0
        option.add_argument('headless')#“有头”模式，即可以看到浏览器界面，若要隐藏浏览器，可设置为 "headless"
        option.add_argument('--disable-javascript')
        dr0 = webdriver.Chrome(chrome_options = option)#得到操作对象
        return dr0

    def CoupletGet(self):
        """获得信息文字源代码"""
        dr0 = self.__init_chrome(load = 2) # 设置为不加载图片
        dr0.get(f'https://ai.binwang.me/couplet/')
        
        dr0.find_element(By.CLASS_NAME,'couplet-input').send_keys(self.text)
        dr0.find_element(By.CLASS_NAME,'couplet-input').send_keys(Keys.ENTER)
        # dr0.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div[3]/button[1]').click()
        sleep(3)
        # '/html/body/div/div[1]/div[2]/div[1]/div[2]'
        # WebDriverWait(dr0,10).until(EC.visibility_of_element_located(dr0.find_element_by_css_selector('#app > div.page > div.content > div.couplet-text.couplet-text_down > div.couplet-bd')))
        return_text = dr0.find_element(By.XPATH, '/html/body/div/div[1]/div[2]/div[2]/div[2]').text

        # dr0.quit()

        return return_text


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'\#对 .*').flags(re.X)])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), check_permitGroup(blockList.permitGroup), DisableModule.require(module_name)],
    )
)
async def Dice(
    app: Ariadne, 
    message: MessageChain,
    group: Group,
    member: Member 
):

    slightly_inittext = MessageProcesser(message,group,member)
    msg_info_dict = slightly_inittext.text_processer()
    input_text = '，'.join(x for x in msg_info_dict['text_split'][1::])

    couplet_a = couplet_api(input_text)
    await app.send_group_message(group, MessageChain(
        Plain(couplet_a.CoupletGet())
    ))