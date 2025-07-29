import re

from auto_teacher_process.utils.text_utils import contains_chinese
from auto_teacher_process.utils.paper_utils import extract_authors_by_institution


def find_names_numbers(input_str):
    end = -1
    for idx, char in enumerate(reversed(input_str)):  # 从后往前遍历字符串
        if char.isdigit() or char == ",":
            continue
        end = idx
        break
    num_list = []
    for num in input_str[-end:].split(","):
        try:
            num_list.append(int(num))
        except:
            # print("XXXXX: ", input_str)
            continue
    # num_list = [int(num) for num in input_str[-end:].split(',')]
    return input_str[:-end], num_list


def parse_unit_names(names, affiliations):
    """
    将姓名和机构解析为以机构为键，教师姓名列表为值的字典列表。
    Args:
        names (str): 姓名信息字符串，支持多个姓名用换行或逗号分隔。
        affiliations (str): 机构信息字符串，支持多个机构用换行分隔。
    Returns:
        list[dict]: 以机构为键，教师姓名列表为值的字典列表。
    """
    # 拆分姓名和机构
    name_list = [name.strip() for name in names.split("\n") if name.strip()]
    aff_list = [re.sub(r"^\d+\.", "", aff.strip()) for aff in affiliations.split("\n") if aff.strip()]

    # 处理多对多关系
    result = {}
    for name in name_list:
        # 检查姓名后是否有序号
        if name[-1].isdigit():
            name_base, indices = find_names_numbers(name)
        else:
            name_base = name
            indices = list(range(1, len(aff_list) + 1))  # 默认全匹配

        # 根据序号将姓名分配到对应机构
        for idx in indices:
            if idx <= len(aff_list):  # 确保索引合法
                if aff_list[idx - 1] not in result:
                    result[aff_list[idx - 1]] = []
                if "," in name_base:
                    result[aff_list[idx - 1]] += name_base.split(",")
                else:
                    result[aff_list[idx - 1]].append(name_base)

    for key, value in result.items():
        result[key] = list(set(value))
    return result


def contain_digits(s):
    return any(char.isdigit() for char in s)


def get_author_order(name, authors):
    if "," in authors and not contain_digits(authors):
        author_list = authors.split(",")
        try:
            order = author_list.index(name) + 1
        except:
            order = -1
        return order
    authors = authors.split("\n")
    for idx, author in enumerate(authors):
        if name in author:
            return idx + 1
    return -1


def judge_cn_paper_affiliation_match(full_author_list, addresses, teacher_school_name, teacher_name_variants):
    unit_names = extract_authors_by_institution(addresses)

    for affiliation, author_names_list in unit_names.items():
        if teacher_school_name not in affiliation:
            continue

        for paper_author_name in author_names_list:
            if paper_author_name.lower() in teacher_name_variants:
                try:
                    author_order = full_author_list.index(paper_author_name) + 1
                except:
                    author_order = 0
                return True, author_order

    return False, -1
