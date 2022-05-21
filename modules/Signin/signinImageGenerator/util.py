#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from pathlib import Path
from typing import Optional, Union

import httpx
from PIL import Image, ImageDraw
from PIL.ImageFont import FreeTypeFont
from pydantic import BaseModel

Ink = Union[str, int, tuple, tuple]


def get_qlogo(id: int) -> bytes:
    """获取QQ头像
    Args:
        id (int): QQ号
    Returns:
        bytes: 图片二进制数据
    """
    resp = httpx.get(f"http://q1.qlogo.cn/g?b=qq&nk={id}&s=640")
    return resp.content


def get_time() -> str:
    """获取格式化后的当前时间"""
    return time.strftime("%Y/%m/%d/ %p%I:%M:%S", time.localtime())


def cut_text(
    font: FreeTypeFont,
    origin: str,
    chars_per_line: int,
):
    """将单行超过指定长度的文本切割成多行
    Args:
        font (FreeTypeFont): 字体
        origin (str): 原始文本
        chars_per_line (int): 每行字符数（按全角字符算）
    """
    target = ""
    start_symbol = "[{<(【《（〈〖［〔“‘『「〝"
    end_symbol = ",.!?;:]}>)%~…，。！？；：】》）〉〗］〕”’～』」〞"
    line_width = 400 # chars_per_line * font.getlength("一")
    for i in origin.splitlines(False):
        if i == "":
            target += "\n"
            continue
        j = 0
        for ind, elem in enumerate(i):
            if i[j : ind + 1] == i[j:]:
                target += i[j : ind + 1] + "\n"
                continue
            elif len(i[j:ind+1])*16 <= line_width:# font.getlength(i[j : ind + 1]) <= line_width:
                continue
            elif ind - j > 3:
                if i[ind] in end_symbol and i[ind - 1] != i[ind]:
                    target += i[j : ind + 1] + "\n"
                    j = ind + 1
                    continue
                elif i[ind] in start_symbol and i[ind - 1] != i[ind]:
                    target += i[j:ind] + "\n"
                    continue
            target += i[j:ind] + "\n"
            j = ind
    return target.rstrip()


def exp_bar(w: int, h: int, rato: float, bg: Ink = "black", fg: Ink = "white") -> Image.Image:
    """获取一个经验条的图片对象
    Args:
        w (int): 宽度
        h (int): 高度
        rato (float): 比例
        bg (_Ink): 背景颜色
        fg (_Ink): 前景颜色
    Returns:
        Image.Image: 图片对象
    """
    origin_w = w
    origin_h = h
    w *= 4
    h *= 4
    bar_canvase = Image.new("RGBA", (w, h), "#00000000")
    bar_draw = ImageDraw.Draw(bar_canvase)
    # draw background
    bar_draw.ellipse((0, 0, h, h), fill=bg)
    bar_draw.ellipse((w - h, 0, w, h), fill=bg)
    bar_draw.rectangle((h // 2, 0, w - h // 2, h), fill=bg)

    # draw exp bar
    n_w = w * rato if rato <= 1 else w
    bar_draw.ellipse((0, 0, h, h), fill=fg)
    bar_draw.ellipse((n_w - h, 0, n_w, h), fill=fg)
    bar_draw.rectangle((h // 2, 0, n_w - h // 2, h), fill=fg)

    return bar_canvase.resize((origin_w, origin_h), Image.LANCZOS)


class Reward(BaseModel):
    """奖励"""

    name: Optional[str] = None
    """奖励名称"""

    num: int
    """奖励数量"""

    ico: Optional[Union[str, Path]]
    """奖励图标"""
