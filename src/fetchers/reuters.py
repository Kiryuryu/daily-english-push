"""Reuters 新闻抓取模块"""

import logging
import hashlib
import requests
import feedparser
from datetime import datetime
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

REUTERS_RSS_URLS = [
    'https://www.reutersagency.com/feed/',
    'https://news.google.com/rss/search?q=site:reuters.com&hl=en-US&gl=US&ceid=US:en',
]


class ReutersFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_latest(self) -> Optional[Dict]:
        """获取最新的Reuters新闻"""
        for rss_url in REUTERS_RSS_URLS:
            try:
                article = self._fetch_from_rss(rss_url)
                if article:
                    return article
            except Exception as e:
                logger.warning(f"从 {rss_url} 获取失败: {e}")
                continue
        
        logger.error("所有RSS源都失败")
        return None
    
    def _fetch_from_rss(self, rss_url: str) -> Optional[Dict]:
        """从RSS获取新闻"""
        try:
            response = self.session.get(rss_url, timeout=30)
            response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            
            for entry in feed.entries[:5]:
                title = entry.get('title', '')
                link = entry.get('link', '')
                summary = entry.get('summary', '') or entry.get('description', '')
                
                if not title or not link:
                    continue
                
                if 'reuters' not in link.lower():
                    continue
                
                content = self._fetch_article_content(link)
                
                article_id = hashlib.md5(link.encode()).hexdigest()[:12]
                
                return {
                    'id': article_id,
                    'title': title,
                    'url': link,
                    'description': summary,
                    'content': content or summary
                }
            
            return None
            
        except Exception as e:
            logger.exception(f"RSS解析失败: {e}")
            return None
    
    def _fetch_article_content(self, url: str) -> str:
        """获取文章正文"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content_parts = []
            
            for p in soup.select('article p, .article-body p, .story-content p'):
                text = p.get_text(strip=True)
                if text and len(text) > 30:
                    content_parts.append(text)
            
            return '\n\n'.join(content_parts[:8])
            
        except Exception as e:
            logger.warning(f"获取文章内容失败: {e}")
            return ''
