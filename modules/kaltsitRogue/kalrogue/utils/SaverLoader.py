#! /usr/bin/env python3
# coding:utf-8
'''用于读取json'''
import json
import os

class SaverLoader:

    # 信息路径 - 后续继续补充
    memberMessageDir = 'resources/memberMessages.json'
    gameSettingsDir  = 'resources/gameBasicSetting.json'
    operatorsDir     = 'resources/elements/operators.json'
    itemDir          = 'resources/elements/item.json'
    elementsDir      = 'resources/elements/elements.json'

    @classmethod
    def get_project_path(cls):
        """得到项目路径"""
        project_path = os.path.join(
            os.path.dirname(__file__),
            "..",
        )
        return project_path

    @classmethod
    def jsonReader(cls, filename):
        """读取指定文件并返回字典"""
        with open(cls().get_project_path()+ '/' + filename,'r',encoding='utf8')as fp:
            json_data = json.load(fp)
        return json_data

    @classmethod
    def SaveChecker(cls, group):
        '''检索存档目录 检查本群是否有存档
        output: search_list 存档列表
        '''
        save_dir = '/resources/saves/' # 存档路径
        filenames=os.listdir(cls().get_project_path()+ save_dir)
        search_list = list(filter(None ,map(lambda x:x if x.startswith(str(group)) else None, filenames)))
        return search_list

    @classmethod
    def jsonSaver(cls, filename, obj):
        '''保存json
        '''
        with open(cls().get_project_path()+ '/' + filename,'w',encoding='utf8')as fp:
            json.dump(obj, fp, ensure_ascii=False)

    

print(SaverLoader.SaveChecker(""))