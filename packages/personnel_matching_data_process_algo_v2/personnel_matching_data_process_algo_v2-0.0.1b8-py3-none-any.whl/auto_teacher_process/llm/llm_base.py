import time
from abc import ABC, abstractmethod

from openai import AsyncOpenAI
from openai._types import NOT_GIVEN, NotGiven
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed

from auto_teacher_process.config import Config
from auto_teacher_process.logger import setup_logger


class BaseLLMProcessor(ABC):
    def __init__(
        self, model_name: str = "qwen2.5-instruct", logger=None, system="llm_processor", stage="unkonw_task_name"
    ):
        """
        LLM处理基类初始化
        实例变量:
        - args: argparse.Namespace 解析后的命令行参数
        - logger: logging.Logger 日志记录器
        - model_name: str LLM模型名称
        - client: AsyncOpenAI LLM客户端
        - system: str
        - stage: str 当前Task名称(或错误类型)
        """
        self.logger = logger if logger else setup_logger(system=system, stage=stage)
        self.client = None
        self.model_name = model_name
        self.initialize_llm_client(model_name)

    def initialize_llm_client(self, model_name: str) -> None:
        """
        初始化LLM客户端
        输入:
            model_name (str): 模型名称
        输出: 无 (初始化实例变量 model_name 和 client)
        """
        if not Config.LLM.is_in_model_list(model_name):
            raise ValueError(f"未找到模型配置: {model_name}")

        conf = Config.LLM.get_llm_config(model_name)
        self.client = AsyncOpenAI(api_key=conf["api_key"], base_url=conf["base_url"])
        # self.logger.debug(f"LLM客户端初始化完成，模型: {model_name}")

    @retry(stop=stop_after_attempt(600), wait=wait_fixed(1), retry=retry_if_exception(lambda e: True))
    async def get_llm_response(
        self,
        prompt: str,
        temperature: float | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        带重试机制的LLM请求
        输入:
            prompt (str): 提示词
            temperature (float): 生成温度
        输出:
            str: LLM的响应文本
        """
        if self.client is None:
            self.logger.warning("LLM client没有初始化，使用默认配置初始化")
            self.initialize_llm_client()

        messages = [{"role": "system", "content": ""}, {"role": "user", "content": prompt}]

        # try:
        self.logger.debug(f"异步发送LLM请求: {prompt[:100]}...", extra={"event": "running"})
        start_time = time.perf_counter()
        completion = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
        )
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        self.logger.debug(
            f"LLM响应: {completion.choices[-1]}...", extra={"event": "running", "duration_ms": duration_ms}
        )

        # 判断是否触发敏感词
        if completion.choices[-1].finish_reason == "content_filter":
            raise Exception("LLM返回结果非正常结束")

        return completion.choices[-1].message.content
        # except Exception as e:
        #     self.logger.error(f"LLM请求失败: {e!s}", exc_info=True)
        #     raise e

    @abstractmethod
    def build_prompt(self, *args, **kwargs) -> str:
        """
        构建提示词 (抽象方法)
        输入: 任务相关参数
        输出:
            str: 完整的提示词
        """

    @abstractmethod
    async def process(self, *args, **kwargs) -> tuple:
        """
        处理流程 (抽象方法)
        输入:
            相关参数
        输出:
            tuple: (处理结果, 是否成功) 例如 (result, success)
        """

    async def run(self, input_data: dict) -> tuple:
        """
        执行完整的处理流程
        输入:
            input_data (dict): 输入数据,字典格式，以支持多个输入
        输出:
            tuple: (最终结果, 处理状态)
        """
        try:
            self.logger.debug(
                f"启动llm处理流程{self.__class__.__name__}，输入参数:{input_data}", extra={"event": "start"}
            )
            start_time = time.time()
            result = await self.process(input_data=input_data)
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            self.logger.debug("处理完成", extra={"event": "end", "duration_ms": duration_ms})
            return result
        except Exception as e:
            self.logger.error(f"处理失败: {e!s}", exc_info=True)
            raise e
