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


def get_push_count(store: LocalStore, source: str) -> int:
    """获取今天已推送的次数"""
    today = datetime.now().strftime('%Y-%m-%d')
    count = 0
    for key in store.list_all():
        if key.startswith(f"{source}_{today}"):
            count += 1
    return count


def run_bbc(force: bool = False):
    """运行BBC早间推送"""
    logger.info("开始BBC早间推送任务")
    
    try:
        fetcher = BBCFetcher()
        llm = DeepSeekClient()
        pusher = ServerChanPusher()
        store = LocalStore(DATA_DIR / 'daily')
        
        # 检查今天是否已推送BBC（除非强制推送）
        if not force and store.exists_today('bbc'):
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
        push_count = get_push_count(store, 'bbc')
        
        # 标题添加日期和序号
        title_suffix = ""
        if push_count > 0:
            title_suffix = f" ({push_count + 1})"
        
        success = pusher.push(
            title=f"BBC Learning English - {today}{title_suffix}",
            content=content
        )
        
        if success:
            # 保存时也加上序号
            save_key = f"bbc_{today}"
            if push_count > 0:
                save_key = f"bbc_{today}_{push_count + 1}"
            
            store.save(save_key, {
                'source': 'bbc',
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'content': content,
                'date': datetime.now().isoformat(),
                'push_count': push_count + 1
            })
            logger.info("BBC推送成功")
        else:
            logger.error("BBC推送失败")
            
        return success
        
    except Exception as e:
        logger.exception(f"BBC推送异常: {e}")
        return False


def run_reuters(force: bool = False):
    """运行Reuters晚间推送"""
    logger.info("开始Reuters晚间推送任务")
    
    try:
        fetcher = ReutersFetcher()
        llm = DeepSeekClient()
        pusher = ServerChanPusher()
        store = LocalStore(DATA_DIR / 'daily')
        
        # 检查今天是否已推送Reuters（除非强制推送）
        if not force and store.exists_today('reuters'):
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
        push_count = get_push_count(store, 'reuters')
        
        # 标题添加日期和序号
        title_suffix = ""
        if push_count > 0:
            title_suffix = f" ({push_count + 1})"
        
        success = pusher.push(
            title=f"国际新闻英文阅读 - {today}{title_suffix}",
            content=content
        )
        
        if success:
            # 保存时也加上序号
            save_key = f"reuters_{today}"
            if push_count > 0:
                save_key = f"reuters_{today}_{push_count + 1}"
            
            store.save(save_key, {
                'source': 'reuters',
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'content': content,
                'date': datetime.now().isoformat(),
                'push_count': push_count + 1
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
        today = datetime.now().strftime('%Y-%m-%d')
        success = pusher.push(
            title=f"本周英语学习汇总 - 第{week_num}周 ({today})",
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
    parser.add_argument('--force', action='store_true',
                        help='强制推送，跳过去重检查')
    args = parser.parse_args()
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / 'daily').mkdir(exist_ok=True)
    (DATA_DIR / 'weekly').mkdir(exist_ok=True)
    
    if args.task == 'bbc':
        success = run_bbc(force=args.force)
    elif args.task == 'reuters':
        success = run_reuters(force=args.force)
    elif args.task == 'weekly':
        success = run_weekly()
    else:
        logger.error(f"未知任务: {args.task}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()