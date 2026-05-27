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
                    'max_tokens': 3000
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
        """生成BBC学习内容 - 包含原文"""
        system_prompt = """你是一个专业的英语学习内容编辑。请根据给定的BBC Learning English文章，生成适合中国学生学习的内容。

输出格式要求（Markdown格式）：

# BBC Learning English 今日阅读

## 文章标题
[文章标题]

## 原文内容
[完整展示原文内容，保留英文原文，段落分明]

## 高频词汇学习
从文章中提取8-10个高频/重点词汇，每个词汇包含：
- **单词** [音标]
  - 词性：n./v./adj.等
  - 中文释义
  - 原文例句：引用原文中的句子
  - 搭配用法：常见搭配

## 阅读理解练习
设计3-5道阅读理解选择题，考查对文章内容的理解：
1. 题目
   A. 选项A
   B. 选项B
   C. 选项C
   D. 选项D
   
   答案：X

## 今日学习要点
总结本文的语法要点、表达技巧或文化背景知识。"""
        
        user_prompt = f"""请根据以下BBC Learning English文章生成完整的学习内容：

标题：{article.get('title', '')}
链接：{article.get('url', '')}

原文内容：
{article.get('content', '')}

请完整保留原文内容，并从中提取高频词汇和设计阅读练习。"""
        
        return self._call_api(system_prompt, user_prompt)
    
    def generate_reuters_content(self, article: Dict) -> Optional[str]:
        """生成Reuters新闻学习内容 - 包含原文"""
        system_prompt = """你是一个专业的英语新闻学习编辑。请根据给定的国际新闻，生成适合中国学生阅读学习的内容。

输出格式要求（Markdown格式）：

# 国际新闻英文阅读

## 新闻标题
[原标题]

## 新闻背景
[用中文简要解释新闻背景，发生了什么，涉及哪些国家/人物/事件，约100字]

## 英文原文
[完整展示新闻原文内容，保留英文]

## 高频词汇学习
从新闻中提取8-10个新闻高频词汇，每个包含：
- **单词** [音标]
  - 词性
  - 中文释义
  - 原文例句
  - 新闻语境用法

## 重点表达解析
提取3-5个新闻英语常用表达：
- **表达**
  - 含义
  - 使用场景
  - 例句

## 阅读理解练习
设计3道选择题考查理解：
1. 题目
   A. 选项
   B. 选项
   C. 选项
   
   答案：X"""
        
        user_prompt = f"""请根据以下国际新闻生成学习内容：

标题：{article.get('title', '')}
链接：{article.get('url', '')}
来源：{article.get('source', 'Reuters')}

原文内容：
{article.get('content', '')}

请完整保留原文，提取高频词汇和新闻表达，设计阅读练习。"""
        
        return self._call_api(system_prompt, user_prompt)
    
    def generate_weekly_summary(self, daily_data: list) -> Optional[str]:
        """生成每周汇总"""
        system_prompt = """你是一个专业的英语学习顾问。请根据本周的学习内容，生成周报。

输出格式要求（Markdown格式）：

# 本周英语阅读复盘

## 本周阅读统计
- BBC Learning English: X 篇
- 国际新闻: X 篇
- 总阅读量: 约 X 词

## 本周高频词汇 Top 20
按出现频率排序，列出20个本周学过的重点词汇：
1. **单词** - 中文释义 - 出现次数

## 本周重点表达回顾
回顾本周学过的5个最值得记住的表达：
- **表达**
  - 含义
  - 例句

## 本周阅读主题
总结本周阅读涉及的主要主题和话题。

## 下周学习建议
根据本周内容给出具体的学习建议。"""
        
        content_list = []
        for item in daily_data:
            source = item.get('source', 'unknown')
            title = item.get('title', '')
            content_list.append(f"- [{source}] {title}")
        
        user_prompt = f"""请根据本周的学习内容生成周报：

本周阅读文章：
{chr(10).join(content_list)}

请汇总本周的词汇、表达和学习要点。"""
        
        return self._call_api(system_prompt, user_prompt)