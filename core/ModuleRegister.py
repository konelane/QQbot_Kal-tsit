#!/usr/bin/env python3
# -*- coding: utf-8 -*-

Modules: list = []


class Module:
    name: str  # 模块名称
    file_name: str  # 模块的文件名或所在文件夹的名称
    author: list  # 作者列表
    description: None = None  # 模块描述
    usage: None = None  # 模块用法
    arg_description: None = None  # 参数描述
    can_disable: bool = True  # 可否分群关闭

    def __init__(
        self,
        name: str,  # 模块名称
        file_name: str,  # 模块的文件名或所在文件夹的名称
        author: list,  # 作者列表
        description: None = None,  # 模块描述
        usage: None = None,  # 模块用法
        arg_description: None = None,  # 参数描述
        can_disable: bool = True,  # 可否分群关闭
    ):
        self.name = name
        self.file_name = file_name
        self.author = author
        self.description = description
        self.usage = usage
        self.arg_description = arg_description
        self.can_disable = can_disable

    def register(self):
        Modules.append(self)
