from bot.property import PRIVILEGED_CMD
import re


def name_and_priviledget(words):
    name = " ".join(words[1:])
    privileged = True if re.compile(PRIVILEGED_CMD).match(words[0]) else False
    return name, privileged
