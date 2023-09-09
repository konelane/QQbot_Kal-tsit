import random


class StoryDice:
    """简单骰子"""

    @classmethod
    def dice_t(cls, text='1d6'):
        """1d6"""
        out = []
        num, side = text.split('d')
        if int(num) >= 100:
            num = 100
        if int(side) >= 1000:
            side = 1000
        for i in range(int(num)):
            out.append(random.randint(1, int(side)))
        return out

    @classmethod
    def dice_basic(cls, text_in):
        """@param
            text_in : "1d100 + 7"
        """
        if 'd' not in text_in:
            return [0], 0
        diff_dice = 0
        if '+' in text_in:
            text_dice = text_in.split('+')[0]
            diff_dice = int(text_in.split('d')[1].split('+')[1])
        elif '-' in text_in:
            text_dice = text_in.split('-')[0]
            diff_dice = int(text_in.split('d')[1].split('-')[1]) * -1
        else:
            text_dice = text_in.split()[0]

        return cls().dice_t(text_dice), diff_dice
