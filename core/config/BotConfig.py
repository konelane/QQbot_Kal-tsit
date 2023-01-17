#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''移植自 https://github.com/Redlnn/redbot/tree/master/util/config.py'''

from pathlib import Path
import os
import orjson
from pydantic import AnyHttpUrl, BaseModel

# from .path import config_path, data_path
data_path = os.path.dirname(__file__) + ''
config_path = os.path.dirname(__file__) + ''


class RConfig(BaseModel):
    __filename__: None = None  # 无需指定后缀，当实例化时不传入该参数则与 BaseModel 无异
    __in_data_folder__: bool = False

    def __init__(self, **data) -> None:
        if self.__filename__ is None:
            super().__init__(**data)
            return
        elif self.__in_data_folder__:
            path = Path(data_path, f'{self.__filename__}.json')
        else:
            path = Path(config_path, f'{self.__filename__}.json')

        if not path.exists():
            super().__init__(**data)
            with open(path, 'w') as f:
                f.write(self.json(indent=2, ensure_ascii=False))
        else:
            with open(path, 'rb') as fb:
                file_data = orjson.loads(fb.read())
            if data:
                for key, item in data.items():
                    file_data[key] = item
            super().__init__(**file_data)

    def save(self) -> None:
        if self.__filename__ is None:
            raise ValueError('__filename__ is not defined')
        elif self.__in_data_folder__:
            path = Path(data_path, f'{self.__filename__}.json')
        else:
            path = Path(config_path, f'{self.__filename__}.json')
        with open(path, 'w') as f:
            f.write(self.json(indent=2, ensure_ascii=False))

    def reload(self) -> None:
        if self.__filename__ is None:
            raise ValueError('__filename__ is not defined')
        elif self.__in_data_folder__:
            path = Path(data_path, f'{self.__filename__}.json')
        else:
            path = Path(config_path, f'{self.__filename__}.json')
        with open(path, 'rb') as fb:
            data = orjson.loads(fb.read())
        super().__init__(**data)


class MAHConfig(RConfig):
    account: int = 1234512345#  bot账号
    host: AnyHttpUrl = 'http://localhost:端口号'
    verifyKey: str = ''


class AdminConfig(RConfig):
    masterId: int = 114514  # 机器人主人的QQ号
    masterName: str = '1919810'
    admins: list = [114514]


class BasicConfig(RConfig):
    __filename__: str = 'Filename'

    botName: str = 'botName'
    logChat: bool = False
    console: bool = False
    debug: bool = False
    databaseUrl: str = '本地数据库地址'
    # mysql+asyncmy://user:pass@hostname/dbname?charset=utf8mb4
    admin: AdminConfig = AdminConfig()
    mah_cfg = MAHConfig()


class ModulesConfig(RConfig):
    __filename__: str = 'modules'
    enabled: bool = True  # 是否允许加载模块
    globalDisabledModules: list = []  # 全局禁用的模块列表
    disabledGroups: dict = {'BotManage': [123456789, 123456780]}  # 分群禁用模块的列表


basic_cfg = BasicConfig()
modules_cfg = ModulesConfig()
