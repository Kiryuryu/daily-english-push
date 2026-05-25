"""BBC Learning English 抓取模块"""

import logging
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict

logger = logging.getLogger(__name__)

BBC_LEARNING_ENGLISH_URL = 'https://www.bbc.co.uk/learningenglish/english'


class BBCFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_latest(self) -> Optional[Dict]:
        """获取最新的BBC Learning English文章"""
        try:
            response = self.session.get(BBC_LEARNING_ENGLISH_URL, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = soup.select('.course-content-item')
            if not articles:
                articles = soup.select('article')
            if not articles:
                articles = soup.select('.text')
            
            for article in articles[:5]:
                link_elem = article.select_one('a')
                if not link_elem:
                    continue
                
                href = link_elem.get('href', '')
                if not href:
                    continue
                
                if not href.startswith('http'):
                    href = 'https://www.bbc.co.uk' + href
                
                title_elem = article.select_one('h3') or article.select_one('h2') or article.select_one('.title')
                title = title_elem.get_text(strip=True) if title_elem else 'Untitled'
                
                desc_elem = article.select_one('p') or article.select_one('.description')
                description = desc_elem.get_text(strip=True) if desc_elem else ''
                
                content = self._fetch_article_content(href)
                
                article_id = hashlib.md5(href.encode()).hexdigest()[:12]
                
                return {
                    'id': article_id,
                    'title': title,
                    'url': href,
                    'description': description,
                    'content': content
                }
            
            logger.error("未找到有效文章")
            return None
            
        except Exception as e:
            logger.exception(f"获取BBC文章失败: {e}")
            return None
    
    def _fetch_article_content(self, url: str) -> str:
        """获取文章正文"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content_parts = []
            
            for p in soup.select('article p, .story-body p, .text p'):
                text = p.get_text(strip=True)
                if text and len(text) > 20:
                    content_parts.append(text)
            
            return '\n\n'.join(content_parts[:10])
            
        except Exception as e:
            logger.warning(f"获取文章内容失败: {e}")
            return ''
