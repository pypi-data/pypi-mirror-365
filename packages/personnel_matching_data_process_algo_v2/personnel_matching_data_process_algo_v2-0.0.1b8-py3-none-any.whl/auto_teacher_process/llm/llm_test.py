import json

import pytest

from auto_teacher_process.llm.services.llm_area import AreaLLMProcessor
from auto_teacher_process.llm.services.llm_email import EmailLLMProcessor
from auto_teacher_process.llm.services.llm_experience import ExperienceLLMProcessor
from auto_teacher_process.llm.services.llm_famous import FamousLLMProcessor
from auto_teacher_process.llm.services.llm_name import NameLLMProcessor
from auto_teacher_process.llm.services.llm_omit import OmitLLMProcessor
from auto_teacher_process.llm.services.llm_position import PositionLLMProcessor
from auto_teacher_process.llm.services.llm_project import ProjectLLMProcessor
from auto_teacher_process.llm.services.llm_teacher_disappear import TeacherDisappearLLMProcessor
from auto_teacher_process.llm.services.llm_title import TitleLLMProcessor
from auto_teacher_process.llm.services.llm_translate import TranslateLLMProcessor


@pytest.mark.asyncio
async def test_name_processor():
    """综合测试NameProcessor类的核心功能"""
    # 初始化处理器实例
    processor = NameLLMProcessor(system="test_system", stage="test_stage")

    # 测试1: 验证完整处理流程（成功场景）
    success_raw_name = {"teacher_name": "作者：<name>李四</name>"}
    result, is_valid = await processor.run(success_raw_name)
    assert result == "李四"
    assert is_valid == 1

    # 测试2: 验证完整处理流程（失败场景）
    failure_raw_name = {"teacher_name": "你说得对，但也不是很对，有一部分对"}
    result, is_valid = await processor.run(failure_raw_name)
    assert result == ""
    assert is_valid == 0

    # 测试3: 验证参数验证（缺少teacher_name键）
    with pytest.raises(ValueError):
        await processor.run({})


@pytest.mark.asyncio
async def test_area_processor():
    """综合测试AreaProcessor类的核心功能"""
    # 初始化处理器实例
    processor = AreaLLMProcessor()

    # 测试1: 验证完整处理流程（成功场景）
    success_input = {"description": "张三教授主要从事人工智能、机器学习和自然语言处理方面的研究工作。"}
    result, is_valid = await processor.run(success_input)
    assert isinstance(result, list)
    assert len(result) >= 2
    assert all(isinstance(area, str) for area in result)
    assert is_valid == 1

    # 测试2: 验证完整处理流程（失败场景）
    failure_input = {"description": "这是一段与研究领域无关的文本内容。"}
    result, is_valid = await processor.run(failure_input)
    assert result == []
    assert is_valid == 0

    # 测试3: 验证参数验证（缺少description键）
    with pytest.raises(ValueError):
        await processor.run({})


@pytest.mark.asyncio
async def test_email_processor():
    """综合测试EmailProcessor类的核心功能"""
    # 初始化处理器实例
    processor = EmailLLMProcessor()

    # 测试1: 验证完整处理流程（成功场景）
    success_input = {"description": "张三教授的邮箱是zhangsan@example.com，欢迎联系。"}
    result, is_valid = await processor.run(success_input)
    assert result == "zhangsan@example.com"
    assert is_valid == 1

    # 测试2: 验证完整处理流程（失败场景）
    failure_input = {"description": "这是一段不包含邮箱地址的测试文本。"}
    result, is_valid = await processor.run(failure_input)
    assert result == ""
    assert is_valid == 0

    # 测试3: 验证参数验证（缺少description键）
    with pytest.raises(ValueError):
        await processor.run({})


@pytest.mark.asyncio
async def test_position_processor():
    """综合测试PositionProcessor类的核心功能"""
    # 初始化处理器实例
    processor = PositionLLMProcessor()

    # 测试1: 验证完整处理流程（成功场景）
    success_input = {"description": "张三教授现任中山大学计算机学院院长，同时担任人工智能实验室主任。"}
    result, is_valid = await processor.run(success_input)
    assert isinstance(result, list)
    assert len(result) == 2
    assert "中山大学计算机学院院长" in result
    assert "中山大学人工智能实验室主任" in result
    assert is_valid == 1

    # 测试2: 验证完整处理流程（失败场景）
    failure_input = {"description": "这是一段不包含行政职务信息的测试文本。"}
    result, is_valid = await processor.run(failure_input)
    assert result == []
    assert is_valid == 0

    # 测试3: 验证参数验证（缺少description键）
    with pytest.raises(ValueError):
        await processor.run({})


@pytest.mark.asyncio
async def test_project_processor():
    """综合测试ProjectProcessor类的核心功能"""
    # 初始化处理器实例
    processor = ProjectLLMProcessor()

    # 测试1: 验证完整处理流程（成功场景）
    success_input = {
        "description": "李四教授主持国家自然科学基金项目《人工智能基础研究》，并参与了《机器学习应用研究》项目。"
    }
    result, is_valid = await processor.run(success_input)
    assert isinstance(result, dict)
    assert "主持的项目" in result and len(result["主持的项目"]) >= 1
    assert "参与的项目" in result and len(result["参与的项目"]) >= 1
    assert any("人工智能基础研究" in item for item in result["主持的项目"])
    assert any("机器学习应用研究" in item for item in result["参与的项目"])
    assert is_valid == 1

    # 测试2: 验证完整处理流程（失败场景 - 无项目）
    failure_input = {"description": "这是一段不包含科研项目的教师简介描述文本。"}
    result, is_valid = await processor.run(failure_input)
    assert result == {"主持的项目": [], "参与的项目": []}
    assert is_valid == 0

    # 测试3: 验证参数验证（缺少description键）
    with pytest.raises(ValueError):
        await processor.run({})

    # 测试4: 验证论文专利过滤逻辑
    paper_patent_input = {
        "description": "王五博士发表了多篇论文，包括《深度学习研究》和《计算机视觉进展》，并申请了两项专利：《图像处理方法》和《数据压缩系统》"
    }
    result, is_valid = await processor.run(paper_patent_input)
    assert result == {"主持的项目": [], "参与的项目": []}
    assert is_valid == 0


@pytest.mark.asyncio
async def test_translate_processor():
    """综合测试TranslateProcessor类的核心功能"""
    # 初始化处理器实例
    processor = TranslateLLMProcessor()

    # 测试1: 验证完整处理流程（成功场景）
    success_input = {"description": "The quick brown fox jumps over the lazy dog."}
    result, is_valid = await processor.run(success_input)
    assert isinstance(result, str)
    assert len(result) > 0
    assert is_valid == 1

    # 测试2: 验证参数验证（缺少description键）
    with pytest.raises(ValueError):
        await processor.run({})

    # 测试3: 验证空输入处理
    empty_input = {"description": ""}
    result, is_valid = await processor.run(empty_input)
    assert result == ""
    assert is_valid == 0


@pytest.mark.asyncio
async def test_title_processor():
    """综合测试TitleProcessor类的核心功能"""
    # 初始化处理器实例
    processor = TitleLLMProcessor()

    # 测试1: 验证完整处理流程（成功场景）
    success_input = {"description": "张三教授，博士生导师，现任中山大学计算机学院院长，同时担任人工智能实验室主任。"}
    teacher_title, _, is_valid = await processor.run(success_input)
    assert isinstance(teacher_title, str)
    teacher_title = json.loads(teacher_title)
    assert len(teacher_title) == 2
    assert "教授" in teacher_title
    assert "博士生导师" in teacher_title
    assert is_valid == 1

    # 测试2: 验证完整处理流程（失败场景）
    failure_input = {"description": "这是一段不包含职称信息的测试文本。"}
    teacher_title, _, is_valid = await processor.run(failure_input)
    assert teacher_title == "[]"
    assert is_valid == 0

    # 测试3: 验证参数验证（缺少description键）
    teacher_title, _, is_valid = await processor.run({})
    assert is_valid == 0


@pytest.mark.asyncio
async def test_omit_processor():
    """综合测试OmitProcessor类的核心功能"""
    # 初始化处理器实例
    processor = OmitLLMProcessor()

    # 测试1: 验证完整处理流程（成功场景 - 中文模式）
    success_input = {
        "teacher_name": "张三",
        "description": "贪玩蓝月，一刀999，是兄弟就来砍我！！！\n张三教授现任中山大学计算机学院院长，同时担任人工智能实验室主任。他长期从事人工智能领域的研究工作，主持多项国家级科研项目，发表SCI论文50余篇。",
        "mode": "cn",
    }
    result, is_valid = await processor.run(success_input)
    assert isinstance(result, str)
    assert len(result) >= 20
    assert "张三" in result and ("教授" in result or "院长" in result)
    assert is_valid == 1

    # 测试2: 验证完整处理流程（失败场景 - 空输入）
    failure_input = {"teacher_name": "李四", "description": "", "mode": "cn"}
    result, is_valid = await processor.run(failure_input)
    assert result == ""
    assert is_valid == 0

    # 测试3: 验证参数验证（缺少必要参数）
    with pytest.raises(KeyError):
        await processor.run(
            {
                "teacher_name": "王五",
                # 缺少description参数
                "mode": "cn",
            }
        )

    # 测试4: 验证英文模式下的功能
    en_input = {
        "teacher_name": "约翰·史密斯",
        "description": """Here's a sample English introduction for Professor John Smith with meaningless ad phrases as requested:

**"Hot deal alert! Limited time offer!**

Professor John Smith is a distinguished scholar in computational neuroscience, currently holding the prestigious Chair of Cognitive Science at MIT. With over 15 years of research experience, he has published 100+ peer-reviewed papers on neural networks and AI ethics. His groundbreaking work on brain-machine interfaces earned him the Turing Award in 2022. Beyond academia, he advises the UN on AI policy and hosts the popular podcast *Future Minds*. Students praise his engaging lectures, blending humor with cutting-edge insights. **But wait! There’s more!** He’s also an avid mountaineer and plays jazz flute. **Act now! Supplies are infinite!"**
""",
        "mode": "en",
    }
    result, is_valid = await processor.run(en_input)
    assert "约翰·史密斯" in result
    assert "John Smith" not in result
    assert is_valid == 1


@pytest.mark.asyncio
async def test_famous_processor():
    """综合测试FamousProcessor类的核心功能"""
    # 初始化处理器实例
    processor = FamousLLMProcessor()

    # 测试1: 验证完整处理流程（成功场景）
    success_input = {"description": "李四研究员是国家杰出青年基金获得者，并主持了万人计划项目。"}
    _, normalized_famous, is_valid = await processor.run(success_input)
    assert isinstance(normalized_famous, str)
    normalized_famous = json.loads(normalized_famous)
    assert len(normalized_famous) == 2
    assert any("杰出青年基金" in item for item in normalized_famous)
    assert is_valid == True

    # 测试2: 验证完整处理流程（失败场景 - 无匹配职称）
    failure_input = {"description": "这是一段不包含著名人才职称信息的测试文本。"}
    _, normalized_famous, is_valid = await processor.run(failure_input)
    assert normalized_famous == "[]"
    assert is_valid == 0


@pytest.mark.asyncio
async def test_experience_processor():
    """综合测试FamousProcessor类的核心功能"""
    # 初始化处理器实例
    processor = ExperienceLLMProcessor()

    # 测试1: 验证完整处理流程（成功场景）
    success_input = {
        "description": "教育、工作经历：1997年09月 - 2001年06月，中南大学，应用化学专业，学士,2012年11月 - 现在，东莞理工学院化学工程与能源技术学院，副教授"
    }
    work_data, edu_data, is_valid = await processor.run(success_input)
    processor.logger.info(f"work_data: {work_data}")
    assert isinstance(work_data, str)
    assert is_valid == 1

    # 测试2: 验证完整处理流程（失败场景 - 无匹配职称）
    failure_input = {"description": "这是一段不包含著名人才职称信息的测试文本。"}
    work_data, edu_data, is_valid = await processor.run(failure_input)
    assert is_valid == 1


@pytest.mark.asyncio
async def test_teacher_disappear_llm_processor():
    """综合测试TeacherDisappearLLMProcessor类的核心功能"""
    processor = TeacherDisappearLLMProcessor()

    # 测试1: 判断主页归属（True/False场景）
    input_data = {
        "type": "homepage_match",
        "name": "张三",
        "profile": "张三，教授，研究方向为人工智能。现任中山大学教授。",
        "homepage_markdown": "# 张三\n中山大学教授，研究方向：人工智能。",
    }
    result, is_valid = await processor.process(input_data)
    assert result in ["True", "False"]
    assert is_valid is True

    # 测试2: 判断是否同一人（True/False场景）
    input_data = {
        "type": "is_same_teacher",
        "des1": "李四，清华大学教授，研究方向为计算机视觉。",
        "des2": "王五，北京大学教授，研究方向为生物信息学。",
    }
    result, is_valid = await processor.process(input_data)
    assert result in ["True", "False"]
    assert is_valid is True

    # 测试3: 提取工作经历（正常JSON数组场景）
    input_data = {
        "type": "work_experience",
        "name": "张三",
        "profile": "张三，教授，研究方向为人工智能。现任中山大学教授。",
        "homepage_markdowns": [
            "# 李四\n北京大学教授，研究方向：生物信息学。",
            "# 张三\n2010年9月-2015年7月：中山大学，讲师\n2015年8月-至今：中山大学，教授",
        ],
    }
    result, is_valid = await processor.process(input_data)
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)
    assert is_valid is True

    # 测试4: 错误输入（缺少必要字段）
    with pytest.raises(Exception):
        await processor.process({"foo": "bar"})
