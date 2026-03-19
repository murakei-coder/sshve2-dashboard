"""
Unit tests for CSVLoader class
"""

import pytest
import pandas as pd
import tempfile
import os
from src.sourcing_aggregator import CSVLoader


class TestCSVLoader:
    """CSVLoader クラスのユニットテスト"""
    
    def test_load_utf8_file(self):
        """UTF-8エンコーディングのCSVファイルを正常に読み込めることを確認"""
        # テスト用のCSVファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False) as f:
            f.write('mcid,total_t30d_gms_BAU,SSHVE2_SourcedFlag\n')
            f.write('MC001,1000.50,Y\n')
            f.write('MC002,2000.75,N\n')
            temp_file = f.name
        
        try:
            loader = CSVLoader()
            df = loader.load(temp_file)
            
            # DataFrameが正しく読み込まれたことを確認
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
            assert list(df.columns) == ['mcid', 'total_t30d_gms_BAU', 'SSHVE2_SourcedFlag']
            assert df.iloc[0]['mcid'] == 'MC001'
            assert df.iloc[0]['total_t30d_gms_BAU'] == 1000.50
            assert df.iloc[0]['SSHVE2_SourcedFlag'] == 'Y'
        finally:
            os.unlink(temp_file)
    
    def test_load_cp932_file(self):
        """cp932エンコーディングのCSVファイルをフォールバックで読み込めることを確認"""
        # テスト用のcp932エンコーディングのCSVファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', encoding='cp932', suffix='.csv', delete=False) as f:
            f.write('mcid,total_t30d_gms_BAU,SSHVE2_SourcedFlag\n')
            f.write('MC001,1000.50,Y\n')
            f.write('MC002,2000.75,N\n')
            temp_file = f.name
        
        try:
            loader = CSVLoader()
            df = loader.load(temp_file)
            
            # DataFrameが正しく読み込まれたことを確認
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
            assert list(df.columns) == ['mcid', 'total_t30d_gms_BAU', 'SSHVE2_SourcedFlag']
        finally:
            os.unlink(temp_file)
    
    def test_file_not_found(self):
        """存在しないファイルを指定した場合にFileNotFoundErrorが発生することを確認"""
        loader = CSVLoader()
        
        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load('nonexistent_file.csv')
        
        assert 'ファイルが見つかりません' in str(exc_info.value)
    
    def test_load_with_japanese_content(self):
        """日本語を含むCSVファイルを正常に読み込めることを確認"""
        # テスト用のUTF-8エンコーディングで日本語を含むCSVファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False) as f:
            f.write('mcid,total_t30d_gms_BAU,SSHVE2_SourcedFlag\n')
            f.write('カテゴリ001,1000.50,Y\n')
            f.write('カテゴリ002,2000.75,N\n')
            temp_file = f.name
        
        try:
            loader = CSVLoader()
            df = loader.load(temp_file)
            
            # DataFrameが正しく読み込まれたことを確認
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
            assert df.iloc[0]['mcid'] == 'カテゴリ001'
        finally:
            os.unlink(temp_file)
