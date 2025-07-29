import re
import unicodedata

import pandas as pd
from langdetect import LangDetectException, detect

# 省份代码映射表
PROVINCE_CODE_DICT = {
    "北京市": 11,
    "天津市": 12,
    "河北省": 13,
    "山西省": 14,
    "内蒙古自治区": 15,
    "辽宁省": 21,
    "吉林省": 22,
    "黑龙江省": 23,
    "上海市": 31,
    "江苏省": 32,
    "浙江省": 33,
    "安徽省": 34,
    "福建省": 35,
    "江西省": 36,
    "山东省": 37,
    "河南省": 41,
    "湖北省": 42,
    "湖南省": 43,
    "广东省": 44,
    "广西壮族自治区": 45,
    "海南省": 46,
    "重庆市": 50,
    "四川省": 51,
    "贵州省": 52,
    "云南省": 53,
    "西藏自治区": 54,
    "陕西省": 61,
    "甘肃省": 62,
    "青海省": 63,
    "宁夏回族自治区": 64,
    "新疆维吾尔自治区": 65,
}


def detect_language_zh(text):
    try:
        lang = detect(text)
    except LangDetectException:
        # 处理无法检测的情况
        return False

    if lang == "zh-cn" or lang == "zh-tw":  # 中文简体或繁体
        return True
    return False


# 字符比例
def is_chinese_char(char):
    """判断字符是否为中文"""
    return "\u4e00" <= char <= "\u9fff" or char.isdigit()


def is_english_char(char):
    """判断字符是否为英文字符"""
    return char.isalpha() and ("a" <= char.lower() <= "z")


def detect_language_ratio(text, threshold=0.1):
    chinese_count = 0
    english_count = 0
    total_count = 0

    # 统计中文和英文字符的数量
    for char in text:
        if is_chinese_char(char):
            chinese_count += 1
            total_count += 1
        elif is_english_char(char):
            english_count += 1
            total_count += 1

    # 如果文本没有中文或英文字符
    if total_count == 0:
        return 0

    # 计算中文和英文字符的比例
    chinese_ratio = chinese_count / total_count

    # 如果中文比例大于阈值（即中文为主，忽略部分英文）
    if chinese_ratio > threshold:
        return 0
    return 1


# 关键字检测
def contains_keywords(text, keywords):
    """检查文本中是否包含指定关键词"""
    for keyword in keywords:
        if keyword in text:
            return True
    return False


# 中文自我介绍的常见关键词
chinese_keywords = [
    "论文",
    "发表",
    "讲师",
    "博士",
    "研究",
    "学术",
    "科研",
    "教授",
    "导师",
    "科学家",
    "研究生",
    "学位",
    "项目",
    "专利",
    "奖项",
    "医生",
    "擅长",
]


def judge_en(description: str):
    clean_text = description.replace("\n", "")
    text = clean_text[:100]
    if detect_language_zh(text):
        return 0

    # 无法确认中英文，再用其他方法判断
    if detect_language_ratio(text) == 0:
        return 0
    return 1


def contains_chinese(s):
    if not isinstance(s, str):
        return True
    return bool(re.search(r"[\u4e00-\u9fff]+", s))


def normalize_title(self, title):
    """去掉所有空格、重音符号，并规范化 Unicode 字符"""
    if pd.isna(title):  # 处理空值
        return ""

    title = title.strip().lower()  # 去掉首尾空格，并转换为小写

    # 统一各种破折号和连字符
    title = title.replace("–", "-").replace("—", "-").replace("‐", "-")
    title = title.replace(":", "")

    # 统一空格（包括全角空格）
    title = re.sub(r"\s+", "", title)  # 去掉所有空格
    title = unicodedata.normalize("NFKC", title)  # 归一化 Unicode

    # 去除重音符号
    normalized_str = unicodedata.normalize("NFD", title)
    title = "".join(c for c in normalized_str if unicodedata.category(c) != "Mn")
    title = title.lower()
    return title
