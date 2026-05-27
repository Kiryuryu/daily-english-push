"""Reuters 新闻抓取模块"""

import logging
import hashlib
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

REUTERS_RSS_URLS = [
    'https://news.google.com/rss/search?q=site:reuters.com&hl=en-US&gl=US&ceid=US:en',
    'https://feeds.npr.org/1004/rss.xml',
    'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
]


class ReutersFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    def fetch_latest(self) -> Optional[Dict]:
        """获取最新的国际新闻"""
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
            
            for entry in feed.entries[:10]:
                title = entry.get('title', '')
                link = entry.get('link', '')
                summary = entry.get('summary', '') or entry.get('description', '')
                
                if not title or not link:
                    continue
                
                content = self._fetch_article_content(link)
                
                article_id = hashlib.md5(link.encode()).hexdigest()[:12]
                
                source = 'Reuters'
                if 'nytimes' in link.lower() or 'nyt' in rss_url.lower():
                    source = 'NYTimes'
                elif 'npr' in link.lower():
                    source = 'NPR'
                elif 'reuters' in link.lower():
                    source = 'Reuters'
                
                return {
                    'id': article_id,
                    'title': title,
                    'url': link,
                    'description': summary,
                    'content': content or summary,
                    'source': source
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
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content_parts = []
            
            for p in soup.select('article p, .article-body p, .story-content p, p'):
                text = p.get_text(strip=True)
                if text and len(text) > 30 and not any(skip in text.lower() for skip in ['copyright', 'subscribe', 'advertisement', 'related']):
                    content_parts.append(text)
            
            return '\n\n'.join(content_parts[:10])
            
        except Exception as e:
            logger.warning(f"获取文章内容失败: {e}")
            return ''