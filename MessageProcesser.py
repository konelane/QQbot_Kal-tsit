'''
Author: KOneLane
Date: 2021-08-27 17:28:01
LastEditors: KOneLane
LastEditTime: 2022-02-27 17:33:08
Description: 
version: V
'''
#! /usr/bin/env python3
# coding:utf-8

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At, Image

import jieba # 实验性分词
import re
from functools import partial


class MessageProcesser:
    """消息标准化处理器-群聊类"""
    def __init__(
        self
        ,message
        ,group
        ,member
    ) -> None:
        # 将图片任务分离出去
        # message = message.asDisplay()
        # self.text = message.get(Plain)[0].text
        
        self.text = message.asDisplay()
        # self.text = '' # 会导致图片也被识别成文字
        self.id = member.id
        self.msgout = {
            'id':self.id,
            'text_split':self.text.split(' '),
            'text_jieba':'',
            'group_id':group.id,
            'text_ori':self.text,                                # 21.11.26 添加复读打断功能时加入
            'type':'group',                                      # 21.12.17 添加漂流瓶功能时加入
            'name':member.name,                                  # 22.02.26 添加签到功能时加入
            # 'pub_time':''
        }
        pass

    def __jieba_prepare(self):
        jieba.initialize()
        # 添加用户专门词
        newwords = [
            '老女人','谜语人','凯尔希','猞猁','哈哈哈哈哈','舰桥','冒泡'
        ]
        for word in newwords:
            jieba.add_word(word,1000000)
        def remove_special_characters(text,pattern):
            filtered_text = re.sub(pattern, '', text)
            return filtered_text
        def jb_cut(text):
            tokens = jieba.cut(text)
            filtered_tokens = [str(word) for word in tokens]
            return filtered_tokens

        PATTERN = '[a-zA-Z|\n|【|】|——|“|”|%|（|）|《|》|\d+月\d+日|\d+日|\d+年|\d+月]'
        tokenized_corpus = jb_cut(remove_special_characters(self.text,PATTERN))
        return tokenized_corpus

    def text_processer(self):
        token = self.__jieba_prepare()
        self.msgout['text_jieba'] = token
        return self.msgout



class PersonalNoteIndex:
    """消息标准化处理器-群聊类"""
    def __init__(
        self
        ,message
        ,group
        ,member
    ) -> None:
        self.text = message.get(Plain)[0].text
        self.id = member.id
        self.msgout = {
            'id':self.id,
            'text_split':message.get(Plain)[0].text.split(' '),
            # 'text_jieba':'',
            # 'group_id':group.id,
            'text_ori':self.text,                                # 21.11.26 添加复读打断功能时加入
            'type':'person'                                       # 21.12.17 添加漂流瓶功能时加入
            # 'pub_time':''
        }
        pass