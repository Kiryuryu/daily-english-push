"""BBC Learning English 抓取模块"""

import logging
import hashlib
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

BBC_LEARNING_ENGLISH_URL = 'https://www.bbc.co.uk/learningenglish/english'
BBC_RSS_URLS = [
    'https://www.bbc.co.uk/learningenglish/english/features/6-minute-english',
    'https://www.bbc.co.uk/learningenglish/english/features/english-at-work',
    'https://www.bbc.co.uk/learningenglish/english/features/the-english-we-speak',
]


class BBCFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    def fetch_latest(self) -> Optional[Dict]:
        """获取最新的BBC Learning English文章"""
        for url in BBC_RSS_URLS:
            try:
                article = self._fetch_from_page(url)
                if article:
                    return article
            except Exception as e:
                logger.warning(f"从 {url} 获取失败: {e}")
                continue
        
        try:
            article = self._fetch_from_main_page()
            if article:
                return article
        except Exception as e:
            logger.warning(f"从主页获取失败: {e}")
        
        logger.error("所有BBC源都失败")
        return None
    
    def _fetch_from_page(self, url: str) -> Optional[Dict]:
        """从特定页面获取文章"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = soup.select('.course-content-item') or soup.select('.text') or soup.select('article')
            
            for article_elem in articles[:3]:
                link_elem = article_elem.select_one('a')
                if not link_elem:
                    continue
                
                href = link_elem.get('href', '')
                if not href:
                    continue
                
                if not href.startswith('http'):
                    href = 'https://www.bbc.co.uk' + href
                
                title_elem = article_elem.select_one('h3') or article_elem.select_one('h2') or link_elem
                title = title_elem.get_text(strip=True) if title_elem else 'Untitled'
                
                if not title or title == 'Untitled':
                    title = href.split('/')[-1].replace('-', ' ').title()
                
                content = self._fetch_article_content(href)
                
                article_id = hashlib.md5(href.encode()).hexdigest()[:12]
                
                return {
                    'id': article_id,
                    'title': title,
                    'url': href,
                    'description': '',
                    'content': content
                }
            
            return None
            
        except Exception as e:
            logger.exception(f"页面解析失败: {e}")
            return None
    
    def _fetch_from_main_page(self) -> Optional[Dict]:
        """从主页获取文章"""
        try:
            response = self.session.get(BBC_LEARNING_ENGLISH_URL, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links = soup.select('a[href*="/learningenglish/english/"]')
            
            for link in links[:10]:
                href = link.get('href', '')
                if not href or 'features' not in href:
                    continue
                
                if not href.startswith('http'):
                    href = 'https://www.bbc.co.uk' + href
                
                title = link.get_text(strip=True)
                if not title:
                    continue
                
                content = self._fetch_article_content(href)
                
                article_id = hashlib.md5(href.encode()).hexdigest()[:12]
                
                return {
                    'id': article_id,
                    'title': title,
                    'url': href,
                    'description': '',
                    'content': content
                }
            
            return None
            
        except Exception as e:
            logger.exception(f"主页解析失败: {e}")
            return None
    
    def _fetch_article_content(self, url: str) -> str:
        """获取文章正文"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content_parts = []
            
            for p in soup.select('p'):
                text = p.get_text(strip=True)
                if text and len(text) > 20 and not any(skip in text.lower() for skip in ['copyright', 'bbc', 'related']):
                    content_parts.append(text)
            
            return '\n\n'.join(content_parts[:15])
            
        except Exception as e:
            logger.warning(f"获取文章内容失败: {e}")
            return ''