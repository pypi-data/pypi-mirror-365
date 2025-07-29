# LLM Processing Module README

## 模块结构
```
llm/
├── config/                # 配置文件目录
│   ├── famous_titles.json   # 著名人才职称配置
│   ├── llm_config.yaml      # LLM模型配置
│   ├── positions.json       # 行政职务配置
│   └── titles.json          # 学术职称配置
├── services/              # 核心服务模块
│   ├── llm_area.py          # 研究领域提取
│   ├── llm_email.py         # 邮箱提取
│   ├── llm_famous.py        # 著名人才识别
│   ├── llm_name.py          # 姓名提取
│   ├── llm_omit.py          # 简介处理
│   ├── llm_position.py      # 行政职务提取
│   ├── llm_project.py       # 科研项目提取
│   ├── llm_title.py         # 职称识别
│   └── llm_translate.py     # 英文翻译
├── llm_base.py              # 基础类模块
└── llm_test.py              # 单元测试
```

## 配置说明
### llm/config/llm_config.yaml
```yaml
llm_config:
  doubao-1-5-pro-32k-250115:  # 模型名称
    api_key: "your_api_key"   # API密钥
    base_url: "api_endpoint"  # 接口地址
  qwen2.5-instruct:           # 支持多模型配置
    api_key: "your_api_key"
    base_url: "api_endpoint"
```

## 核心服务
### 基础功能类
`BaseLLMProcessor` 提供以下基础能力：
- LLM客户端初始化
- 日志系统集成
- 带重试机制的API调用
- 提示词模板构建
- 输入输出处理

### 服务模块规范
所有服务模块遵循统一接口：
```python
class XxxProcessor(BaseLLMProcessor):
    def build_prompt(self, input_data: dict) -> str: ...
    async def process(self, *args, **kwargs) -> tuple: ...
```

## 使用示例
```python
# 初始化处理器
processor = NameProcessor()

# 准备输入数据
input_data = {"TEXT": "作者：<name>李四</name>"}

# 执行处理
result, is_valid = await processor.run(input_data)

# 输出结果
print(f"提取姓名: {result}, 有效性: {is_valid}")
```

## 测试指南
运行单元测试：
```bash
# 在项目根目录执行
export PYTHONPATH=$(pwd)
pytest -v -s auto_teacher_process/llm/llm_test.py
```

测试覆盖功能：
- 姓名提取验证
- 邮箱识别准确性
- 研究领域提取
- 行政职务解析
- 著名人才识别
- 项目提取
- 职称识别
- 英文翻译
- 简介处理

## 开发规范
1. 新增服务模块需继承`BaseLLMProcessor`
2. 保持`build_prompt`与`process`方法分离
3. 错误处理需包含`try-except`块
4. 日志记录使用`self.logger`对象
5. 配置修改需同步更新对应JSON文件
