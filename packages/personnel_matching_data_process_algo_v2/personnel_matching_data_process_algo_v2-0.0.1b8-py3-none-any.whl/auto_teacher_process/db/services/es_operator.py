import pandas as pd
from elasticsearch import AsyncElasticsearch

from auto_teacher_process.config import Config
from auto_teacher_process.logger import setup_logger


class ESOperator:
    """ES数据库通用操作器"""

    def __init__(self, system: str = "es_processor", stage: str = "unkonw_task_name", logger=None):
        self.es_engine = None
        self.logger = logger if logger else setup_logger(system=system, stage=stage)
        self._setup_es_engine()

    def _setup_es_engine(self):
        """初始化数据库引擎"""
        try:
            self.es_engine = AsyncElasticsearch(
                hosts=[{"scheme": "http", "host": Config.DB.ES.HOST, "port": Config.DB.ES.PORT}],
                basic_auth=(Config.DB.ES.USER, Config.DB.ES.PASSWORD),
                connections_per_node=200,
                request_timeout=30,
                retry_on_timeout=True,
                max_retries=3,
            )
            self.logger.debug("ES连接成功")
        except Exception as e:
            self.logger.error(f"ES连接失败: {e}", exc_info=True)
            raise e

    def get_es_engine(self):
        """获取数据库引擎"""
        return self.es_engine

    async def close_es_engine(self):
        """关闭数据库引擎"""
        if self.es_engine:
            try:
                await self.es_engine.close()
            except Exception as e:
                self.logger.error(f"关闭ES数据库引擎失败: {e}", exc_info=True)
                raise e
            finally:
                self.logger.debug("ES数据库引擎已关闭")

    # 工具函数
    async def get_data_from_es(self, index_name, query, scroll_size):
        try:
            # 初始化滚动查询
            scroll_response = await self.es_engine.search(index=index_name, query=query, size=scroll_size, scroll="5m")

            scroll_id = scroll_response.get("_scroll_id")
            hits = scroll_response["hits"]["hits"]
            all_data = []

            # 滚动获取所有数据
            while hits:
                all_data.extend([hit["_source"] for hit in hits])
                scroll_response = await self.es_engine.scroll(scroll_id=scroll_id, scroll="5m")
                scroll_id = scroll_response.get("_scroll_id")
                hits = scroll_response["hits"]["hits"]

            # 清理滚动上下文
            if scroll_id:
                await self.es_engine.clear_scroll(scroll_id=scroll_id)
        except Exception as e:
            self.logger.error(f"ES数据库查询出错: {e}", exc_info=True)
            return []
        return all_data

    # ------------------------------------------------
    # 按"机构"滚动查询论文, 索引为 raw_teacher_paper
    # -----------------------------------------------
    async def async_es_to_df_by_affiliation_idx_paper(
        self, affiliation, index_name="raw_teacher_paper", scroll_size=5000
    ):
        """
        异步从ES查询指定机构的全部数据并转为DataFrame
        args:
            affiliation: 机构名称字符串或列表
            index_name: 索引名称，默认为 raw_teacher_paper
            scroll_size: 每次滚动查询的大小，默认为 5000
        returns:
            返回一个包含所有匹配记录的 DataFrame，如果没有匹配记录则返回空
        example:
            # 查询单个机构
            df = await async_es_to_df_by_affiliation_idx_paper("guangzhou university")
            # 查询多个机构
            df = await async_es_to_df_by_affiliation_idx_paper(["guangzhou university", "sun yat-sen university"])
        """
        try:
            # 处理输入的 affiliation 参数
            if isinstance(affiliation, str):
                # 单机构查询
                affiliation_query = {"term": {"affiliations": affiliation.lower()}}
            elif isinstance(affiliation, list):
                # 多机构查询
                affiliation_lower_list = [aff.lower() for aff in affiliation]
                affiliation_query = {"terms": {"affiliations": affiliation_lower_list}}
            else:
                raise ValueError("affiliation 参数必须是字符串或列表")

            all_data = await self.get_data_from_es(index_name, affiliation_query, scroll_size)

            if not all_data:
                print(f"未找到机构 '{affiliation}' 的匹配记录")
                self.logger.debug(f"未找到机构 '{affiliation}' 的匹配记录")
                return None

            df = pd.DataFrame(all_data)
            self.logger.debug(f"成功查询到 {len(df)} 条记录，机构: {affiliation}")
            return df

        except Exception as e:
            self.logger.error(f"es查询出错: {e!s}", exc_info=True)
            return None

    # ----------------------------------------------
    # 按"标题"查询论文, 索引为 raw_teacher_paper
    # ----------------------------------------------
    async def async_es_to_df_by_title_idx_paper(self, title, index_name="raw_teacher_paper", scroll_size=5000):
        """
        异步从ES查询指定标题的论文数据并返回DataFrame
        args:
            title: 论文标题
            index_name: 索引名称，默认为 raw_teacher_paper
            scroll_size: 每次滚动查询的大小，默认为 5000
        returns:
            返回一个包含所有匹配记录的列表，如果没有匹配记录则返回空列表
        example:
            # 查询单个标题
            df = await async_es_to_df_by_title_idx_paper(
                "Facile synthesis of Bi nanoparticle modified TiO2 with enhanced visible light photocatalytic activity"
            )
            # 查询多个标题
            df = await async_es_to_df_by_title_idx_paper([
                "Facile synthesis of Bi nanoparticle modified TiO2 with enhanced visible light photocatalytic activity",
                "Microstructural characteristics of a commercially pure Zr treated by pulsed laser at different powers"
            ])
        """
        try:
            # 处理输入的 title 参数
            if isinstance(title, str):
                # 单标题查询
                title_query = {"term": {"title.lowercase": title.lower()}}
            elif isinstance(title, list):
                # 多标题查询
                title_lower_list = [t.lower() for t in title]
                title_query = {"terms": {"title.lowercase": title_lower_list}}
            else:
                raise ValueError("title 参数必须是字符串或列表")

            all_data = await self.get_data_from_es(index_name, title_query, scroll_size)

            if not all_data:
                self.logger.debug(f"未找到标题 '{title}' 的匹配记录")
                return None

            df = pd.DataFrame(all_data)
            self.logger.debug(f"成功查询到 {len(df)} 条记录，标题: {title}")
            return df

        except Exception as e:
            self.logger.error(f"es查询出错: {e!s}", exc_info=True)
            return None

    # ----------------------------------------------
    # 按"教师"和"学校"查询教师信息, 索引为 derived_teacher_data
    # ----------------------------------------------
    async def async_es_to_df_by_teacher_and_school_name_idx_teacher_data(
        self, teacher, school_name, index_name="derived_teacher_data", scroll_size=5000
    ):
        """
        异步从ES查询教师和学校的全部数据并转为DataFrame
        args:
            teacher: 教师姓名（字符串）或姓名列表
            school_name: 学校名称
            index_name: 索引名称，默认为 derived_teacher_data
            scroll_size: 每次滚动查询的大小，默认为 5000
        returns:
            返回匹配记录的DataFrame，无记录时返回空DataFrame
        example:
            # 查询单个教师
            df = await async_es_to_df_by_teacher_and_school_name_idx_teacher_data("李进", "广州大学")
            # 查询多个教师
            df = await async_es_to_df_by_teacher_and_school_name_idx_teacher_data(["李进", "王宇"], "广州大学")
            # 查询多个教师和多个学校
            df = await async_es_to_df_by_teacher_and_school_name_idx_teacher_data(["李进", "王宇"], ["广州大学", "广东海洋大学", "中山大学", "华南理工大学"])
        """
        try:
            # 处理教师名称输入
            if isinstance(teacher, str):
                teacher_query = {"term": {"name_variants": teacher.lower()}}
            elif isinstance(teacher, list):
                teacher_query = {"terms": {"name_variants": [t.lower() for t in teacher]}}
            else:
                raise ValueError("teachers参数必须是字符串或列表")

            # 处理学校输入
            if isinstance(school_name, str):
                school_query = {"term": {"school_name": school_name.lower()}}
            elif isinstance(school_name, list):
                school_query = {"terms": {"school_name": [s.lower() for s in school_name]}}
            else:
                raise ValueError("school_name参数必须是字符串或列表")

            # 构建查询体
            query = {"bool": {"must": [teacher_query, school_query]}}

            all_data = await self.get_data_from_es(index_name, query, scroll_size)

            # 结果处理
            if not all_data:
                self.logger.debug(f"未找到教师 '{teacher}' 学校 '{school_name}' 的匹配记录")
                return None

            df = pd.DataFrame(all_data)
            self.logger.debug(f"成功查询到 {len(df)} 条记录，学校: {school_name}，教师: {teacher}")
            return df

        except Exception as e:
            self.logger.error(f"查询出错: {e!s}", exc_info=True)
            return None

    # ----------------------------------------------
    # 按"教师"查询教师信息, 索引为 derived_teacher_data
    # ----------------------------------------------
    async def async_es_to_df_by_teacher_idx_teacher_data(
        self, teacher, index_name="derived_teacher_data", scroll_size=5000
    ):
        """
        异步从ES查询教师的全部数据并转为DataFrame
        args:
            teacher: 教师姓名（字符串）或姓名列表
            index_name: 索引名称，默认为 derived_teacher_data
            scroll_size: 每次滚动查询的大小，默认为 5000
        returns:
            返回匹配记录的DataFrame，无记录时返回空DataFrame
        example:
            # 查询单个教师
            df = await async_es_to_df_by_teacher_idx_teacher_data("李进")
            # 查询多个教师
            df = await async_es_to_df_by_teacher_idx_teacher_data(["李进", "王宇"])
        """
        try:
            # 处理教师名称输入
            if isinstance(teacher, str):
                teacher_query = {"term": {"name_variants": teacher.lower()}}
            elif isinstance(teacher, list):
                teacher_query = {"terms": {"name_variants": [t.lower() for t in teacher]}}
            else:
                raise ValueError("teachers参数必须是字符串或列表")

            all_data = await self.get_data_from_es(index_name, teacher_query, scroll_size)

            # 结果处理
            if not all_data:
                self.logger.debug(f"未找到教师 '{teacher}' 的匹配记录")
                return None

            df = pd.DataFrame(all_data)
            self.logger.debug(f"成功查询到 {len(df)} 条记录，教师: {teacher}")
            return df

        except Exception as e:
            self.logger.error(f"查询出错: {e!s}", exc_info=True)
            return None

    # ----------------------------------------------
    # 按"发明人"和"申请机构"查询专利, 索引为 raw_teacher_patent
    # ----------------------------------------------
    async def async_es_to_df_by_inventor_and_applicant_idx_patent(
        self, inventor, applicant, index_name="raw_teacher_patent", scroll_size=5000
    ):
        """
        异步从ES查询发明人和单位的全部数据并转为DataFrame
        args:
            inventor: 发明人姓名（字符串）或姓名列表
            applicant: 申请机构名称
            index_name: 索引名称，默认为 raw_teacher_patent
            scroll_size: 每次滚动查询的大小，默认为 5000
        returns:
            返回一个包含所有匹配记录的 DataFrame，如果没有匹配记录则返回空
        example:
            # 查询单个发明人和单个机构
            df = await async_es_to_df_by_inventor_and_applicant_idx_patent("李进", "广州大学")
            # 查询多个发明人和单个机构
            df = await async_es_to_df_by_inventor_and_applicant_idx_patent(["李进", "王宇"], "广州大学")
            # 查询单个发明人和多个机构
            df = await async_es_to_df_by_inventor_and_applicant_idx_patent("李进", ["广州大学", "广东海洋大学", "中山大学", "华南理工大学"])
            # 查询多个发明人和多个机构
            df = await async_es_to_df_by_inventor_and_applicant_idx_patent(["李进", "王宇"], ["广州大学", "广东海洋大学", "中山大学", "华南理工大学"])
        """
        try:
            # 处理输入的 inventor 参数
            if isinstance(inventor, str):
                # 单发明人查询
                inventor_query = {"term": {"inventor": inventor.lower()}}
            elif isinstance(inventor, list):
                # 多发明人查询
                inventor_lower_list = [inv.lower() for inv in inventor]
                inventor_query = {"terms": {"inventor": inventor_lower_list}}
            else:
                raise ValueError("inventor 参数必须是字符串或列表")

            # 处理输入的 applicant 参数
            if isinstance(applicant, str):
                # 单申请机构
                applicant_query = {"wildcard": {"applicant": {"value": f"*{applicant.lower()}*"}}}
            elif isinstance(applicant, list):
                # 多申请机构
                applicant_queries = [{"wildcard": {"applicant": {"value": f"*{app.lower()}*"}}} for app in applicant]
                applicant_query = {"bool": {"should": applicant_queries}}
            else:
                raise ValueError("applicant 参数必须是字符串或列表")

            # 构建查询体（同时满足发明人和申请人条件）
            query = {"bool": {"must": [inventor_query, applicant_query]}}

            all_data = await self.get_data_from_es(index_name, query, scroll_size)

            if not all_data:
                self.logger.debug(f"未找到发明人 '{inventor}' 申请机构 '{applicant}' 的匹配记录")
                return None

            df = pd.DataFrame(all_data)
            self.logger.debug(f"成功查询到 {len(df)} 条记录，申请机构: {applicant}，发明人: {inventor}")
            return df
        except Exception as e:
            self.logger.error(f"查询出错: {e!s}", exc_info=True)
            return None

    # ----------------------------------------------
    # 按"作者"和"机构"查询论文, 索引为 raw_teacher_paper
    # ----------------------------------------------
    async def async_es_to_df_by_author_and_affiliation_idx_paper(
        self, author, affiliation, index_name="raw_teacher_paper", scroll_size=5000
    ):
        """
        异步从ES查询指定作者和机构的论文数据并转为DataFrame
        args:
            author: 作者姓名字符串或列表
            affiliation: 机构名称字符串或列表
            index_name: 索引名称，默认为 raw_teacher_paper
            scroll_size: 每次滚动查询的大小，默认为 5000
        returns:
            返回包含所有匹配记录的 DataFrame，无匹配时返回空DataFrame
        example:
            # 查询单个作者, 单个机构
            df = await async_es_to_df_by_author_and_affiliation_idx_paper("jin, li", "guangzhou university")
            # 查询多个作者, 单个机构
            df = await async_es_to_df_by_author_and_affiliation_idx_paper(["jin, li", "li, jin", "li, j."], "guangzhou university")
            # 查询单个作者, 多个机构
            df = await async_es_to_df_by_author_and_affiliation_idx_paper("li, jin", ["guangzhou university", "guangdong ocean university", "sun yat-sen university", "south china university of technology"])
            # 查询多个作者, 多个机构
            df = await async_es_to_df_by_author_and_affiliation_idx_paper(["jin, li", "li, jin", "li, j."], ["guangzhou university", "guangdong ocean university", "sun yat-sen university", "south china university of technology"])
        """
        try:
            # 处理输入的 author 参数
            if isinstance(author, str):
                # 单作者查询
                author_query = {"term": {"author_list": author.lower()}}
            elif isinstance(author, list):
                # 多作者查询
                author_lower_list = [auth.lower() for auth in author]
                author_query = {"terms": {"author_list": author_lower_list}}
            else:
                raise ValueError("author 参数必须是字符串或列表")

            # 处理输入的 affiliation 参数
            if isinstance(affiliation, str):
                # 单机构查询
                affiliation_query = {"term": {"affiliations": affiliation.lower()}}
            elif isinstance(affiliation, list):
                # 多机构查询
                affiliation_lower_list = [aff.lower() for aff in affiliation]
                affiliation_query = {"terms": {"affiliations": affiliation_lower_list}}
            else:
                raise ValueError("affiliation 参数必须是字符串或列表")

            # 构建查询体
            query = {
                "bool": {
                    "must": [
                        author_query,  # 作者查询
                        affiliation_query,  # 机构查询
                    ]
                }
            }

            all_data = await self.get_data_from_es(index_name, query, scroll_size)

            # 处理无匹配结果的情况
            if not all_data:
                self.logger.debug(f"未找到作者 '{author}' 机构 '{affiliation}' 的匹配记录")
                return None

            # 转换为DataFrame并返回
            df = pd.DataFrame(all_data)
            self.logger.debug(f"成功查询到 {len(df)} 条记录，机构: {affiliation}，作者: {author}")
            return df

        except Exception as e:
            self.logger.error(f"查询出错: {e!s}", exc_info=True)
            return None

    # ----------------------------------------------------------
    # 按"教师姓名"和"依托单位"通配符查询项目, 索引为 raw_teacher_project
    # ----------------------------------------------------------
    async def async_es_to_df_by_teacher_name_and_supporting_unit_idx_project(
        self, teacher_name, supporting_unit, index_name="raw_teacher_project", scroll_size=5000
    ):
        """
        异步从ES查询指定教师姓名和依托单位的项目数据并转为DataFrame
        args:
            teacher_name: 教师姓名字符串或列表
            supporting_unit: 依托单位字符串或列表
            index_name: 索引名称，默认为 raw_teacher_project
            scroll_size: 每次滚动查询的大小，默认为 5000
        returns:
            返回包含所有匹配记录的 DataFrame，无匹配时返回空DataFrame
        example:
            # 查询单个教师和依托单位
            df = await async_es_to_df_by_teacher_name_and_supporting_unit_idx_project("牛芳", "中国科学院")
            # 查询多个教师和多个依托单位
            df = await async_es_to_df_by_teacher_name_and_supporting_unit_idx_project(["牛芳", "陈佳洱"], ["中国科学院", "北京大学"])
            # 查询单个教师和多个依托单位
            df = await async_es_to_df_by_teacher_name_and_supporting_unit_idx_project("牛芳", ["中国科学院", "清华大学", "北京大学"])
            # 查询多个教师和单个依托单位
            df = await async_es_to_df_by_teacher_name_and_supporting_unit_idx_project(["牛芳", "陈佳洱"], "中国科学院")
        """
        try:
            # 处理教师姓名参数
            if isinstance(teacher_name, str):
                # 单个教师姓名
                teacher_query = {"wildcard": {"teacher_names": {"value": f"*{teacher_name.lower()}*"}}}
            elif isinstance(teacher_name, list):
                # 多个教师姓名
                teacher_queries = [
                    {"wildcard": {"teacher_names": {"value": f"*{name.lower()}*"}}} for name in teacher_name
                ]
                teacher_query = {"bool": {"should": teacher_queries}}
            else:
                raise ValueError("teacher_name 参数必须是字符串或列表")

            # 处理依托单位参数
            if isinstance(supporting_unit, str):
                # 单个依托单位
                unit_query = {"wildcard": {"supporting_unit": {"value": f"*{supporting_unit.lower()}*"}}}
            elif isinstance(supporting_unit, list):
                # 多个依托单位
                unit_queries = [
                    {"wildcard": {"supporting_unit": {"value": f"*{unit.lower()}*"}}} for unit in supporting_unit
                ]
                unit_query = {"bool": {"should": unit_queries}}
            else:
                raise ValueError("supporting_unit 参数必须是字符串或列表")

            # 构建完整查询体
            query = {"bool": {"must": [teacher_query, unit_query]}}

            all_data = await self.get_data_from_es(index_name, query, scroll_size)

            # 处理无匹配结果的情况
            if not all_data:
                self.logger.debug(f"未找到教师姓名 '{teacher_name}' 依托单位 '{supporting_unit}' 的匹配记录")
                return pd.DataFrame()

            # 转换为DataFrame并返回
            df = pd.DataFrame(all_data)
            self.logger.debug(f"成功查询到 {len(df)} 条记录，依托单位: {supporting_unit}，教师姓名: {teacher_name}")
            return df

        except Exception as e:
            self.logger.error(f"查询出错: {e!s}", exc_info=True)
            return pd.DataFrame()

    # ----------------------------------------------------------
    # 按"作者"和"机构"查询中文论文, 索引为 raw_teacher_cn_paper
    # ----------------------------------------------------------
    async def async_es_to_df_by_author_and_affiliation_idx_cn_paper(self, author, affiliation,
                                                                    index_name="raw_teacher_cn_paper",
                                                                    scroll_size=5000):
        """
        异步从ES查询指定作者和机构的论文数据并转为DataFrame
        args:
            author: 作者姓名字符串或列表
            affiliation: 机构名称字符串或列表
            index_name: 索引名称，默认为 raw_teacher_paper
            scroll_size: 每次滚动查询的大小，默认为 5000
        returns:
            返回包含所有匹配记录的 DataFrame，无匹配时返回空DataFrame
        example:
            # 查询单个作者, 单个机构
            df = await async_es_to_df_by_author_and_affiliation_idx_cn_paper("夏云", "中国科学院大学")
            # 查询多个作者, 单个机构
            df = await async_es_to_df_by_author_and_affiliation_idx_cn_paper(["夏云", "曾晓茂"], "中国科学院大学")
            # 查询单个作者, 多个机构
            df = await async_es_to_df_by_author_and_affiliation_idx_cn_paper("曾晓茂", ["guangzhou university", "中国科学院大学"])
            # 查询多个作者, 多个机构
            df = await async_es_to_df_by_author_and_affiliation_idx_cn_paper(["夏云", "曾晓茂"], ["guangzhou university", "中国科学院大学"])
        """
        try:
            # 处理输入的 author 参数
            if isinstance(author, str):
                # 单作者查询
                author_query = {"term": {"full_author_list": author.lower()}}
            elif isinstance(author, list):
                # 多作者查询
                author_lower_list = [auth.lower() for auth in author]
                author_query = {"terms": {"full_author_list": author_lower_list}}
            else:
                raise ValueError("author 参数必须是字符串或列表")

            # 处理输入的 affiliation 参数
            if isinstance(affiliation, str):
                # 单机构
                affiliation_query = {
                    "wildcard": {
                        "affiliations": {
                            "value": f"*{affiliation.lower()}*"
                        }
                    }
                }
            elif isinstance(affiliation, list):
                # 多机构
                affiliation_queries = [
                    {
                        "wildcard": {
                            "affiliations": {
                                "value": f"*{aff.lower()}*"
                            }
                        }
                    }
                    for aff in affiliation
                ]
                affiliation_query = {"bool": {"should": affiliation_queries}}
            else:
                raise ValueError("affiliation 参数必须是字符串或列表")

            # 构建查询体
            query = {
                "bool": {
                    "must": [
                        author_query,  # 作者查询
                        affiliation_query  # 机构查询
                    ]
                }
            }

            all_data = await self.get_data_from_es(index_name, query, scroll_size)

            # 处理无匹配结果的情况
            if not all_data:
                self.logger.debug(f"未找到作者 '{author}' 机构 '{affiliation}' 的匹配记录")
                return None

            # 转换为DataFrame并返回
            df = pd.DataFrame(all_data)
            self.logger.debug(f"成功查询到 {len(df)} 条记录，机构: {affiliation}，作者: {author}")
            return df

        except Exception as e:
            self.logger.error(f"查询出错: {e!s}", exc_info=True)
            return None