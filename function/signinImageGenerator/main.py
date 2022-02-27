"""

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from io import BytesIO
from os.path import dirname, join
from typing import Optional, Union
from uuid import UUID, uuid4

# import httpx
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from util import Ink, Reward, cut_text, exp_bar, get_qlogo, get_time
import argparse


placeholder = "占位符+123"  # 用于获取字符高度


def get_signin_img(
    qq: int,
    name: str,
    uuid: Optional[Union[UUID, str]],
    level: int,
    exp,#: tuple[int, int],
    total_days: int,
    consecutive_days: int,
    is_signin_consecutively: bool,
    rewards,#: list[Reward],
    font_path: str,
    text_color: Ink = "white",
    exp_bar_fg_color: Ink = "#FE9A2E",
    exp_bar_bg_color: Ink = "#00000055",
) -> bytes:
    """生成一张签到打卡图，应该算 CPU 密集型任务，因此 httpx 并没有使用 asyncio 如有需要可自行魔改
    Args:
        qq (int): QQ号
        name (str): 群名片
        uuid (Union[UUID, str]): 用户唯一标识
        level (int): 好感等级
        exp (tuple[int, int]): 好感经验值，请使用 (当前经验值, 总所需经验值) 的格式传入
        total_days (int): 累计签到天数
        consecutive_days (int): 连续签到天数
        is_signin_consecutively (bool): 是否连续签到
        rewards (list[Reward]): 签到奖励
        font_path (str): 字体路径
        text_color (_In): 文字颜色
        exp_bar_fg_color (_Ink): 经验条前景色
        exp_bar_bg_color (_Ink): 经验条背景色
    Returns:
        bytes: 生成结果的图片二进制数据
    """
    size = (1920, 1080)
    avatar_size = 384
    avatar_xy = int(size[1] * 0.15)

    canvas = Image.new("RGB", size, "#FFFFFF")
    draw = ImageDraw.Draw(canvas)

    qlogo = Image.open(BytesIO(get_qlogo(id=qq)))
    # qlogo = Image.open('3.jpg')

    # 背景
    if size[1] > size[0]:
        qlogo1 = qlogo.resize((size[1], size[1]), Image.LANCZOS).filter(ImageFilter.GaussianBlur(radius=50))
        canvas.paste(qlogo1, ((size[0] - size[1]) // 2, 0))
    else:
        qlogo1 = qlogo.resize((size[0], size[0]), Image.LANCZOS).filter(ImageFilter.GaussianBlur(radius=50))
        canvas.paste(qlogo1, (0, (size[1] - size[0]) // 2))

    # 背景加一层黑
    mask = Image.new("RGBA", size, "#00000055")
    canvas.paste(mask, (0, 0), mask.split()[3])

    # 魔法阵
    mahojin_size_offset = 55  # 魔法阵比头像大多少（半径）
    mahojin_size = avatar_size + 2 * mahojin_size_offset
    mahojin = Image.open(join(dirname(__file__), "imgs", "mahojin.png"))
    mahojin = mahojin.resize((mahojin_size, mahojin_size), Image.LANCZOS)
    canvas.paste(mahojin, (avatar_xy - mahojin_size_offset, avatar_xy - mahojin_size_offset), mask=mahojin.split()[3])

    # 头像描边
    stroke_width = 5  # 描边厚度
    stroke = Image.new(
        "RGBA", ((avatar_size + 2 * stroke_width) * 4, (avatar_size + 2 * stroke_width) * 4), "#00000000"
    )
    stroke_draw = ImageDraw.Draw(stroke)
    stroke_draw.ellipse(
        (0, 0, (avatar_size + 2 * stroke_width) * 4, (avatar_size + 2 * stroke_width) * 4), fill="#000000bb"
    )
    stroke = stroke.resize((avatar_size + 2 * stroke_width, avatar_size + 2 * stroke_width), Image.LANCZOS)
    canvas.paste(stroke, (avatar_xy - stroke_width, avatar_xy - stroke_width), mask=stroke.split()[3])

    # 圆形头像蒙版
    avatar_mask = Image.new("RGBA", (avatar_size * 4, avatar_size * 4), "#00000000")
    avatar_mask_draw = ImageDraw.Draw(avatar_mask)
    avatar_mask_draw.ellipse((0, 0, avatar_size * 4, avatar_size * 4), fill="#000000ff")
    avatar_mask = avatar_mask.resize((avatar_size, avatar_size), Image.LANCZOS)

    # 圆形头像
    qlogo2 = qlogo.resize((avatar_size, avatar_size), Image.LANCZOS)
    canvas.paste(qlogo2, (avatar_xy, avatar_xy), avatar_mask)

    font_1 = ImageFont.truetype(font_path, size=60)
    font_2 = ImageFont.truetype(font_path, size=35)
    font_3 = ImageFont.truetype(font_path, size=45)
    qq_text = f"QQ：{qq}"
    uid = f"uid：{uuid}"
    impression = f"信赖值：Lv{level}  {exp[0]} / {exp[1]}"

    y = avatar_xy + 25

    draw.text((2 * avatar_xy + avatar_size, y), name, font=font_1, fill=text_color)
    y += font_1.getsize(name)[1] + 50
    draw.text((2 * avatar_xy + avatar_size, y), qq_text, font=font_2, fill=text_color)
    y += font_2.getsize(qq_text)[1] + 30
    if uid is not None:
        draw.text((2 * avatar_xy + avatar_size, y), uid, font=font_2, fill=text_color)
        y += font_2.getsize(uid)[1] + 30
    draw.text((2 * avatar_xy + avatar_size, y), impression, font=font_2, fill=text_color)
    bar = exp_bar(font_2.getsize(impression)[0], 6, exp[0] / exp[1], fg=exp_bar_fg_color, bg=exp_bar_bg_color)
    canvas.paste(bar, (2 * avatar_xy + avatar_size, y + font_2.getsize(impression)[1] + 10), mask=bar.split()[3])

    y = avatar_xy + avatar_size + 100
    draw.text((avatar_xy + 30, y), f"共签到 {total_days} 天", font=font_3, fill=text_color)

    if is_signin_consecutively:
        y += font_3.getsize(placeholder)[1] + 20
        draw.text((avatar_xy + 30, y), f"连续签到 {consecutive_days} 天", font=font_3, fill=text_color)
        y += font_3.getsize(placeholder)[1] + 30
    else:
        y += font_3.getsize(placeholder)[1] + 30

    for reward in rewards:
        x_offset = avatar_xy + 30
        if reward.ico is not None:
            ico = Image.open(reward.ico).convert("RGBA")
            ico = ico.resize((font_2.getsize(placeholder)[1], font_2.getsize(placeholder)[1]), Image.LANCZOS)
            canvas.paste(ico, (x_offset, y + 5), mask=ico.split()[3])
            x_offset = x_offset + 20 + ico.size[0]
        if reward.name is not None:
            draw.text((x_offset, y), f"{reward.name} +{reward.num}", font=font_2, fill=text_color)
        else:
            draw.text((x_offset, y), f"+{reward.num}", font=font_2, fill=text_color)
        y += font_2.getsize(placeholder)[1] + 30

    # 一言背景
    hitokoto_bg = Image.new("RGBA", (1045, 390), "#00000000")
    hitokoto_bg_draw = ImageDraw.Draw(hitokoto_bg)
    hitokoto_bg_draw.rounded_rectangle((0, 0, 1045, 390), 20, fill="#00000030")
    hitokoto_bg = hitokoto_bg.resize((1045, 390), Image.LANCZOS)
    canvas.paste(hitokoto_bg, (2 * avatar_xy + avatar_size, avatar_xy + avatar_size + 55), mask=hitokoto_bg.split()[3])

    # 获取一言
    try:
        # hotokoto = requests.get("https://v1.jinrishici.com/?encode=text&charset=utf-8&max_length=100").text
        hotokoto = requests.get("https://v1.jinrishici.com/rensheng.txt")
    except Exception as e:
        hotokoto = "今天的学习资料获取失败"
        print(e)
    else:
        hotokoto = '一句炎国诗词：\n\n' + hotokoto.text
    # hotokoto = '''由于一言目前属于公益性运营，为了保证资源的公平利用和不过度消耗公益资金，我们会定期的屏蔽某些大流量的站点。若您的站点的流量较大，您需要提前联系我们获得授权后再开始使用。对于超过阈值的站点，我们有可'''
    font_4 = ImageFont.truetype(font_path, size=45)
    draw.text(
        (2 * avatar_xy + avatar_size + 50, avatar_xy + avatar_size + 100),
        cut_text(font_4, hotokoto, 21),
        font=font_4,
        fill=text_color,
        spacing=10,
    )  # 最大不要超过5行

    # footer
    font_5 = ImageFont.truetype(font_path, size=15)
    draw.text((15, size[1] - 55), f"Kal'tsit Bot ©2022\n{get_time()}", font=font_5, fill="#cccccc")

    # canvas.show()  # 直接展示生成结果（保存为临时文件）

    canvas.convert("RGB")
    byte_io = BytesIO()
    canvas.save(
        byte_io,
        format="JPEG",
        quality=90,
        optimize=True,
        progressive=True,
        subsampling=2,
        qtables="web_high",
    )
    return byte_io.getvalue()


if __name__ == "__main__":
    font_path = join(dirname(__file__), "fonts", "OPPOSans-B.ttf")

    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument("--id", type=int, default=591016144)
    parser.add_argument("--signin_uid", type=str, default='test_uuid')
    parser.add_argument("--name", type=str, default='凯尔希测试')
    parser.add_argument("--exp", type=int, default=0)
    parser.add_argument("--total_days", type=int, default=0)
    parser.add_argument("--consecutive_days", type=int, default=0)
    parser.add_argument("--is_signin_consecutively", type=int, default=0)
    parser.add_argument("--reliance", type=int, default=0)
    parser.add_argument("--credit", type=int, default=0)
    parser.add_argument("--last_signin_time", type=str, default="2022/02/26-00:00:00")

    args = parser.parse_args()
    

    # 假设触发了签到事件，获得了用户的QQ号、群名片
    qq = args.id
    name = args.name

    # 先从数据库中查询签到总天数、连续签到天数、上次签到时间、签到经验值
    # 此次假设以下值为从数据库中查询得到
    total_days = args.total_days
    consecutive_days = args.consecutive_days
    last_signin_time = time.time() - 86390  # 该值仅用于测试
    exp = (args.exp, 200)
    
    is_signin_consecutively = True if args.is_signin_consecutively == 1 else False
    img_bytes = get_signin_img(
        qq=qq,
        name=name,
        uuid=uuid4(),
        level=1,
        exp=exp,
        total_days=total_days,
        consecutive_days=consecutive_days,
        is_signin_consecutively=is_signin_consecutively,
        rewards=[
            Reward(num=args.reliance, ico=join(dirname(__file__), "imgs", "xinlai.png")),
            Reward(name="信用", num=args.credit, ico=join(dirname(__file__), "imgs", "credit.png")),
        ],
        font_path=font_path,
    )
    # print(img_bytes)
    save_dir = dirname(__file__) + '/save_test.png'
    print(save_dir)
    with open(save_dir,'wb') as f:
        f.write(img_bytes)
        f.flush()
        f.close()

    print('图片保存完毕')