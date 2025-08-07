# -*- coding: utf-8 -*-
# @Time    : 2025/8/7 12:29
# @Author  : JustKidding
# @Email   : superjustkidding@gmail.com
# @File    : enum.py
# @Software: PyCharm
"""
枚举
"""
import enum
from contextvars import ContextVar

if hasattr(enum, "EnumType"):
    from enum import EnumType

    EnumType._check_for_existing_members_ = lambda _, __: _


class EnumMem:
    """
    枚举成员类
    """

    def __init__(self, value, desc):
        """
        :param value: 枚举值
        :param desc: 枚举值的描述
        """
        self.value = value
        self.desc = desc


class EnumMeta:
    @classmethod
    def __enum__(cls, *args):
        mem = args[0]
        __enum_dict__ = getattr(cls, "__enum_dict__", {})

        if isinstance(mem, EnumMem):
            __enum_dict__[mem.value] = mem.desc
            value = mem.value
        else:
            value = mem
        cls.__enum_dict__ = __enum_dict__
        return value

    def __str__(self):
        return str(self._value_)

    @classmethod
    def values(cls):
        """
        所有枚举值
        :return: 所有枚举值
        """
        return getattr(cls, "__enum_dict__").keys()

    @classmethod
    def dict(cls):
        """
        所有枚举值, 以及说明
        :return: 枚举值－说明
        """
        return getattr(cls, "__enum_dict__")

    @classmethod
    def desc(cls, member, default=None):
        """
        获取对某个值的描述
        :param value: 枚举值
        :return: 说明
        """
        import i18n

        enum_dict = cls.dict()
        value = enum_dict.get(member, default)
        if value is None:
            return member
        data = ContextVar("data", default={}).get()
        lan = data.get("lan", "en-us") or "en-us"
        if isinstance(value, (list, tuple)):
            index = 0 if lan == "zh-cn" else 1
            return value[index]
        return i18n.t(value, locale=lan.split("-")[0])


class IntEnum(EnumMeta, int, enum.Enum):
    """
    枚举类
    """

    def __new__(cls, *args):
        value = cls.__enum__(*args)
        member = int.__new__(cls, value)
        member._value_ = value
        return member


class FloatEnum(EnumMeta, float, enum.Enum):
    """
    枚举类
    """

    def __new__(cls, *args):
        value = cls.__enum__(*args)
        member = float.__new__(cls, value)
        member._value_ = value
        return member


class StrEnum(EnumMeta, str, enum.Enum):
    def __new__(cls, *args):
        value = cls.__enum__(*args)
        member = str.__new__(cls, value)
        member._value_ = value
        return member


Enum = IntEnum

if __name__ == "__main__":
    class Test(Enum):
        """
        使用EnumMem值的枚举
        """
        TOP = EnumMem(1, "顶部")
        MID = EnumMem(2, "中部")
