#! /usr/bin/env python3
# coding:utf-8
import os

class TextReceiver:
    '''用于接收文本 - 回传给kaltsit'''
    log_mode = True   # 记录模式


    @classmethod
    def LogSaver(cls):
        '''文本记录log'''


    @classmethod
    def TextPresent(cls, text_input):
        '''文本透传 - to ariadne'''
        
        return text_input, 'out_'
        
    @classmethod
    def get_project_path(cls):
        """得到项目路径"""
        project_path = os.path.join(
            os.path.dirname(__file__),
            "..",
        )
        return project_path

    @classmethod
    def textRead(cls, node_name, story_line, part_id):
        '''根据node_name查文本'''
        text_dir = cls().get_project_path() + '/resources/story/' + story_line + '/' + node_name + '/'+ str(part_id) + '.txt'
        
        with open(text_dir, 'r' ,encoding='utf-8') as f:
            text_out = f.read()

        return text_out

    