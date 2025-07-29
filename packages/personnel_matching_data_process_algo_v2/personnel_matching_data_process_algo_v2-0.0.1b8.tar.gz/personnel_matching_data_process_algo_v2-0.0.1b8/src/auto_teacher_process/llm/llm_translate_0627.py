import asyncio
import re
import sys

import pandas as pd
import yaml

sys.path.append("/root/wyq")
import argparse
import logging
import os
from logging.handlers import RotatingFileHandler

from openai import AsyncOpenAI

# from db_utils.db_util import get_df_from_db_by_query
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed
from tqdm import tqdm


def setup_logging(log_file="data_insertion.log"):
    """
    配置日志记录
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(log_file, maxBytes=10**7, backupCount=5)
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger


# 读取 YAML 配置
with open("/root/wyq/auto_teacher_process/llm_config.yaml") as f:
    config = yaml.safe_load(f)
model_name = config["model_name"]
api_key = config["api_key"]
base_url = config["base_url"]
client = AsyncOpenAI(api_key=api_key, base_url=base_url)

import pymysql

db_config = {
    "host": "172.22.121.11",
    "user": "lhh",
    "password": "ef4cbd4e-0583-407e-aa78-7ba33ff7958b",
    "database": "personnel-matching-new",
    "port": 43200,
    "charset": "utf8mb4",  # 推荐设置字符集
    "cursorclass": pymysql.cursors.Cursor,  # 使用默认游标
    # 'host': "localhost",
    # 'port': 3306,
    # 'user': "root",
    # 'password': "123456",
    # 'database': "test",
    # 'charset': 'utf8mb4'
}
translate_prompt = """
你是一个专业的中英翻译助手。请将教师{NAMES}简介翻译成中文，要求如下：

1. 准确、自然地翻译英文内容；
2. 简介中姓名信息绝对不要翻译，保持原始语言；
3. 除人名外，所有内容请用通顺、符合中文表达习惯的语言翻译；
4. 不得添加、删减或改写原文信息；
5. 请仅输出翻译结果，并用 <translation> 和 </translation> 标签包裹。

英文简介如下：
<english_text>
{TEXT}
</english_text>

输出格式如下：
<translation>
（在这里填写翻译结果）
</translation>
"""


def parse_response(response):
    # 使用正则提取 translation 标签内容，忽略大小写，允许换行
    match = re.search(r"<translation[^>]*>(.*?)</translation>", response, re.IGNORECASE | re.DOTALL)
    if match:
        content = match.group(1).strip()
        return content, 1
    print("未找到 <> 标签")
    return "", 0


@retry(stop=stop_after_attempt(600), wait=wait_fixed(2), retry=retry_if_exception(lambda e: True))
async def get_llm_response(prompt):
    messages = [
        {
            "role": "system",
            "content": "",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    completion = await client.chat.completions.create(model=model_name, messages=messages, temperature=0.3)

    return completion.choices[-1].message.content


async def extract_email(description, derived_teacher_name):
    raw_prompt = translate_prompt.format(TEXT=description, NAMES=derived_teacher_name)
    # raw_prompt = translate_prompt.format(TEXT=description)

    try:
        output = await get_llm_response(raw_prompt)
    except Exception as e:  # 捕获所有异常
        print(f"请求失败，出现异常：{e}. 返回空字符串。")
        exit(1)
    cn_description, is_valid = parse_response(output)
    return cn_description, is_valid


def get_user_subset(users, i, n_splits):
    # 确保 i 在合法范围内
    if i < 1 or i > n_splits:
        raise ValueError(f"参数 i 必须在 1 和 {n_splits} 之间")

    # 计算每份的大小
    total_users = len(users)
    split_size = total_users // n_splits
    remainder = total_users % n_splits  # 处理不能整除的情况

    # 计算分割的起始和结束索引
    start_idx = (i - 1) * split_size + min(i - 1, remainder)
    end_idx = start_idx + split_size + (1 if i <= remainder else 0)

    return users[start_idx:end_idx]


def save_to_cache(new_df_list, args):
    output_dir = f"{args.save_dir}/sub_{args.sub}"
    os.makedirs(output_dir, exist_ok=True)
    cache_file = os.path.join(output_dir, f"{args.province}_cache.csv")
    new_df = pd.DataFrame(new_df_list)
    new_df.to_csv(cache_file, index=False)
    # print(f"定时缓存: {args.province} 的数据已经保存到 {cache_file}")


def load_cache(args):
    cache_file = f"{args.save_dir}/sub_{args.sub}/{args.province}_cache.csv"
    if os.path.exists(cache_file):
        print(f"加载缓存: 从 {cache_file} 加载之前保存的数据")
        df = pd.read_csv(cache_file)
        processed_teachers = set(df["teacher_id"].values)
        df_list = df.to_dict(orient="records")
        return df_list, processed_teachers
    print("没有找到缓存，重新开始处理")
    return [], set()


def fetch_all_data(query):
    db_connection = pymysql.connect(**db_config)
    cursor = db_connection.cursor()
    # 执行SQL查询
    cursor.execute(query, ())
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    raw_info = pd.DataFrame(rows, columns=columns)
    return raw_info


async def main(args):
    new_df_list, processed_teachers = load_cache(args)
    batch_size = 100000  # 每批处理的大小
    save_interval = 1  # 每处理 n 批后保存一次

    # TODO: 修改查询条件 id <=20 , id > 20 AND id <= 40, id > 40 AND id <= 50
    query_sql = args.query_sql

    df_teachers = fetch_all_data(query_sql)
    # df_teachers.to_parquet("/home/lhh/datawork/email/0605/data/not_email_data.parquet")
    # df_teachers = pd.read_parquet("/home/lhh/datawork/email/0605/data/not_email_data.parquet")
    print(f"df_teachers of len: {len(df_teachers)}")

    df_teachers = get_user_subset(df_teachers, args.sub, args.all)
    print(f"第 {args.sub} 份教师数据共有 {len(df_teachers)} 条记录")

    # # 过滤
    # df_teachers = df_teachers[~df_teachers["omit_description"].str.lower().str.contains(
    #     "i'm unable to answer that question|you can try asking about another topic|i can't help with that|as an ai developed by|i'm sorry, but i can't|this request cannot be fulfilled",
    #     regex=True
    # )]
    # 处理单个教师的函数
    async def process_row(row):
        teacher_id = row.teacher_id
        if teacher_id in processed_teachers:
            return None  # 跳过已处理的教师

        ori_description = row.omit_description
        derived_teacher_name = row.derived_teacher_name
        if ori_description:
            cn_description, is_valid = await extract_email(ori_description, derived_teacher_name)
            # cn_description, is_valid = await extract_email(ori_description)

        else:
            cn_description = ""
            is_valid = 0

        new_row = {
            "teacher_id": teacher_id,
            "cn_description": cn_description,
            "is_valid": is_valid,
            "description": ori_description,
        }

        return new_row

    # 异步处理批量行的主函数
    # async def process_batch(batch_rows):
    #     tasks = [process_row(row) for _, row in batch_rows.iterrows()]
    #     results = await asyncio.gather(*tasks)
    #     return [result for result in results if result]
    async def process_batch(batch_rows, max_concurrent=500):
        semaphore = asyncio.Semaphore(max_concurrent)

        async def run_with_semaphore(row):
            async with semaphore:
                return await process_row(row)

        tasks = [asyncio.create_task(run_with_semaphore(row)) for _, row in batch_rows.iterrows()]
        results = await asyncio.gather(*tasks)
        return [result for result in results if result]

    # valid_email_count = 0  # 有效邮箱计数器

    for i in tqdm(range(0, len(df_teachers), batch_size)):
        batch_rows = df_teachers.iloc[i : i + batch_size]

        # 处理批次行
        new_rows = await process_batch(batch_rows)

        # 将batch结果存入new_df_list
        new_df_list.extend(new_rows)

        # # 更新有效邮箱计数
        # valid_email_count += sum(1 for row in new_rows if row['is_valid'] == 1)

        # # 满100条有效数据，提前结束
        # if valid_email_count >= 100:
        #     print(f"已提取 {valid_email_count} 条有效邮箱，提前停止提取。")
        #     break

        # 定期保存 DataFrame 到 CSV
        if (i // batch_size + 1) % save_interval == 0:
            save_to_cache(new_df_list, args)

    new_df = pd.DataFrame(new_df_list)
    new_df["create_time"] = pd.Timestamp.now()
    new_df["update_time"] = pd.Timestamp.now()

    output_dir = f"{args.save_dir}/sub_{args.sub}"
    os.makedirs(output_dir, exist_ok=True)
    new_df.to_csv(os.path.join(output_dir, args.province + "_all.csv"), index=False)
    print("########################################")
    print(f"{args.province} 的 email 提取数据已经保存！！！！！！")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="接受命令行参数的示例脚本")
    parser.add_argument("--province", type=str, default="", required=False, help="输入省份")
    parser.add_argument("--sub", type=int, default=1, required=False)
    parser.add_argument("--all", type=int, default=1, required=False)
    parser.add_argument("--save_dir", type=str, default="", required=False)
    parser.add_argument("--query_sql", type=str, default="", required=False)
    logger = setup_logging()
    args = parser.parse_args()
    args.province = "0627qw"
    args.sub = 1
    args.all = 1
    args.save_dir = "/root/wyq/auto_teacher_process/data"
    args.query_sql = """
SELECT o.*, t.derived_teacher_name
FROM (
    SELECT *
    FROM derived_intl_omit_description
    WHERE is_valid = 1
    ORDER BY id DESC
    LIMIT 100
) AS o
LEFT JOIN derived_intl_teacher_data AS t
ON o.teacher_id = t.teacher_id;

    """
    asyncio.run(main(args))
