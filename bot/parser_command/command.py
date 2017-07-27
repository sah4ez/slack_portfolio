import property
import re


def name_and_priviledget(words):
    name = " ".join(words[1:])
    privileged = True if re.compile(property.PRIVILEGED_CMD).match(words[0]) else False
    return name, privileged
