"""DataCentralからSQLクエリを取得するコンポーネント"""

import os
import requests
from typing import Optional, Dict
from .exceptions import DataCentralError


class QueryFetcher:
    """DataCentral URLからクエリを取得"""
    
    def __init__(self, auth_config: Optional[Dict[str, str]] = None):
        """
        認証設定を初期化
        
        Parameters:
            auth_config: 認証情報の辞書（環境変数から読み込み）
        """
        self.auth_config = auth_config or self._load_auth_from_env()
    
    def _load_auth_from_env(self) -> Dict[str, str]:
        """環境変数から認証情報を読み込む"""
        auth = {}
        if os.getenv('DATACENTRAL_USERNAME'):
            auth['username'] = os.getenv('DATACENTRAL_USERNAME')
        if os.getenv('DATACENTRAL_PASSWORD'):
            auth['password'] = os.getenv('DATACENTRAL_PASSWORD')
        if os.getenv('DATACENTRAL_TOKEN'):
            auth['token'] = os.getenv('DATACENTRAL_TOKEN')
        return auth
    
    def fetch_query(self, url: str) -> str:
        """
        DataCentral URLからクエリを取得
        
        Parameters:
            url: DataCentral URL
        
        Returns:
            クエリテキスト
        
        Raises:
            DataCentralError: 接続失敗、認証失敗、無効URL時
        """
        if not url or not isinstance(url, str):
            raise DataCentralError(f"無効なURL: {url}")
        
        if not url.startswith('https://'):
            raise DataCentralError(f"HTTPSを使用してください: {url}")
        
        try:
            # 認証情報を準備
            headers = {}
            auth = None
            
            if 'token' in self.auth_config:
                headers['Authorization'] = f"Bearer {self.auth_config['token']}"
            elif 'username' in self.auth_config and 'password' in self.auth_config:
                auth = (self.auth_config['username'], self.auth_config['password'])
            
            # HTTPSでリクエスト
            response = requests.get(url, headers=headers, auth=auth, timeout=30)
            
            # ステータスコードチェック
            if response.status_code == 401:
                raise DataCentralError(
                    "認証に失敗しました。環境変数DATACENTRAL_USERNAMEとDATACENTRAL_PASSWORD、"
                    "またはDATACENTRAL_TOKENを設定してください。"
                )
            elif response.status_code == 404:
                raise DataCentralError(f"URLが見つかりません: {url}")
            elif response.status_code != 200:
                raise DataCentralError(
                    f"DataCentralへの接続に失敗しました。ステータスコード: {response.status_code}"
                )
            
            # クエリテキストを抽出（実際のDataCentralのHTMLパース処理が必要）
            query_text = self._extract_query_from_response(response.text)
            
            if not query_text:
                raise DataCentralError("クエリテキストが見つかりませんでした")
            
            return query_text
            
        except requests.exceptions.ConnectionError as e:
            raise DataCentralError(f"DataCentralへの接続に失敗しました: {str(e)}")
        except requests.exceptions.Timeout as e:
            raise DataCentralError(f"接続がタイムアウトしました: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise DataCentralError(f"リクエストエラー: {str(e)}")
    
    def _extract_query_from_response(self, html_content: str) -> str:
        """
        HTMLレスポンスからクエリテキストを抽出
        
        Parameters:
            html_content: HTMLコンテンツ
        
        Returns:
            抽出されたクエリテキスト
        """
        # 簡易実装: 実際のDataCentralのHTML構造に応じて調整が必要
        # ここでは<pre>タグや<textarea>タグ内のSQLを探す
        import re
        
        # <pre>タグ内のSQLを探す
        pre_match = re.search(r'<pre[^>]*>(.*?)</pre>', html_content, re.DOTALL | re.IGNORECASE)
        if pre_match:
            return pre_match.group(1).strip()
        
        # <textarea>タグ内のSQLを探す
        textarea_match = re.search(r'<textarea[^>]*>(.*?)</textarea>', html_content, re.DOTALL | re.IGNORECASE)
        if textarea_match:
            return textarea_match.group(1).strip()
        
        # SQLキーワードで始まる行を探す
        lines = html_content.split('\n')
        sql_keywords = ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE', 'CREATE']
        for i, line in enumerate(lines):
            stripped = line.strip()
            if any(stripped.upper().startswith(kw) for kw in sql_keywords):
                # この行から始まるSQLブロックを抽出
                sql_lines = []
                for j in range(i, len(lines)):
                    sql_lines.append(lines[j])
                    # セミコロンで終わる場合は終了
                    if lines[j].strip().endswith(';'):
                        break
                return '\n'.join(sql_lines)
        
        return ""
