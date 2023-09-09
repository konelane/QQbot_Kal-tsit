#! /usr/bin/env python3
# coding:utf-8

class MessageProcesser:
    """消息标准化处理器-群聊类"""
    def __init__(
            self
            ,message
            ,group
            ,member
    ) -> None:

        self.text = message.display
        self.id = member.id
        self.msgout = {
            'id':self.id,
            'text_split':self.text.split(' '),
            'group_id':group.id,
            'text_ori':self.text,                                # 21.11.26 添加复读打断功能时加入
            'type':'group',                                      # 21.12.17 添加漂流瓶功能时加入
            'name':member.name,                                  # 22.02.26 添加签到功能时加入
            # 'pub_time':''
        }
        pass

    def text_processer(self):
        if self.text in ['[图片]', '<! 不支持的消息类型 !>', '[APP消息]']:
            return ''
        else:
            return self.msgout


