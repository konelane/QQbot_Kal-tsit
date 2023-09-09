#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
仿锤子便签的文字转图片
"""

import os
import time
from io import BytesIO
from pathlib import Path

from graia.ariadne.util.async_exec import cpu_bound
from PIL import Image as Img
from PIL import ImageDraw, ImageFont

from core.config.BotConfig import RConfig, basic_cfg, BasicConfig

root_path = Path(__file__).parent.parent.resolve()


class Text2ImgConfig(RConfig):
    __filename__: str = 'text2img'
    # 字体文件的文件名（带后缀名），支持ttf/otf/ttc/otc
    # 字体文件请放在根目录的 fonts 文件夹内
    FontName: str = 'OPPOSans-B.ttf'
    # 若使用ttc/otc字体文件，则填写要加载的ttc/otc的字形索引号，不懂请填1
    # 具体索引号可安装 afdko 后使用 `otc2otf -r {name}.ttc`查看
    # afdko: https://github.com/adobe-type-tools/afdko
    TTCIndex: int = 1
    FontSize: int = 50  # 字体大小
    FontColor: str = '#645647'  # 字体颜色
    LineSpace: int = 30  # 行距
    TextMargin: int = 80  # 文字范围到内框的距离
    CharsPerLine: int = 25  # 每行长度（单位：字符数量，以中文字符为准）
    BackgroundColor: str = '#fffcf6'  # 背景颜色
    BorderSideMargin: int = 50  # 外框距左右边界距离
    BorderTopMargin: int = 70  # 外框距上边界距离
    BorderBottomMargin: int = 250  # 外框距下边界距离
    BorderInterval: int = 5  # 内外框距离
    BorderSquareWrapWidth: int = 5  # 外边框四角的小正方形边长
    BorderOutlineColor: str = '#e9e5d9'  # 边框颜色
    BorderOutlineWidth: int = 5  # 边框描边（内描边）厚度


hr = '{hr}'


def _get_time(mode: int = 1) -> str:
    """
    返回当前时间
    """
    time_now = int(time.time())
    time_local = time.localtime(time_now)
    if mode == 2:
        dt = time.strftime('%Y-%m-%d_%H-%M-%S', time_local)
    else:
        dt = time.strftime('%Y-%m-%d %H:%M:%S', time_local)
    return dt


def cut_text(
        origin: str,
        font: ImageFont.FreeTypeFont,
        chars_per_line: int,
):
    target = ''
    start_symbol = '[{<(【《（〈〖［〔“‘『「〝'
    end_symbol = ',.!?;:]}>)%~…，。！？；：】》）〉〗］〕”’～』」〞'
    line_width = chars_per_line * font.getlength("一")
    for i in origin.splitlines(False):
        if i == '':
            target += '\n'
            continue
        j = 0
        for ind, elem in enumerate(i):
            if i[j : ind + 1] == i[j:]:
                target += i[j : ind + 1] + '\n'
                continue
            elif font.getlength(i[j : ind + 1]) <= line_width:
                continue
            elif ind - j > 3:
                if i[ind] in end_symbol and i[ind - 1] != i[ind]:
                    target += i[j : ind + 1] + '\n'
                    j = ind + 1
                    continue
                elif i[ind] in start_symbol and i[ind - 1] != i[ind]:
                    target += i[j:ind] + '\n'
                    continue
            target += i[j:ind] + '\n'
            j = ind
    return target.rstrip()


@cpu_bound
def async_generate_img(*args, **kwargs):
    return generate_img(*args, **kwargs)


def generate_img(
        text_and_img: list = None,  # list[str | bytes] | list[str] | list[bytes] | None
        config: Text2ImgConfig = Text2ImgConfig(),
        img_path = os.path.join(BasicConfig().databaseUrl + 'temp_prts.jpg'),
        font_path_folder = BasicConfig().databaseUrl + 'fonts',
        img_type = None
) -> bytes:
    """
    根据输入的文本，生成一张图并返回图片文件的路径

    - 本地文件转 bytes 方法：BytesIO(open('1.jpg', 'rb').getvalue())
    - 网络文件转 bytes 方法：requests.get('http://localhost/1.jpg'.content)

    :param text_and_img: 要放到图里的文本（str）/图片（bytes）
    :return: 图片文件的路径
    """

    if text_and_img is None:
        raise ValueError('ArgumentError: 参数内容为空')
    elif not isinstance(text_and_img, list):
        raise ValueError('ArgumentError: 参数类型错误')

    if img_type == 'forcast':
        fontname = 'UbuntuMono-R.ttf' # 天气预报专用配置 - 等宽字体
        font_path = Path(root_path, font_path_folder, fontname)  # 字体文件的路径
        if not font_path.exists():
            raise ValueError(f'文本转图片所用的字体文件不存在，请检查配置文件，尝试访问的路径如下：↓\n{font_path}')
        if len(fontname) <= 4 or fontname[-4:] not in ('.ttf', '.ttc', '.otf', '.otc'):
            raise ValueError('所配置的字体文件名不正确，请检查配置文件')
        font_path = str(font_path)

        is_ttc_font = True if fontname.endswith('.ttc') or fontname.endswith('.otc') else False

    else:
        font_path = Path(root_path, font_path_folder, config.FontName)  # 字体文件的路径
        if not font_path.exists():
            raise ValueError(f'文本转图片所用的字体文件不存在，请检查配置文件，尝试访问的路径如下：↓\n{font_path}')
        if len(config.FontName) <= 4 or config.FontName[-4:] not in ('.ttf', '.ttc', '.otf', '.otc'):
            raise ValueError('所配置的字体文件名不正确，请检查配置文件')
        font_path = str(font_path)

        is_ttc_font = True if config.FontName.endswith('.ttc') or config.FontName.endswith('.otc') else False

    if is_ttc_font:
        font = ImageFont.truetype(font_path, size=config.FontSize, index=config.TTCIndex)  # 确定正文用的ttf字体
        extra_font = ImageFont.truetype(
            font_path, size=config.FontSize - int(0.3 * config.FontSize), index=config.TTCIndex
        )  # 确定而额外文本用的ttf字体
    else:
        # 确定正文用的ttf字体
        font = ImageFont.truetype(font_path, size=config.FontSize)
        # 确定而额外文本用的ttf字体
        extra_font = ImageFont.truetype(font_path, size=config.FontSize - int(0.3 * config.FontSize))

    extra_text1 = f'由 {basic_cfg.botName} 生成'  # 额外文本1
    extra_text2 = _get_time()  # 额外文本2

    line_width = int(config.CharsPerLine * font.getlength('一'))  # 行宽 = 每行全角宽度的字符数 * 一个字符框的宽度

    content_height = 0
    contents: list = []
    # contents = [{
    #     'content': str/Img.Image,
    #     'height': 区域高度
    # }]

    for i in text_and_img:
        if isinstance(i, str):
            text = cut_text(i.replace('{hr}', config.CharsPerLine * '—'), font, config.CharsPerLine)
            text_height = font.getsize_multiline(text, spacing=config.LineSpace)[1]
            contents.append({'content': text, 'height': text_height})
            content_height += text_height + config.LineSpace
            del text_height
        elif isinstance(i, bytes):
            img: Img.Image = Img.open(BytesIO(i))
            img_height = int(line_width / img.size[0] * img.size[1])
            img = img.resize((line_width, img_height), Img.LANCZOS)
            contents.append({'content': img, 'height': img_height})
            content_height += img_height + (2 * config.LineSpace)
            del img_height

    # 画布高度=(内容区域高度+(2*正文边距)+(边框上边距+4*边框厚度+2*内外框距离+边框下边距)
    bg_height = (
            content_height
            + (2 * config.TextMargin)
            + (config.BorderTopMargin + (4 * config.BorderOutlineWidth) + (2 * config.BorderInterval))
            + config.BorderBottomMargin
            + config.LineSpace
    )
    # 画布宽度=行宽+2*正文侧面边距+2*(边框侧面边距+(2*边框厚度)+内外框距离)
    bg_width = (
            line_width
            + (2 * config.TextMargin)
            + (2 * (config.BorderSideMargin + (2 * config.BorderOutlineWidth) + config.BorderInterval))
    )

    canvas = Img.new('RGB', (bg_width, bg_height), config.BackgroundColor)
    draw = ImageDraw.Draw(canvas)
    # 从这里开始绘图均为(x, y)坐标，横坐标x，纵坐标y
    # rectangle(起点坐标, 终点坐标) 绘制矩形，且方向必须为从左上到右下

    # 绘制外框
    # 外框左上点坐标 x=边框侧边距 y=边框上边距
    # 外框右下点坐标 x=画布宽度-边框侧边距 y=画布高度-边框上边距
    draw.rectangle(
        (
            (config.BorderSideMargin, config.BorderTopMargin),
            (bg_width - config.BorderSideMargin, bg_height - config.BorderBottomMargin),
        ),
        fill=None,
        outline=config.BorderOutlineColor,
        width=config.BorderOutlineWidth,
    )
    # 绘制内框
    # 内框左上点坐标 x=边框侧边距+外边框厚度+内外框距离 y=边框上边距+外边框厚度+内外框距离
    # 内框右下点坐标 x=画布宽度-边框侧边距-外边框厚度-内外框距离 y=画布高度-边框上边距-外边框厚度-内外框距离
    draw.rectangle(
        (
            (
                config.BorderSideMargin + config.BorderOutlineWidth + config.BorderInterval,
                config.BorderTopMargin + config.BorderOutlineWidth + config.BorderInterval,
            ),
            (
                bg_width - config.BorderSideMargin - config.BorderOutlineWidth - config.BorderInterval,
                bg_height - config.BorderBottomMargin - config.BorderOutlineWidth - config.BorderInterval,
            ),
        ),
        fill=None,
        outline=config.BorderOutlineColor,
        width=config.BorderOutlineWidth,
    )

    pil_compensation = config.BorderOutlineWidth - 1 if config.BorderOutlineWidth > 1 else 0

    # 绘制左上小方形
    # 左上点坐标 x=边框侧边距-边长-2*边框厚度+补偿 y=边框侧边距-边长-2*边框厚度+补偿 (补偿PIL绘图的错位)
    # 右下点坐标 x=边框侧边距+补偿 y=边框上边距+补偿
    draw.rectangle(
        (
            (
                config.BorderSideMargin
                - config.BorderSquareWrapWidth
                - (2 * config.BorderOutlineWidth)
                + pil_compensation,
                config.BorderTopMargin
                - config.BorderSquareWrapWidth
                - (2 * config.BorderOutlineWidth)
                + pil_compensation,
            ),
            (
                config.BorderSideMargin + pil_compensation,
                config.BorderTopMargin + pil_compensation,
            ),
        ),
        fill=None,
        outline=config.BorderOutlineColor,
        width=config.BorderOutlineWidth,
    )
    # 绘制右上小方形
    # 左上点坐标 x=画布宽度-(边框侧边距+补偿) y=边框侧边距-边长-2*边框厚度+补偿 (补偿PIL绘图的错位)
    # 右下点坐标 x=画布宽度-(边框侧边距-边长-2*边框厚度+补偿) y=边框上边距+补偿
    draw.rectangle(
        (
            (
                bg_width - config.BorderSideMargin - pil_compensation,
                config.BorderTopMargin
                - config.BorderSquareWrapWidth
                - (2 * config.BorderOutlineWidth)
                + pil_compensation,
            ),
            (
                bg_width
                - config.BorderSideMargin
                + config.BorderSquareWrapWidth
                + (2 * config.BorderOutlineWidth - pil_compensation),
                config.BorderTopMargin + pil_compensation,
            ),
        ),
        fill=None,
        outline=config.BorderOutlineColor,
        width=config.BorderOutlineWidth,
    )
    # 绘制左下小方形
    # 左上点坐标 x=边框侧边距-边长-2*边框厚度+补偿 y=画布高度-(边框下边距+补偿) (补偿PIL绘图的错位)
    # 右下点坐标 x=边框侧边距+补偿 y=画布高度-(边框侧边距-边长-2*边框厚度+补偿)
    draw.rectangle(
        (
            (
                config.BorderSideMargin
                - config.BorderSquareWrapWidth
                - (2 * config.BorderOutlineWidth)
                + pil_compensation,
                bg_height - config.BorderBottomMargin - pil_compensation,
            ),
            (
                config.BorderSideMargin + pil_compensation,
                bg_height
                - config.BorderBottomMargin
                + config.BorderSquareWrapWidth
                + (2 * config.BorderOutlineWidth)
                - pil_compensation,
            ),
        ),
        fill=None,
        outline=config.BorderOutlineColor,
        width=config.BorderOutlineWidth,
    )
    # 绘制右下小方形
    # 左上点坐标 x=画布宽度-(边框侧边距+补偿) y=画布高度-(边框下边距+补偿) (补偿PIL绘图的错位)
    # 右下点坐标 x=画布宽度-(边框侧边距-边长-2*边框厚度+补偿) y=画布高度-(边框侧边距-边长-2*边框厚度+补偿)
    draw.rectangle(
        (
            (
                bg_width - config.BorderSideMargin - pil_compensation,
                bg_height - config.BorderBottomMargin - pil_compensation,
            ),
            (
                bg_width
                - config.BorderSideMargin
                + config.BorderSquareWrapWidth
                + (2 * config.BorderOutlineWidth - pil_compensation),
                bg_height
                - config.BorderBottomMargin
                + config.BorderSquareWrapWidth
                + (2 * config.BorderOutlineWidth)
                - pil_compensation,
            ),
        ),
        fill=None,
        outline=config.BorderOutlineColor,
        width=config.BorderOutlineWidth,
    )

    # 绘制内容
    # 开始坐标:
    # x=边框侧边距+2*边框厚度+内外框距离+正文侧边距
    # y=边框上边距+2*边框厚度+内外框距离+正文上边距+行号*(行高+行距)
    content_area_x = (
            config.BorderSideMargin + (2 * config.BorderOutlineWidth) + config.BorderInterval + config.TextMargin
    )
    content_area_y = (
            config.BorderTopMargin + (2 * config.BorderOutlineWidth) + config.BorderInterval + config.TextMargin - 7
    )

    content_area_y += config.LineSpace

    for i in contents:
        if isinstance(i['content'], str):
            draw.text(
                (content_area_x, content_area_y),
                i['content'],
                fill=config.FontColor,
                font=font,
                spacing=config.LineSpace,
            )
            content_area_y += i['height'] + config.LineSpace
        elif isinstance(i['content'], Img.Image):
            canvas.paste(i['content'], (content_area_x, content_area_y + config.LineSpace))
            content_area_y += i['height'] + (2 * config.LineSpace)

    # 绘制第一行额外文字
    # 开始坐标 x=边框侧边距+(4*内外框距离) y=画布高度-边框下边距+(2*内外框距离)
    draw.text(
        (
            config.BorderSideMargin + (4 * config.BorderInterval),
            bg_height - config.BorderBottomMargin + (2 * config.BorderInterval),
        ),
        extra_text1,
        fill='#b4a08e',
        font=extra_font,
    )
    # 绘制第二行额外文字
    # 开始坐标 x=边框侧边距+(4*内外框距离) y=画布高度-边框下边距+(3*内外框距离)+第一行额外文字的高度
    draw.text(
        (
            config.BorderSideMargin + (4 * config.BorderInterval),
            bg_height - config.BorderBottomMargin + (3 * config.BorderInterval) + extra_font.getsize(extra_text1)[1],
        ),
        extra_text2,
        fill='#b4a08e',
        font=extra_font,
    )

    # canvas = canvas.convert(mode='RGB')  # 将RGBA转换为RGB
    # canvas.show()  # 展示生成结果

    byte_io = BytesIO()
    canvas.save(
        byte_io,
        format='JPEG',
        quality=90,
        optimize=True,
        progressive=True,
        subsampling=2,
        qtables='web_high',
    )


    ## 角落加入m3标志
    canvas.convert('RGBA')

    box = (

        bg_width - 225,
        config.BorderTopMargin + 4*config.BorderInterval,
        bg_width - 75,
        config.BorderTopMargin + 4*config.BorderInterval + 150
    )  # 底图上需要P掉的区域
    m3path = os.path.join('bot/database/faces/M3.png')
    tmp_img = Img.open(m3path) # 需要传的图片
    print(box, 4*config.BorderInterval)
    tmp_img = tmp_img.resize((150, 150))
    print(tmp_img.size)
    tmp_img = tmp_img.convert('RGBA')
    canvas.paste(tmp_img, box, tmp_img)


    # 保存为jpg图片 https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html?highlight=subsampling#jpeg
    # img_name = 'bot/database/temp_prts.jpg'  # 自定义临时文件的保存名称
    # img_path = os.path.join(img_name)  # 自定义临时文件保存路径
    print(img_path)
    canvas.save(
        img_path,
        format='JPEG',
        quality=90,
        optimize=True,
        progressive=True,
        subsampling=2,
        qtables='web_high'
    )

    # 保存为png图片 https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html?highlight=subsampling#png
    # img_name = 'temp_{}.png'.format(__get_time(2))  # 自定义临时文件的保存名称
    # img_path = os.path.join(temp_dir_path, img_name)  # 自定义临时文件保存路径
    # canvas.save(img_path, format='PNG', optimize=True)

    return byte_io.getvalue()



# claim_text = '''
# hi 博士你好，欢迎来到凯尔希的荣誉室。
# 当前(20220321)，凯尔希bot已完全依照mirai+mah+Graia-Ariadne+saya框架搭建，当前版本源码暂未开源。目前正经历一次项目重构，功能移植中，可能出现极不稳定的情况。若凯尔希出现不回应、突然疯狂回应之类的现象，或许是“技术性调整”，嗯，一定是。

# 目前已经完成重构可以使用的功能包括：
#  - 签到`#打卡`
#  - 4人小队组队`#22`
#  - 特殊文本触发彩蛋 `老女人`
#  - 夸夸`#praise`

# 凯尔希菜单请输入`#help`查看。欢迎有想法有爱的小伙伴一同开发凯尔希。

# 最后，新加群的小伙伴，凯尔希是可以拉群的，拉群前先与群主沟通即可。如果无法正常拉群，可能是功能还在调整。请勿禁言/踢出bot，违规群聊与个人将加入一份黑名单。

# '''


# generate_img([claim_text])