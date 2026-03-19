"""ローカルデータベースでクエリを実行するコンポーネント"""

import sqlite3
import pandas as pd
from typing import Optional
from .exceptions import QueryExecutionError


class QueryExecutor:
    """ローカルデータベースでクエリを実行"""
    
    def __init__(self, db_path: str = "database.sqlite"):
        """
        データベース接続を初期化
        
        Parameters:
            db_path: SQLiteデータベースファイルパス
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        クエリを実行し、結果をDataFrameとして返す
        
        Parameters:
            query: 実行するSQLクエリ
        
        Returns:
            クエリ結果のDataFrame
        
        Raises:
            QueryExecutionError: データベース接続エラー、クエリ実行エラー
        """
        try:
            # データベースに接続
            if self.connection is None:
                self.connection = sqlite3.connect(self.db_path)
            
            # クエリを実行してDataFrameとして取得
            df = pd.read_sql_query(query, self.connection)
            
            return df
            
        except sqlite3.OperationalError as e:
            if "unable to open database file" in str(e).lower():
                raise QueryExecutionError(
                    f"データベースファイルが見つかりません: {self.db_path}"
                )
            else:
                raise QueryExecutionError(f"SQLエラー: {str(e)}")
        
        except sqlite3.DatabaseError as e:
            raise QueryExecutionError(f"データベース接続エラー: {str(e)}")
        
        except Exception as e:
            raise QueryExecutionError(f"クエリ実行エラー: {str(e)}")
    
    def close(self):
        """データベース接続を閉じる"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __enter__(self):
        """コンテキストマネージャーのエントリ"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャーの終了"""
        self.close()
