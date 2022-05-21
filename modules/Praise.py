#! /usr/bin/env python3
# coding:utf-8
import random
from os.path import basename

from core.decos import check_group, check_member, DisableModule
from core.ModuleRegister import Module
from database.kaltsitReply import blockList

from graia.ariadne.message.parser.twilight import RegexMatch
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Image, Plain
from graia.ariadne.message.parser.twilight import Twilight
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

adjective = [
  "ace",
  "adorable",
  "amazing",
  "astonishing",
  "astounding",
  "awe-inspiring",
  "awesome",
  "baboosh",
  "badass",
  "beautiful",
  "bedazzling",
  "best",
  "bravissimo",
  "breathtaking",
  "brightest",
  "brilliant",
  "charming",
  "clever",
  "chic",
  "classy",
  "clever",
  "cool",
  "crackin'",
  "cute",
  "dandy",
  "dazzling",
  "delicate",
  "delicious",
  "delightful",
  "distinctive",
  "divine",
  "dope",
  "elegant",
  "epic",
  "excellent",
  "exclusive",
  "exceptional",
  "exciting",
  "exquisite",
  "extraordinary",
  "fabulous",
  "fancy",
  "fantastic",
  "fantabulosus",
  "fantabulous",
  "fascinating",
  "fine",
  "finest",
  "first-class",
  "first-rate",
  "flawless",
  "formidable",
  "funkadelic",
  "geometric",
  "glorious",
  "gnarly",
  "good",
  "good-looking",
  "gorgeous",
  "grand",
  "great",
  "groovy",
  "groundbreaking",
  "hip",
  "hot",
  "hunky-dory",
  "impeccable",
  "impressive",
  "incredible",
  "irresistible",
  "just wow",
  "kickass",
  "kryptonian",
  "laudable",
  "legendary",
  "lovely",
  "luminous",
  "magnificent",
  "magnifique",
  "majestic",
  "marvelous",
  "mathematical",
  "metal",
  "mind-blowing",
  "miraculous",
  "nice",
  "neat",
  "nice",
  "outstanding",
  "particular",
  "peachy",
  "peculiar",
  "perfect",
  "phenomenal",
  "pioneering",
  "polished",
  "posh",
  "praiseworthy",
  "premium",
  "priceless",
  "prime",
  "primo",
  "proper",
  "rad",
  "radical",
  "remarkable",
  "riveting",
  "rockandroll",
  "rockin",
  "sensational",
  "sharp",
  "shining",
  "slick",
  "smart",
  "smashing",
  "solid",
  "special",
  "spectacular",
  "spiffing",
  "splendery-doodley",
  "splendid",
  "splendiferous",
  "stellar",
  "striking",
  "stonking",
  "stunning",
  "stupefying",
  "stupendous",
  "stylish",
  "sublime",
  "supah",
  "super",
  "super-duper",
  "super-excellent",
  "super-good",
  "superb",
  "superior",
  "supreme",
  "sweet",
  "sweetest",
  "swell",
  "terrific",
  "tiptop",
  "top-notch",
  "transcendent",
  "tremendous",
  "tubular",
  "ultimate",
  "unique",
  "unbelievable",
  "unreal",
  "well-made",
  "wicked",
  "wise",
  "wonderful",
  "wondrous",
  "world-class"
]


adverb_manner = [
  "beautifully",
  "bellissimo",
  "bigly",
  "bravely",
  "brightly",
  "calmly",
  "carefully",
  "cautiously",
  "cheerfully",
  "clearly",
  "correctly",
  "courageously",
  "daringly",
  "deliberately",
  "doubtfully",
  "eagerly",
  "easily",
  "effectively",
  "elegantly",
  "enormously",
  "enthusiastically",
  "faithfully",
  "fast",
  "fondly",
  "fortunately",
  "frankly",
  "frantically",
  "generously",
  "gently",
  "gladly",
  "gracefully",
  "happily",
  "healthily",
  "honestly",
  "joyously",
  "justly",
  "kindly",
  "neatly",
  "openly",
  "patiently",
  "perfectly",
  "politely",
  "powerfully",
  "quickly",
  "quietly",
  "rapidly",
  "really",
  "regularly",
  "repeatedly",
  "rightfully",
  "seriously",
  "sharply",
  "smoothly",
  "speedily",
  "successfully",
  "swiftly",
  "tenderly",
  "thoughtfully",
  "truthfully",
  "trustfully",
  "warmly",
  "well",
  "wisely"
]


# adverb = adverb_manner

# exclamation =[  
#   "ah",
#   "aha",
#   "ahh",
#   "ahhh",
#   "aw",
#   "aww",
#   "awww",
#   "amazeballs",
#   "aye",
#   "booyeah",
#   "cowabunga",
#   "gee",
#   "ha",
#   "hah",
#   "hmm",
#   "ho-ho",
#   "huh",
#   "heh",
#   "hooah",
#   "hooray",
#   "hurrah",
#   "hurray",
#   "huzzah",
#   "mhm",
#   "mm",
#   "mmh",
#   "mmhm",
#   "mmm",
#   "oh",
#   "ole",
#   "ooh",
#   "uh-hu",
#   "wee",
#   "whee",
#   "whoa",
#   "wow",
#   "wowie",
#   "yahoo",
#   "yay",
#   "yeah",
#   "yeahyah",
#   "yee-haw",
#   "yikes",
#   "yippie",
#   "yow",
#   "yowza"
# ]



# smiley =[
#   ":)",
#   ":D",
#   ":-D",
#   ";)",
#   "(-:",
#   "B-)"
# ]
  



# created = [
#   "assembled",
#   "brewed",
#   "built",
#   "created",
#   "composed",
#   "constructed",
#   "designed",
#   "devised",
#   "done",
#   "forged",
#   "formed",
#   "initiated",
#   "invented",
#   "made",
#   "organized",
#   "planned",
#   "prepared",
#   "set up",
#   "thrown together"
# ]

# creating = [
#   "assembling",
#   "brewing",
#   "building",
#   "creating",
#   "composing",
#   "constructing",
#   "designing",
#   "devising",
#   "forging",
#   "forming",
#   "initiating",
#   "inventing",
#   "making",
#   "organizing",
#   "planning",
#   "preparin",
#   "setting up"
# ]



channel = Channel.current()

module_name = basename(__file__)[:-3]

Module(
    name='Praise',
    file_name=module_name,
    author=['KOneLane'],
    usage='modules.Praise',
).register()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'#praise')])],
        decorators=[check_group(blockList.blockGroup), check_member(blockList.blockID), DisableModule.require(module_name)],
    )
)
async def Praise(
    app: Ariadne, 
    group: Group, 
    message: MessageChain,
    member: Member
):
    
    adv1 = random.sample(adverb_manner,1)[0]
    adjective1 = random.sample(adjective,1)[0]
    outtext = f"博士，你他喵真的{adv1} {adjective1}" + "!"
    
    

    await app.sendGroupMessage(group, MessageChain.create(
        Plain(outtext)
    ))



