"""每周汇总生成模块"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from storage.local_store import LocalStore
    from llm.deepseek import DeepSeekClient

logger = logging.getLogger(__name__)


class WeeklySummary:
    def __init__(self, store: 'LocalStore', llm: 'DeepSeekClient'):
        self.store = store
        self.llm = llm
    
    def generate(self) -> str:
        """生成每周汇总"""
        try:
            daily_data = self.store.get_recent(days=7)
            
            if not daily_data:
                logger.warning("没有本周数据")
                return self._generate_empty_summary()
            
            bbc_count = sum(1 for d in daily_data if d.get('source') == 'bbc')
            reuters_count = sum(1 for d in daily_data if d.get('source') == 'reuters')
            
            llm_content = self.llm.generate_weekly_summary(daily_data)
            
            if llm_content:
                return llm_content
            else:
                return self._generate_basic_summary(bbc_count, reuters_count, daily_data)
                
        except Exception as e:
            logger.exception(f"生成周报失败: {e}")
            return ""
    
    def _generate_empty_summary(self) -> str:
        """生成空周报"""
        week_num = datetime.now().isocalendar()[1]
        return f"""# 本周英语阅读复盘

## 本周阅读数量
第{week_num}周暂无学习记录

## 下周建议
开始你的每日英语学习之旅吧！"""
    
    def _generate_basic_summary(self, bbc_count: int, reuters_count: int, daily_data: list) -> str:
        """生成基础周报"""
        week_num = datetime.now().isocalendar()[1]
        
        titles = [d.get('title', '') for d in daily_data if d.get('title')]
        
        return f"""# 本周英语阅读复盘

## 本周阅读数量
- BBC Learning English: {bbc_count} 篇
- Reuters 新闻: {reuters_count} 篇
- 总计: {bbc_count + reuters_count} 篇

## 本周阅读文章
{chr(10).join(f'- {t}' for t in titles[:10])}

## 下周建议
继续保持每日学习习惯，建议每天至少阅读一篇英文文章。"""
