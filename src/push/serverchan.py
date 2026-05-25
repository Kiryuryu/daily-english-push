"""Server酱推送模块"""

import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

SERVERCHAN_API_URL = 'https://sctapi.ftqq.com/{sendkey}.send'


class ServerChanPusher:
    def __init__(self):
        self.sendkey = os.environ.get('SERVERCHAN_SENDKEY')
        if not self.sendkey:
            raise ValueError("SERVERCHAN_SENDKEY environment variable not set")
    
    def push(self, title: str, content: str) -> bool:
        """推送消息到微信"""
        try:
            url = SERVERCHAN_API_URL.format(sendkey=self.sendkey)
            
            response = requests.post(
                url,
                data={
                    'title': title,
                    'desp': content
                },
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 0:
                logger.info(f"推送成功: {title}")
                return True
            else:
                logger.error(f"推送失败: {result}")
                return False
                
        except Exception as e:
            logger.exception(f"推送异常: {e}")
            return False
    
    def push_error(self, title: str, error_msg: str) -> bool:
        """推送错误消息"""
        content = f"""## 错误信息

{error_msg}

请检查日志获取详细信息。"""
        return self.push(title, content)
