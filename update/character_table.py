#! /usr/bin/env python3
# coding:utf-8
import json 
import os

def get_project_path():
    """得到当前文件父目录路径"""
    project_path = os.path.join(
        os.path.dirname(__file__),
        "",
    )
    return project_path

with open(get_project_path() + 'character_table.json','r',encoding='utf8')as fp:
    json_data = json.load(fp)
    # print('这是文件中的json数据：',json_data)
    print('这是读取到文件数据的数据类型：', type(json_data))
        
    json.dump(
        {'list':list(filter(lambda x: x.startswith('char'), list(json_data.keys())))}, 
        open(get_project_path() + 'character_list.json', 'w')
    )
    print("character_list.json 保存完毕")