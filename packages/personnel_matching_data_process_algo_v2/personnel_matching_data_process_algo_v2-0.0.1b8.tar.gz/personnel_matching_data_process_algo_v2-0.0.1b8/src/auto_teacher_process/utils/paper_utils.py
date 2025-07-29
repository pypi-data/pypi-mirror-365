import difflib
import json
import re
from collections import defaultdict

import pandas as pd
from rapidfuzz import fuzz

from auto_teacher_process.utils.name_utils import segment_pinyin


def clean_text(text):
    """
    清洗文本：转换为大写，并去除多余符号，将其转为以空格分隔的单词。
    """
    # 转换为大写
    text = text.upper()

    # 使用正则表达式去掉多余的符号（保留字母和数字）
    text = re.sub(r"[^A-Z0-9\s]", " ", text)

    # 替换多个连续的空格为一个空格
    text = re.sub(r"\s+", " ", text)

    # 去除文本两端的空格
    text = text.strip()

    # 去掉介词和其他无关词
    # prepositions = ['OF', 'IN', 'ON', 'AT', 'FOR', 'BY', 'WITH', 'FROM', 'ABOUT', 'INTO', 'OVER',
    #                 'UNDER', 'BETWEEN', 'THROUGH', 'WITHOUT', 'WITHIN', 'THE', 'UNIVERSITY', 'UNIV', 'UNIVER',
    #                 'COLLEGE', 'TECH', 'TECHNOLOGY',"SCHOOL"]
    prepositions = [
        "OF",
        "IN",
        "ON",
        "AT",
        "FOR",
        "BY",
        "WITH",
        "FROM",
        "ABOUT",
        "INTO",
        "OVER",
        "UNDER",
        "BETWEEN",
        "THROUGH",
        "WITHOUT",
        "WITHIN",
        "THE",
        "COLLEGE",
        "SCHOOL",
    ]
    text_words = text.split()
    text = " ".join(word for word in text_words if word not in prepositions)
    text = " ".join([word for word in text.split() if not word.upper().startswith("UNIV")])

    return text


def clean_school_text(text):
    """
    清洗文本：转换为大写，并去除多余符号，将其转为以空格分隔的单词。
    """
    # 转换为大写
    text = text.upper()

    # 使用正则表达式去掉多余的符号（保留字母和数字）
    text = re.sub(r"[^A-Z0-9\s]", " ", text)

    # 替换多个连续的空格为一个空格
    text = re.sub(r"\s+", " ", text)

    # 去除文本两端的空格
    text = text.strip()

    # 去掉介词和其他无关词
    prepositions = [
        "OF",
        "IN",
        "ON",
        "AT",
        "FOR",
        "BY",
        "WITH",
        "FROM",
        "ABOUT",
        "INTO",
        "OVER",
        "UNDER",
        "BETWEEN",
        "THROUGH",
        "WITHOUT",
        "WITHIN",
        "THE",
    ]
    text_words = text.split()
    text = " ".join(word for word in text_words if word not in prepositions)

    return text


def extract_institutions(data):
    if not isinstance(data, str):
        data = str(data)
    pattern = r"\[(.*?)\]\s+(.*?)(?:;|$)"

    matches = re.findall(pattern, data)

    institutions = []
    for match in matches:
        institution = match[1].strip()
        institutions.append(institution)
    return institutions


def extract_authors_by_institution(data):
    # 正则表达式匹配机构和作者
    pattern = r"\[(.*?)\]\s+(.*?)(?:;|$)"

    matches = re.findall(pattern, data)

    # 使用字典保存每个机构及其对应的作者
    institution_authors = defaultdict(list)

    for match in matches:
        authors = match[0].split(";")
        institution = match[1].strip()

        for author in authors:
            # 去除首尾空格并添加到机构对应的作者列表中
            institution_authors[institution].append(author.strip())

    return institution_authors


def longest_common_prefix(str1, str2):
    """
    计算两个字符串的最长公共前缀
    """
    prefix = ""
    for char1, char2 in zip(str1, str2, strict=False):
        if char1 == char2:
            prefix += char1
        else:
            break
    return prefix


def find_best_match(target_school_list, candidates):
    best_matches = {}
    cleaned_target_schools = {school: clean_text(school) for school in target_school_list}
    for primary_part_ori, secondary_part_ori, ori_candidate in candidates:
        primary_part = clean_text(primary_part_ori)
        secondary_part = clean_text(secondary_part_ori)
        combined_part_ori = (primary_part + ", " + secondary_part).strip()
        primary_matched = False
        secondary_matched = False

        # Step 1
        for target_school in target_school_list:
            abb_name = ""
            if "(" in target_school and ")" in target_school:
                pattern = r"\((.*?)\)"
                matches = re.findall(pattern, target_school)
                if matches and all(match.isupper() for match in matches):
                    abb_name = matches[0]
            target_school_re = re.sub(r"\(.*?\)", "", target_school).strip()
            target_school_re = clean_school_text(target_school_re)
            if abb_name == "":
                abb_name = "".join([word[0] for word in target_school_re.split()])
            target_school_re = clean_text(target_school_re)
            target_school_words = target_school_re.split(" ")

            # Match primary and secondary part based on abbreviation
            if primary_part and abb_name in primary_part_ori.split(" "):
                if ori_candidate not in best_matches:
                    best_matches[ori_candidate] = target_school
                primary_matched = True
                break

            if not primary_matched and abb_name in secondary_part_ori.split(" "):
                if ori_candidate not in best_matches:
                    best_matches[ori_candidate] = target_school
                secondary_matched = True
                break

        if ori_candidate in best_matches:
            continue
        # Step 2
        if "univ" in ori_candidate.lower():  # 判断是否含有“univ”
            # 如果有，直接使用“univ”相关部分
            univ_parts = ori_candidate.split(",")
            univ_part = None
            for part in univ_parts:
                if "univ" in part.lower():
                    univ_part = part.strip()
                    break
            if univ_part:
                # 直接将univ相关部分进行匹配
                # print(f"Using univ part: {univ_part}")
                primary_part = clean_text(univ_part)
                secondary_part = ""  # 清空secondary_part，不再需要
                combined_part_ori = primary_part  # 不再使用逗号后部分

        sorted_target_schools = sorted(
            target_school_list,
            key=lambda school: max(
                fuzz.token_sort_ratio(primary_part, cleaned_target_schools[school]) / 100.0,
                fuzz.token_sort_ratio(secondary_part, cleaned_target_schools[school]) / 100.0,
            ),
            reverse=True,
        )

        # Now process with sorted schools
        for school in sorted_target_schools:
            primary_score = fuzz.token_sort_ratio(primary_part, cleaned_target_schools[school]) / 100.0
            secondary_score = fuzz.token_sort_ratio(secondary_part, cleaned_target_schools[school]) / 100.0
            max_score = max(primary_score, secondary_score)
            # print(
            #     f"candidate: {combined_part_ori}    School: {cleaned_target_schools[school]}    Score: {max_score:.2f}")

        primary_matched_else = False
        secondary_matched_else = False

        # Check for primary and secondary matches in the sorted schools
        for target_school in sorted_target_schools:
            if "(" in target_school and ")" in target_school:
                pattern = r"\((.*?)\)"
                matches = re.findall(pattern, target_school)
            target_school_re = re.sub(r"\(.*?\)", "", target_school).strip()
            target_school_re = clean_text(target_school_re)
            target_school_words = target_school_re.split()
            if primary_part:
                primary_words = primary_part.split(" ")
                exit_flg = False
                for primary_word in primary_words:
                    for target_word in target_school_words:
                        common_prefix = longest_common_prefix(target_word.upper(), primary_word.upper())
                        if len(common_prefix) >= 4:
                            if ori_candidate not in best_matches:
                                best_matches[ori_candidate] = target_school
                            primary_matched_else = True
                            exit_flg = True
                            break
                    if exit_flg:
                        break

            if not primary_matched_else and secondary_part:
                secondary_words = secondary_part.split(" ")
                exit_flg = False
                for secondary_word in secondary_words:
                    for target_word in target_school_words:
                        common_prefix = longest_common_prefix(target_word.upper(), secondary_word.upper())
                        if len(common_prefix) >= 4:
                            if ori_candidate not in best_matches:
                                best_matches[ori_candidate] = target_school
                            secondary_matched_else = True
                            exit_flg = True
                            break
                    if exit_flg:
                        break

            if primary_matched_else or secondary_matched_else:
                break

    return best_matches


def extract_and_match_institutions(address, affiliations):
    abb_author_list_dict = extract_authors_by_institution(address)

    target_schools_list = affiliations.split(";")
    target_schools_list = [school.strip() for school in target_schools_list]

    target_schools_list = [
        school
        for school in target_schools_list
        if school and school.split() and school.split()[-1].lower() != "system"
    ]
    target_schools_list = list(dict.fromkeys(target_schools_list))

    candidates_clean = []
    for inst in abb_author_list_dict:
        ori_inst = inst
        parts = inst.split(", ")  # 用逗号分隔候选学校
        primary_part = parts[0] if len(parts) > 0 else ""  # 第一部分
        secondary_part = parts[1] if len(parts) > 1 else ""  # 第二部分
        candidates_clean.append((primary_part, secondary_part, ori_inst))

    matches = find_best_match(target_schools_list, candidates_clean)

    return matches, abb_author_list_dict


def longest_common_substring(str1, str2):
    """
    计算两个字符串的最长公共子序列长度
    Args:
    str1: 第一个字符串
    str2: 第二个字符串
    Returns:
    最长公共子序列长度
    """
    seqMatch = difflib.SequenceMatcher(None, str1, str2)
    match = seqMatch.find_longest_match(0, len(str1), 0, len(str2))
    return match.size


def normalize_name(name: str) -> str:
    # 去除多余空格并格式化为首字母大写
    if "   " in name:
        name = name.replace("   ", "?").replace(" ", "").replace("?", " ")
        return name

    return name


def project_parse(project_str):
    if project_str is None or pd.isna(project_str):
        return []
    try:
        project_dict = json.loads(project_str)
        projects = project_dict["主持的项目"] + project_dict["参与的项目"]
        projects = [p[:100] for p in projects]
        return projects
    except:
        return []


def extract_corresponding_authors(text):
    # 首先将文本按分号分割，得到每个作者或单位的信息
    entries = text.split(".;")
    corresponding_authors = []
    # 匹配 (corresponding author) 之前的所有内容
    pattern = r"(.*?)(?= \(corresponding author\))"
    for entry in entries:
        if "(corresponding author)" in entry:
            authors = re.search(pattern, entry)
            corresponding_authors.extend(authors.group().split("; "))

    corresponding_authors = list(set(corresponding_authors))
    return corresponding_authors


def judge_reprint_author(author_name, author_list, reprint_addresses):
    try:
        match_author = get_reprint_author(author_list, reprint_addresses)
    except:
        match_author = set()
    return 1 if author_name in match_author else 0


def get_reprint_author(author_list, reprint_addresses):
    authors = author_list  # .split('; ')
    corresponding_authors = extract_corresponding_authors(reprint_addresses)
    match_author = []
    for author in authors:
        if ", " in author:
            if "." in author:
                names = author.split(", ")
                if len(names) == 2:
                    last_name, first_name = names[0], names[1]
                    if f"{last_name}, {first_name.replace('.', '').replace(' ', '')}" in corresponding_authors:
                        match_author.append(author)
                        continue
            names = author.split(", ")
            if len(names) == 2:
                last_name, first_name = names[0], names[1]
                format_author_name_1 = f"{last_name}, {segment_pinyin(first_name)}"
                format_author_name_2 = f"{first_name}, {segment_pinyin(last_name)}"
                if format_author_name_1 in corresponding_authors or format_author_name_2 in corresponding_authors:
                    match_author.append(author)
        elif len(author.split(" ")) == 2:
            names = author.split(" ")
            last_name, first_name = names[0], names[1]
            format_author_name = f"{last_name}, {segment_pinyin(first_name)}"
            if format_author_name in corresponding_authors:
                match_author.append(author)
        else:
            if author in corresponding_authors:
                match_author.append(author)

    return set(match_author)


def judge_affiliation_match(data, past_schools_en_list, teacher_name_variants):
    full_author_list = data["author_list"].split("; ")

    abb_full_school_name_dict, abb_author_list_dict = extract_and_match_institutions(
        data["addresses"], data["affiliations"]
    )
    # 遍历 abb_full_name_dict，判断是否有匹配的机构
    for abb_name, full_school_name in abb_full_school_name_dict.items():
        if full_school_name.lower() in past_schools_en_list:
            # 匹配到机构
            institution_author_list = abb_author_list_dict[abb_name]
            for author_name in institution_author_list:
                author_name = normalize_name(author_name)
                if author_name.lower() in teacher_name_variants:
                    is_corresponding_author = judge_reprint_author(
                        author_name=author_name,
                        author_list=full_author_list,
                        reprint_addresses=data["reprint_addresses"],
                    )
                    try:
                        author_order = full_author_list.index(author_name) + 1
                    except:
                        author_order = 0
                    return True, author_order, is_corresponding_author
    return False, 0, 0


#
# # 示例测试
# test = """[Garwood, W. St. John; Garwood, W. St. John, Jr.] Univ Texas, Sch Law, Austin, TX 78712 USA; [Garwood, W. St. John; Garwood, W. St. John, Jr.] Univ Texas Austin, Austin, TX 78712 USA"""
# target_schools = """University of Texas System; University of Texas Austin; University of Texas System; University of Texas Austin"""
# matches = extract_and_match_institutions(test, target_schools)
# print(matches)
# if __name__ == '__main__':
#     address = """[Garwood, W. St. John; Garwood, W. St. John, Jr.] Univ Texas, Sch Law, Austin, TX 78712 USA; [Garwood, W. St. John; Garwood, W. St. John, Jr.] Univ Texas Austin, Austin, TX 78712 USA"""
#     a = extract_authors_by_institution(address)
#     print(a)
