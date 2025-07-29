import json
import re
import string

import pandas as pd

from auto_teacher_process.config import Config

province_code_dict = Config.DB_CONFIG.TEACHER_LEVEL.PORVINCE_CODE_DICT
famous_projects_level_scores = Config.DB_CONFIG.TEACHER_LEVEL.FAMOUS_PROJECTS_LEVEL_SCORES
famous_titles_level_scores = Config.DB_CONFIG.TEACHER_LEVEL.FAMOUS_TITLES_LEVEL_SCORES
titles_level_scores = Config.DB_CONFIG.TEACHER_LEVEL.TITLES_LEVEL_SCORES


def _remove_punctuation(text):
    """清除中英文标点符号"""
    punctuation = string.punctuation + "“”‘’？【】（）《》()/"
    text = re.sub(rf"[{punctuation}]+", "", text)
    return text


def _project_famous_check(projects):
    """检测国家级重要科研项目"""

    def find_match_positions(data, keyword):
        start_idx = data.find(keyword)
        if start_idx != -1:
            return (start_idx, start_idx + len(keyword))
        return None

    matched_projects = []

    for data in projects:
        temp_matches = []  # Temporary list to store matches with their positions
        # print(data)
        if data is None:
            continue  # Skip None values in the projects list
        if data is not None:
            # 如果 data 不是字符串，则转换为字符串
            data = str(data)
            # 去除空格并清除标点符号
            data = _remove_punctuation(data.replace(" ", ""))
            # Check for 国家重点研发
            if "国家重点研发" in data:
                found_match = False
                for keyword in ["项目", "子课题", "课题", "子专题", "专题", "项目骨干"]:
                    pos = find_match_positions(data, keyword)
                    if pos:
                        temp_matches.append((f"国家重点研发-{keyword}", pos))
                        found_match = True
                if found_match == False:
                    temp_matches.append(("国家重点研发", (-1, -1)))

            # Check for 973项目
            if "973项目" in data:
                found_match = False
                for keyword in ["首席科学家", "首席科学家助理", "子课题", "子专题", "课题", "专题"]:
                    pos = find_match_positions(data, keyword)
                    if pos:
                        temp_matches.append(("973项目-" + keyword, pos))
                        found_match = True
                if found_match == False:
                    temp_matches.append(("973项目", (-1, -1)))

            # Check for 973计划
            if "973计划" in data:
                found_match = False
                for keyword in ["首席科学家", "首席科学家助理", "子课题", "子专题", "课题", "专题"]:
                    pos = find_match_positions(data, keyword)
                    if pos:
                        temp_matches.append(("973计划-" + keyword, pos))
                        found_match = True
                if found_match == False:
                    temp_matches.append(("973计划", (-1, -1)))

            # Check for 863项目
            if "863项目" in data:
                found_match = False
                for keyword in ["子课题", "子专题"]:
                    pos = find_match_positions(data, keyword)
                    if pos:
                        temp_matches.append(("863项目-" + keyword, pos))
                        found_match = True
                if found_match == False:
                    temp_matches.append(("863项目", (-1, -1)))

            # Check for 863计划
            if "863计划" in data:
                found_match = False
                for keyword in ["子课题", "子专题"]:
                    pos = find_match_positions(data, keyword)
                    if pos:
                        temp_matches.append(("863计划-" + keyword, pos))
                        found_match = True
                if found_match == False:
                    temp_matches.append(("863计划", (-1, -1)))

            # Check for 国家科技重大专项
            if "国家科技重大专项" in data or "国家重大科技专项" in data:
                found_match = False
                for keyword in ["项目", "课题", "专题", "子课题", "子专题"]:
                    pos = find_match_positions(data, keyword)
                    if pos:
                        temp_matches.append(("国家科技重大专项-" + keyword, pos))
                        found_match = True
                if found_match == False:
                    temp_matches.append(("国家科技重大专项", (-1, -1)))

            # Check for 国家科技支撑
            if "国家科技支撑" in data:
                found_match = False
                for keyword in ["项目", "专题", "课题", "子专题", "子课题"]:
                    pos = find_match_positions(data, keyword)
                    if pos:
                        temp_matches.append(("国家科技支撑-" + keyword, pos))
                        found_match = True
                if found_match == False:
                    temp_matches.append(("国家科技支撑", (-1, -1)))

            # Check for 国家自然科学基金重大
            if "国家自然科学基金重大" in data:
                found_match = False
                for keyword in ["课题", "项目", "子课题", "子专题"]:
                    pos = find_match_positions(data, keyword)
                    if pos:
                        temp_matches.append(("国家自然科学基金重大-" + keyword, pos))
                        found_match = True
                if found_match == False:
                    temp_matches.append(("国家自然科学基金重大", (-1, -1)))
            if "国家自然基金重大" in data:
                found_match = False
                for keyword in ["课题", "项目", "子课题", "子专题"]:
                    pos = find_match_positions(data, keyword)
                    if pos:
                        temp_matches.append(("国家自然科学基金重大-" + keyword, pos))
                        found_match = True
                if found_match == False:
                    temp_matches.append(("国家自然科学基金重大", (-1, -1)))
            # Check for 国家自然科学基金重点
            if "国家自然科学基金重点" in data:
                found_match = False
                for keyword in ["课题", "项目", "子课题", "子专题"]:
                    pos = find_match_positions(data, keyword)
                    # print(pos)
                    if pos:
                        temp_matches.append(("国家自然科学基金重点-" + keyword, pos))
                        found_match = True
                # print(found_match)
                if found_match == False:
                    temp_matches.append(("国家自然科学基金重点", (-1, -1)))
            if "国家自然基金重点" in data:
                found_match = False
                for keyword in ["课题", "项目", "子课题", "子专题"]:
                    pos = find_match_positions(data, keyword)
                    # print(pos)
                    if pos:
                        temp_matches.append(("国家自然科学基金重点-" + keyword, pos))
                        found_match = True
                # print(found_match)
                if found_match == False:
                    temp_matches.append(("国家自然科学基金重点", (-1, -1)))

            # Check for 国家自然科学基金面上项目
            if "国家自然科学基金面上项目" in data:
                temp_matches.append(("国家自然科学基金面上项目", (-1, -1)))
            if "国家自然科学基金面上" in data:
                temp_matches.append(("国家自然科学基金面上项目", (-1, -1)))
            if "国家自然基金面上" in data:
                temp_matches.append(("国家自然科学基金面上项目", (-1, -1)))
            if "国家自然科学基金" in data:
                temp_matches.append(("国家自然基金", (-1, -1)))
            if "国家自然基金" in data:
                temp_matches.append(("国家自然基金", (-1, -1)))
            # Check for 国家自然科学基金青年项目
            if "国家自然科学基金青年项目" in data:
                temp_matches.append(("国家自然科学基金青年项目", (-1, -1)))
            if "国家自然科学基金青年" in data:
                temp_matches.append(("国家自然科学基金青年项目", (-1, -1)))
            if "国家自然科学青年基金" in data:
                temp_matches.append(("国家自然科学基金青年项目", (-1, -1)))
            if "国家自然科学青年" in data:
                temp_matches.append(("国家自然科学基金青年项目", (-1, -1)))
            if "国家自然基金青年" in data:
                temp_matches.append(("国家自然科学基金青年项目", (-1, -1)))

            # print(temp_matches)
            # Remove substring matches
            for i, (title_i, (start_i, end_i)) in enumerate(temp_matches):
                is_substring = False
                for j, (title_j, (start_j, end_j)) in enumerate(temp_matches):
                    if i != j:
                        # 处理“课题”和“子课题”
                        if "课题" in title_i and "子课题" in title_j:
                            if start_i > start_j and end_i == end_j:
                                is_substring = True
                                break
                        # 处理“专题”和“子专题”
                        elif "专题" in title_i and "子专题" in title_j:
                            # 确保"子专题"不是“子课题”的一部分
                            if start_i > start_j and end_i == end_j and "课题" not in title_i:
                                is_substring = True
                                break
                        # 处理“项目”和“项目骨干”
                        elif "项目" in title_i and "项目骨干" in title_j:
                            if start_i == start_j and end_i < end_j:
                                is_substring = True
                                break
                if not is_substring:
                    matched_projects.append(title_i)
            if "省" in data and ("项目" in data or "计划" in data or "基金" in data or "课题" in data):
                matched_projects.append("省级项目")
            # 提取市级项目
            if "市" in data and ("项目" in data or "计划" in data or "基金" in data or "课题" in data):
                matched_projects.append("市级项目")
            if ("省" not in data and "市" not in data and "国家" not in data) and (
                "项目" in data or "计划" in data or "基金" in data or "课题" in data
            ):
                matched_projects.append("其他项目")

    return list(set(matched_projects))


def _quchong(matched_projects):
    """去重处理，优先保留更具体的项目类型"""
    matched_projects = list(set(matched_projects))
    to_remove = []

    if "国家自然基金" in matched_projects:
        for match in matched_projects:
            if match != "国家自然基金" and all(kw in match for kw in ["国家", "自然", "基金"]):
                to_remove.append("国家自然基金")
                break

    return [m for m in matched_projects if m not in to_remove]


def calculate_famous_projects_level(projects: list) -> int:
    """计算项目等级评分"""
    if not projects:
        return 0

    max_score = 10  # 默认评分
    for project in projects:
        for score_str, title_group in famous_projects_level_scores.items():
            if project in title_group:
                max_score = max(max_score, int(score_str))
                break
    return max_score


def calculate_famous_titles_level(famous_titles: list) -> int:
    """计算帽子等级评分"""
    if not famous_titles:
        return 0

    max_score = 40  # 默认评分
    for title in famous_titles:
        for score_str, title_group in famous_titles_level_scores.items():
            if title in title_group:
                max_score = max(max_score, int(score_str))
                break
    return max_score


def calculate_position_level(position_list: list) -> int:
    """计算职位等级评分"""
    if not position_list:
        return 0

    # 定义职位等级映射，以分数为键，职位为值（字符串匹配）90
    def is_principal(position):
        if "校长" in position and "副" not in position:
            if "助理" not in position:
                if "讲座教授" not in position:
                    return True
        return False

    # 匹配“副校长”，返回85分
    def is_vice_principal(position):
        if "副校长" in position:
            if "助理" not in position:
                return True
        return False

    # 匹配“国家”或“中国”并且包含“主任”或“理事长”，排除“副”  80
    def is_national_lab_director(position):
        if ("国家" in position or "中国" in position) and ("主任" in position or "理事长" in position):
            if "副" not in position:  # 排除副职
                return True
        return False

    # 匹配“带头人”或“首席科学家”，返回80分
    def is_leader_or_chief_scientist(position):
        if "带头人" in position or "首席科学家" in position:
            return True
        return False

    # 匹配“国家”或“中国”并且包含“主任”或“理事长”、“秘书长”、“组长”、“主席”，要求副职  70
    def is_national_lab_vice_director(position):
        if ("国家" in position or "中国" in position) and (
            "主任" in position
            or "理事长" in position
            or "秘书长" in position
            or "组长" in position
            or "主席" in position
        ):
            if "副" in position:  # 副职
                return True
        return False

    # 匹配包含“省”或省名字，并且包含“主任”或“理事长”、“秘书长”、“组长”、“主席”，排除副职 70
    def is_provincial_position(position):
        if "省" in position and (
            "主任" in position
            or "理事长" in position
            or "秘书长" in position
            or "组长" in position
            or "主席" in position
        ):
            if "副" not in position:  # 排除副职
                return True
        return False

    def is_director_or_chair(position):
        if "处长" in position or "院长" in position or "部长" in position or "党委书记" in position:
            if "助理" not in position:
                return True
        return False

    # 取出所有匹配的职位等级
    levels = []

    # 遍历所有职位，匹配对应的规则
    for position in position_list:
        if is_principal(position):
            levels.append(90)
        if is_vice_principal(position):
            levels.append(85)
        if is_national_lab_director(position):
            levels.append(80)
        if is_leader_or_chief_scientist(position):
            levels.append(80)
        if is_national_lab_vice_director(position):
            levels.append(70)
        if is_provincial_position(position):
            levels.append(70)
        if is_director_or_chair(position):
            levels.append(70)
        if not any(
            [
                is_principal(position),
                is_vice_principal(position),
                is_national_lab_director(position),
                is_leader_or_chief_scientist(position),
                is_national_lab_vice_director(position),
                is_provincial_position(position),
                is_director_or_chair(position),
            ]
        ):
            levels.append(60)
    # print(levels)
    # 如果找到匹配的职位等级，返回最高的
    if levels:
        highest_level = max(levels)
    # 如果没有匹配的职位，且职位列表不为空，返回 60 分
    else:
        highest_level = 0

    return highest_level


def calculate_titles_level(titles: list) -> int:
    """计算职称等级评分"""
    if not titles:
        return 10

    max_score = 10  # 默认评分
    for title in titles:
        for score_str, title_group in titles_level_scores.items():
            if title in title_group:
                max_score = max(max_score, int(score_str))
                break
    return max_score


def calculate_teacher_level(teacher_df: pd.DataFrame, school_level_dict) -> pd.DataFrame:
    """计算教师等级信息"""

    levels = []
    for _, row in teacher_df.iterrows():
        try:
            positions = json.loads(row["position"]) if row["position"] else None

            titles = json.loads(row["title"])

            famous_titles = json.loads(row["normalized_titles"])

            host_projects = json.loads(row["host_projects"])

            join_projects = json.loads(row["join_projects"])

            level_row = {
                "teacher_id": row["teacher_id"],
                "famous_titles_level": calculate_famous_titles_level(famous_titles),
                "project_level": calculate_famous_projects_level(host_projects),
                "position_level": calculate_position_level(positions),
                "job_title_level": calculate_titles_level(titles),
                "school_level": school_level_dict.get(row["school_name"], 40),
            }
            levels.append(level_row)

        except Exception:
            continue

    return pd.DataFrame(levels)
