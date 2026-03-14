"""Prompt templates for AI writing."""

# System prompt for chapter generation
SYSTEM_PROMPT = """你是一位专业的网络小说作家，擅长创作玄幻、仙侠、都市等类型的长篇小说。
你的文笔流畅，情节跌宕起伏，人物塑造鲜明。
请根据用户提供的上下文信息，生成高质量的章节内容。"""

# Context assembly prompt
CONTEXT_ASSEMBLY_PROMPT = """请根据以下信息组装写作上下文：

## 永久设定层（世界观、主角设定、文风要求）
{world_setting}

## 大纲导航层（当前卷目标 + 前后各3章摘要）
{outline_context}

## 人物状态层（所有出场人物当前状态）
{character_context}

## 关键事件层（与本章相关的历史重要节点）
{event_context}

## 近期原文层（最近3章完整原文）
{recent_content}

请基于以上上下文，创作下一章内容。"""

# Chapter generation prompt
CHAPTER_GENERATION_PROMPT = """## 本章写作目标
{chapter_goal}

## 情绪基调
{emotional_tone}

## 结尾钩子
{ending_hook}

## 重要事件触发
{special_events}

## 生成要求
- 字数：{target_words}字左右
- 对话比例：{dialogue_ratio}%
- 节奏：{pace}

请开始创作本章内容："""

# Chapter summary prompt
CHAPTER_SUMMARY_PROMPT = """请用约100字概括以下章节的核心内容：
{chapter_content}

要求：
- 保留关键情节
- 包含主要人物
- 指出重要发展"""

# Character status extraction prompt
CHARACTER_EXTRACTION_PROMPT = """从以下章节内容中提取人物状态变化：
{chapter_content}

请以JSON格式输出人物变化信息：
{{
    "character_name": {{
        "status_changed": true/false,
        "location_change": "新位置或null",
        "realm_change": "新境界或null",
        "equipment_changes": ["获得/失去的物品"],
        "relationship_changes": ["关系变化"]
    }}
}}"""

# Consistency check prompt
CONSISTENCY_CHECK_PROMPT = """请检查以下章节内容与设定的一致性：

## 世界观设定
{world_setting}

## 人物状态
{character_status}

## 章节内容
{chapter_content}

请检查以下方面：
1. 已死角色是否复活（逻辑错误）
2. 人物当前境界/装备是否与状态表一致
3. 地理位置是否合理
4. 时间线是否矛盾

请以JSON格式输出检查结果：
{{
    "issues": [
        {{
            "type": "类型",
            "description": "问题描述",
            "severity": "high/medium/low"
        }}
    ]
}}"""

# Style check prompt
STYLE_CHECK_PROMPT = """请检查以下章节的文风质量：

## 期望文风
{style_requirement}

## 章节内容
{chapter_content}

请检查以下方面：
1. 句式重复度（检测AI机械感）
2. 爽点密度分析
3. 情感曲线检测
4. 与设定文风的符合度

请以JSON格式输出检查结果：
{{
    "issues": [
        {{
            "type": "类型",
            "description": "问题描述",
            "severity": "high/medium/low"
        }},
        {{
            "type": "repetition",
            "repetition_ratio": 0.0-1.0
        }},
        {{
            "type": "style_match",
            "match_score": 0.0-1.0
        }}
    ]
}}"""

# Quality check prompt
QUALITY_CHECK_PROMPT = """请检查以下章节的质量：

## 章节内容
{chapter_content}

请检查以下方面：
1. 字数是否达到1800字
2. 生成8个候选标题（悬念型/爽点型/数字型）
3. 结尾是否有钩子
4. 开头是否吸引人

请以JSON格式输出检查结果：
{{
    "word_count": 数字,
    "titles": {{
        "suspense": ["标题1", "标题2", "标题3"],
        "爽点": ["标题1", "标题2", "标题3"],
        "数字": ["标题1", "标题2", "标题3"]
    }},
    "has_ending_hook": true/false,
    "is_good_start": true/false,
    "suggestions": ["建议1", "建议2"]
}}"""

# Memory update prompt
MEMORY_UPDATE_PROMPT = """请分析以下章节，提取需要记忆的关键信息：

## 章节内容
{chapter_content}

## 当前章节号
{chapter_number}

请提取：
1. 本章摘要（100字）
2. 人物状态变化
3. 关键事件（如有）
4. 埋下的伏笔（如有）

请以JSON格式输出：
{{
    "summary": "本章摘要",
    "character_updates": [
        {{
            "name": "人物名",
            "changes": ["变化1", "变化2"]
        }}
    ],
    "new_events": [
        {{
            "name": "事件名",
            "description": "事件描述"
        }}
    ],
    "foreshadowings": [
        {{
            "content": "伏笔内容",
            "type": "类型"
        }}
    ]
}}"""
