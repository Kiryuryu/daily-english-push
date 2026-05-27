"""本地存储模块"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class LocalStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, key: str) -> Path:
        return self.data_dir / f"{key}.json"
    
    def exists(self, key: str) -> bool:
        """检查记录是否存在"""
        return self._get_file_path(key).exists()
    
    def exists_today(self, source: str) -> bool:
        """检查今天是否已推送该来源的文章"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_file = self.data_dir / f"{source}_{today}.json"
        return today_file.exists()
    
    def save(self, key: str, data: Dict) -> bool:
        """保存记录"""
        try:
            file_path = self._get_file_path(key)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"保存成功: {key}")
            return True
        except Exception as e:
            logger.exception(f"保存失败: {e}")
            return False
    
    def save_today(self, source: str, data: Dict) -> bool:
        """保存今日推送记录"""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"{source}_{today}"
        return self.save(key, data)
    
    def load(self, key: str) -> Optional[Dict]:
        """加载记录"""
        try:
            file_path = self._get_file_path(key)
            if not file_path.exists():
                return None
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.exception(f"加载失败: {e}")
            return None
    
    def get_recent(self, days: int = 7) -> List[Dict]:
        """获取最近N天的记录"""
        results = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for file_path in self.data_dir.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                date_str = data.get('date', '')
                if date_str:
                    record_date = datetime.fromisoformat(date_str)
                    if record_date >= cutoff:
                        results.append(data)
            except Exception as e:
                logger.warning(f"读取文件失败 {file_path}: {e}")
                continue
        
        return sorted(results, key=lambda x: x.get('date', ''), reverse=True)
    
    def list_all(self) -> List[str]:
        """列出所有记录的key"""
        return [p.stem for p in self.data_dir.glob('*.json')]