"""クエリ内の日付を置換するコンポーネント"""

import re
from datetime import datetime
from .exceptions import DataValidationError


class DateReplacer:
    """クエリ内の日付を置換"""
    
    DATE_PATTERN = r'\d{4}-\d{2}-\d{2}'
    
    def replace_dates(self, query: str, target_date: str, 
                     start_line: int = 6, end_line: int = 11) -> str:
        """
        クエリの指定行範囲内の日付を置換
        
        Parameters:
            query: 元のクエリテキスト
            target_date: 置換する日付（'yyyy-mm-dd'形式）
            start_line: 開始行（1-indexed）
            end_line: 終了行（1-indexed）
        
        Returns:
            日付が置換されたクエリテキスト
        
        Raises:
            DataValidationError: 日付形式が不正な場合
        """
        # 日付形式を検証
        if not self.validate_date_format(target_date):
            raise DataValidationError(
                f"日付形式が不正です: {target_date}。'yyyy-mm-dd'形式で指定してください（例: 2026-02-02）"
            )
        
        # クエリを行に分割
        lines = query.split('\n')
        
        # 指定範囲の行の日付を置換（1-indexedを0-indexedに変換）
        start_idx = start_line - 1
        end_idx = end_line
        
        for i in range(start_idx, min(end_idx, len(lines))):
            # この行に日付パターンがあれば置換
            lines[i] = re.sub(self.DATE_PATTERN, target_date, lines[i])
        
        return '\n'.join(lines)
    
    def validate_date_format(self, date_str: str) -> bool:
        """
        日付形式を検証
        
        Parameters:
            date_str: 検証する日付文字列
        
        Returns:
            True if valid, False otherwise
        """
        if not date_str or not isinstance(date_str, str):
            return False
        
        # 正規表現で形式チェック
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return False
        
        # 実際の日付として有効かチェック
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
