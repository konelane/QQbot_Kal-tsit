#! /usr/bin/env python3
# coding:utf-8

from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain,At,Image
import jieba # 实验性分词
import re
from functools import partial

class MessageProcesser:
    """消息标准化处理器"""
    def __init__(
        self
        ,message
        # ,group
        ,member
    ) -> None:
        self.text = message.get(Plain)[0].text
        self.id = member.id
        self.msgout = {
            'id':self.id,
            'text_split':message.get(Plain)[0].text.split(' '),
            'text_jieba':''
        }
        pass

    def __jieba_prepare(self):
        jieba.initialize()
        # 添加用户专门词
        newwords = [
            '老女人','谜语人','凯尔希','猞猁','哈哈哈哈哈','舰桥'
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