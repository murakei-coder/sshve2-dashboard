"""
Unit tests for MCIDAggregator class
"""

import pandas as pd
import pytest
from src.sourcing_aggregator import MCIDAggregator, AggregatedResult


class TestMCIDAggregator:
    """MCIDAggregatorのユニットテスト"""
    
    def test_aggregate_single_mcid(self):
        """単一MCIDの集約テスト"""
        # テストデータ作成
        df = pd.DataFrame({
            'mcid': ['MCID001', 'MCID001', 'MCID001'],
            'total_t30d_gms_BAU': [100.0, 200.0, 300.0],
            'SSHVE2_SourcedFlag': ['Y', 'Y', 'N']
        })
        
        aggregator = MCIDAggregator()
        results = aggregator.aggregate(df)
        
        assert len(results) == 1
        assert results[0].mcid == 'MCID001'
        assert results[0].total_gms == 600.0
        assert results[0].sourced_gms == 300.0
        assert results[0].sourced_gms_percent == 50.0
    
    def test_aggregate_multiple_mcids(self):
        """複数MCIDの集約テスト"""
        df = pd.DataFrame({
            'mcid': ['MCID001', 'MCID001', 'MCID002', 'MCID002'],
            'total_t30d_gms_BAU': [100.0, 200.0, 150.0, 250.0],
            'SSHVE2_SourcedFlag': ['Y', 'N', 'Y', 'Y']
        })
        
        aggregator = MCIDAggregator()
        results = aggregator.aggregate(df)
        
        assert len(results) == 2
        
        # MCID001の検証
        mcid001 = [r for r in results if r.mcid == 'MCID001'][0]
        assert mcid001.total_gms == 300.0
        assert mcid001.sourced_gms == 100.0
        assert abs(mcid001.sourced_gms_percent - 33.33) < 0.01
        
        # MCID002の検証
        mcid002 = [r for r in results if r.mcid == 'MCID002'][0]
        assert mcid002.total_gms == 400.0
        assert mcid002.sourced_gms == 400.0
        assert mcid002.sourced_gms_percent == 100.0
    
    def test_aggregate_zero_total_gms(self):
        """Total GMSが0の場合のテスト（ゼロ除算対応）"""
        df = pd.DataFrame({
            'mcid': ['MCID001'],
            'total_t30d_gms_BAU': [0.0],
            'SSHVE2_SourcedFlag': ['Y']
        })
        
        aggregator = MCIDAggregator()
        results = aggregator.aggregate(df)
        
        assert len(results) == 1
        assert results[0].total_gms == 0.0
        assert results[0].sourced_gms == 0.0
        assert results[0].sourced_gms_percent == 0.0
    
    def test_aggregate_no_sourced_items(self):
        """Sourcedアイテムが無い場合のテスト"""
        df = pd.DataFrame({
            'mcid': ['MCID001', 'MCID001'],
            'total_t30d_gms_BAU': [100.0, 200.0],
            'SSHVE2_SourcedFlag': ['N', 'N']
        })
        
        aggregator = MCIDAggregator()
        results = aggregator.aggregate(df)
        
        assert len(results) == 1
        assert results[0].total_gms == 300.0
        assert results[0].sourced_gms == 0.0
        assert results[0].sourced_gms_percent == 0.0
    
    def test_calculate_sourced_gms(self):
        """_calculate_sourced_gms ヘルパーメソッドのテスト"""
        df = pd.DataFrame({
            'mcid': ['MCID001', 'MCID001', 'MCID001'],
            'total_t30d_gms_BAU': [100.0, 200.0, 300.0],
            'SSHVE2_SourcedFlag': ['Y', 'Y', 'N']
        })
        
        aggregator = MCIDAggregator()
        sourced_gms = aggregator._calculate_sourced_gms(df)
        
        assert sourced_gms == 300.0
    
    def test_calculate_percentage_normal(self):
        """_calculate_percentage ヘルパーメソッドの通常ケーステスト"""
        aggregator = MCIDAggregator()
        
        percentage = aggregator._calculate_percentage(50.0, 100.0)
        assert percentage == 50.0
        
        percentage = aggregator._calculate_percentage(100.0, 400.0)
        assert percentage == 25.0
    
    def test_calculate_percentage_zero_division(self):
        """_calculate_percentage ヘルパーメソッドのゼロ除算テスト"""
        aggregator = MCIDAggregator()
        
        percentage = aggregator._calculate_percentage(0.0, 0.0)
        assert percentage == 0.0
        
        percentage = aggregator._calculate_percentage(100.0, 0.0)
        assert percentage == 0.0
