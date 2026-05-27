#!/usr/bin/env python3
"""每日英语新闻推送主程序"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from fetchers.bbc import BBCFetcher
from fetchers.reuters import ReutersFetcher
from llm.deepseek import DeepSeekClient
from push.serverchan import ServerChanPusher
from storage.local_store import LocalStore
from weekly.summary import WeeklySummary

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / 'data'


def run_bbc():
    """运行BBC早间推送"""
    logger.info("开始BBC早间推送任务")
    
    try:
        fetcher = BBCFetcher()
        llm = DeepSeekClient()
        pusher = ServerChanPusher()
        store = LocalStore(DATA_DIR / 'daily')
        
        # 检查今天是否已推送BBC
        if store.exists_today('bbc'):
            logger.info("今天已推送BBC文章，跳过")
            return True
        
        article = fetcher.fetch_latest()
        if not article:
            logger.error("未能获取BBC文章")
            pusher.push_error("BBC推送失败", "未能获取最新文章")
            return False
        
        content = llm.generate_bbc_content(article)
        if not content:
            logger.error("DeepSeek生成内容失败")
            pusher.push_error("BBC推送失败", "AI生成内容失败")
            return False
        
        today = datetime.now().strftime('%Y-%m-%d')
        success = pusher.push(
            title=f"BBC Learning English - {today}",
            content=content
        )
        
        if success:
            store.save_today('bbc', {
                'source': 'bbc',
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'content': content,
                'date': datetime.now().isoformat()
            })
            logger.info("BBC推送成功")
        else:
            logger.error("BBC推送失败")
            
        return success
        
    except Exception as e:
        logger.exception(f"BBC推送异常: {e}")
        return False


def run_reuters():
    """运行Reuters晚间推送"""
    logger.info("开始Reuters晚间推送任务")
    
    try:
        fetcher = ReutersFetcher()
        llm = DeepSeekClient()
        pusher = ServerChanPusher()
        store = LocalStore(DATA_DIR / 'daily')
        
        # 检查今天是否已推送Reuters
        if store.exists_today('reuters'):
            logger.info("今天已推送Reuters文章，跳过")
            return True
        
        article = fetcher.fetch_latest()
        if not article:
            logger.error("未能获取Reuters文章")
            pusher.push_error("Reuters推送失败", "未能获取最新新闻")
            return False
        
        content = llm.generate_reuters_content(article)
        if not content:
            logger.error("DeepSeek生成内容失败")
            pusher.push_error("Reuters推送失败", "AI生成内容失败")
            return False
        
        today = datetime.now().strftime('%Y-%m-%d')
        success = pusher.push(
            title=f"国际新闻英文阅读 - {today}",
            content=content
        )
        
        if success:
            store.save_today('reuters', {
                'source': 'reuters',
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'content': content,
                'date': datetime.now().isoformat()
            })
            logger.info("Reuters推送成功")
        else:
            logger.error("Reuters推送失败")
            
        return success
        
    except Exception as e:
        logger.exception(f"Reuters推送异常: {e}")
        return False


def run_weekly():
    """运行每周汇总"""
    logger.info("开始每周汇总任务")
    
    try:
        llm = DeepSeekClient()
        pusher = ServerChanPusher()
        store = LocalStore(DATA_DIR / 'daily')
        weekly_store = LocalStore(DATA_DIR / 'weekly')
        
        summary_gen = WeeklySummary(store, llm)
        content = summary_gen.generate()
        
        if not content:
            logger.error("生成周报失败")
            pusher.push_error("周报生成失败", "无法生成周报内容")
            return False
        
        week_num = datetime.now().isocalendar()[1]
        success = pusher.push(
            title=f"本周英语学习汇总 - 第{week_num}周",
            content=content
        )
        
        if success:
            weekly_store.save(f"week_{week_num}", {
                'content': content,
                'date': datetime.now().isoformat()
            })
            logger.info("周报推送成功")
        else:
            logger.error("周报推送失败")
            
        return success
        
    except Exception as e:
        logger.exception(f"周报推送异常: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='每日英语新闻推送')
    parser.add_argument('--task', choices=['bbc', 'reuters', 'weekly'], 
                        required=True, help='任务类型')
    args = parser.parse_args()
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / 'daily').mkdir(exist_ok=True)
    (DATA_DIR / 'weekly').mkdir(exist_ok=True)
    
    if args.task == 'bbc':
        success = run_bbc()
    elif args.task == 'reuters':
        success = run_reuters()
    elif args.task == 'weekly':
        success = run_weekly()
    else:
        logger.error(f"未知任务: {args.task}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()