"""DeepSeek API 客户端"""

import os
import logging
import requests
from typing import Optional, Dict

logger = logging.getLogger(__name__)

DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'


class DeepSeekClient:
    def __init__(self):
        self.api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")
    
    def _call_api(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """调用DeepSeek API"""
        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': user_prompt}
                    ],
                    'temperature': 0.7,
                    'max_tokens': 2000
                },
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except Exception as e:
            logger.exception(f"DeepSeek API调用失败: {e}")
            return None
    
    def generate_bbc_content(self, article: Dict) -> Optional[str]:
        """生成BBC学习内容"""
        system_prompt = """你是一个专业的英语学习内容编辑。请根据给定的BBC Learning English文章，生成适合中国学生学习的内容。

输出格式要求（Markdown格式）：

# BBC Learning English 今日阅读

## 一句话概括
[用中文概括文章主题，1-2句话]

## English Summary
[80-120词的英文摘要]

## 今日重点词汇
列出5个重点词汇，每个词汇包含：
- **单词**：中文释义
  - 语境含义：在本文中的具体含义
  - 例句：原文中的句子
  - 搭配：常见搭配用法

## 今日小练习
3道选择题，格式如下：
1. 题目
   A. 选项A
   B. 选项B
   C. 选项C
   D. 选项D
   
   答案：X"""
        
        user_prompt = f"""请根据以下文章生成英语学习内容：

标题：{article.get('title', '')}
链接：{article.get('url', '')}
内容：
{article.get('content', '')[:2000]}"""
        
        return self._call_api(system_prompt, user_prompt)
    
    def generate_reuters_content(self, article: Dict) -> Optional[str]:
        """生成Reuters新闻学习内容"""
        system_prompt = """你是一个专业的英语新闻学习编辑。请根据给定的Reuters新闻，生成适合中国学生阅读学习的内容。

输出格式要求（Markdown格式）：

# Reuters 晚间英文新闻

## 今日新闻
[标题]
原文链接：[URL]

## 中文背景
[用中文解释新闻发生了什么，背景信息，约100-150字]

## English Summary
[100-150词的英文摘要]

## 高价值表达
列出5个新闻英语常用表达，每个包含：
- **表达**：中文释义
  - 使用场景

## 适合背的句子
摘取或改写2个新闻英语表达，适合背诵的句子。"""
        
        user_prompt = f"""请根据以下新闻生成学习内容：

标题：{article.get('title', '')}
链接：{article.get('url', '')}
内容：
{article.get('content', '')[:2000]}"""
        
        return self._call_api(system_prompt, user_prompt)
    
    def generate_weekly_summary(self, daily_data: list) -> Optional[str]:
        """生成每周汇总"""
        system_prompt = """你是一个专业的英语学习顾问。请根据本周的学习内容，生成周报。

输出格式要求（Markdown格式）：

# 本周英语阅读复盘

## 本周阅读数量
BBC X篇，Reuters X篇

## 本周高频主题
[列出本周涉及的主要主题，如AI、经济、健康、地缘政治等]

## 本周重点词汇 Top 20
按出现频率和实用性排序，列出20个词汇，格式：
1. **单词** - 中文释义

## 本周最值得复习的 5 个表达
[列出5个最值得复习的表达，每个包含例句]

## 下周建议
[给出下周学习建议]"""
        
        content_list = []
        for item in daily_data:
            content_list.append(f"来源: {item.get('source', '')}\n标题: {item.get('title', '')}")
        
        user_prompt = f"""请根据本周的学习内容生成周报：

{chr(10).join(content_list)}"""
        
        return self._call_api(system_prompt, user_prompt)
