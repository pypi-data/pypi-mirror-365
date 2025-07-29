"""
Test cases for the Sniffer class.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

from ml_sniff import Sniffer


class TestSniffer:
    """Test cases for the Sniffer class."""
    
    def setup_method(self):
        """Set up test data."""
        np.random.seed(42)
        self.n_samples = 100
        
        # Create classification data
        self.classification_data = pd.DataFrame({
            'feature1': np.random.normal(0, 1, self.n_samples),
            'feature2': np.random.normal(0, 1, self.n_samples),
            'feature3': np.random.normal(0, 1, self.n_samples),
            'target': np.random.choice([0, 1, 2], self.n_samples, p=[0.4, 0.35, 0.25])
        })
        
        # Create regression data
        self.regression_data = pd.DataFrame({
            'feature1': np.random.normal(0, 1, self.n_samples),
            'feature2': np.random.normal(0, 1, self.n_samples),
            'feature3': np.random.normal(0, 1, self.n_samples),
            'target': np.random.normal(0, 1, self.n_samples)
        })
        
        # Create clustering data (no clear target)
        self.clustering_data = pd.DataFrame({
            'feature1': np.random.normal(0, 1, self.n_samples),
            'feature2': np.random.normal(0, 1, self.n_samples),
            'feature3': np.random.normal(0, 1, self.n_samples),
            'feature4': np.random.normal(0, 1, self.n_samples)
        })
    
    def test_init_with_dataframe(self):
        """Test initialization with pandas DataFrame."""
        sniffer = Sniffer(self.classification_data)
        assert sniffer.data is not None
        assert len(sniffer.data) == self.n_samples
        assert len(sniffer.data.columns) == 4
    
    def test_init_with_csv_file(self):
        """Test initialization with CSV file path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.classification_data.to_csv(f.name, index=False)
            file_path = f.name
        
        try:
            sniffer = Sniffer(file_path)
            assert sniffer.data is not None
            assert len(sniffer.data) == self.n_samples
            assert len(sniffer.data.columns) == 4
        finally:
            os.unlink(file_path)
    
    def test_init_with_invalid_data(self):
        """Test initialization with invalid data type."""
        with pytest.raises(ValueError):
            Sniffer(123)
    
    def test_classification_detection(self):
        """Test classification problem detection."""
        sniffer = Sniffer(self.classification_data)
        
        assert sniffer.target_column == 'target'
        assert sniffer.problem_type == 'Classification'
        assert sniffer.suggested_model == 'RandomForestClassifier'
    
    def test_regression_detection(self):
        """Test regression problem detection."""
        sniffer = Sniffer(self.regression_data)
        
        assert sniffer.target_column == 'target'
        assert sniffer.problem_type == 'Regression'
        assert sniffer.suggested_model == 'RandomForestRegressor'
    
    def test_clustering_detection(self):
        """Test clustering problem detection."""
        sniffer = Sniffer(self.clustering_data)
        
        # Should detect no clear target column for clustering data
        assert sniffer.target_column is None
        assert sniffer.problem_type == 'Clustering'
    
    def test_get_label_distribution_classification(self):
        """Test label distribution for classification."""
        sniffer = Sniffer(self.classification_data)
        label_dist = sniffer.get_label_distribution()
        
        assert label_dist is not None
        assert isinstance(label_dist, dict)
        assert all(isinstance(k, (int, str)) for k in label_dist.keys())
        assert all(isinstance(v, int) for v in label_dist.values())
    
    def test_get_label_distribution_regression(self):
        """Test label distribution for regression (should return None)."""
        sniffer = Sniffer(self.regression_data)
        label_dist = sniffer.get_label_distribution()
        
        assert label_dist is None
    
    def test_get_summary(self):
        """Test get_summary method."""
        sniffer = Sniffer(self.classification_data)
        summary = sniffer.get_summary()
        
        assert isinstance(summary, dict)
        assert 'target_column' in summary
        assert 'problem_type' in summary
        assert 'suggested_model' in summary
        assert 'basic_stats' in summary
        assert 'label_distribution' in summary
        
        # Check basic stats
        stats = summary['basic_stats']
        assert 'rows' in stats
        assert 'columns' in stats
        assert 'missing_percentage' in stats
        assert 'dtypes' in stats
        assert 'memory_usage_mb' in stats
    
    def test_basic_stats_calculation(self):
        """Test basic statistics calculation."""
        sniffer = Sniffer(self.classification_data)
        stats = sniffer.analysis_results['basic_stats']
        
        assert stats['rows'] == self.n_samples
        assert stats['columns'] == 4
        assert stats['missing_percentage'] == 0.0  # No missing data in our test
        assert isinstance(stats['memory_usage_mb'], float)
        assert stats['memory_usage_mb'] > 0
    
    def test_data_with_missing_values(self):
        """Test handling of data with missing values."""
        data_with_missing = self.classification_data.copy()
        data_with_missing.loc[0, 'feature1'] = np.nan
        data_with_missing.loc[1, 'target'] = np.nan
        
        sniffer = Sniffer(data_with_missing)
        
        # Should still work and detect the problem type
        assert sniffer.problem_type in ['Classification', 'Regression', 'Clustering']
        assert sniffer.analysis_results['basic_stats']['missing_percentage'] > 0
    
    def test_categorical_target_detection(self):
        """Test detection of categorical target columns."""
        categorical_data = pd.DataFrame({
            'feature1': np.random.normal(0, 1, 50),
            'feature2': np.random.normal(0, 1, 50),
            'target': ['A', 'B', 'C'] * 16 + ['A', 'B']  # 50 samples
        })
        
        sniffer = Sniffer(categorical_data)
        
        assert sniffer.target_column == 'target'
        assert sniffer.problem_type == 'Classification'
        assert sniffer.suggested_model == 'RandomForestClassifier'
    
    def test_binary_classification_detection(self):
        """Test detection of binary classification."""
        binary_data = pd.DataFrame({
            'feature1': np.random.normal(0, 1, 100),
            'feature2': np.random.normal(0, 1, 100),
            'target': np.random.choice([0, 1], 100)
        })
        
        sniffer = Sniffer(binary_data)
        
        assert sniffer.target_column == 'target'
        assert sniffer.problem_type == 'Classification'
        assert sniffer.suggested_model == 'RandomForestClassifier'
    
    def test_visualize_data_method(self):
        """Test that visualize_data method doesn't crash."""
        sniffer = Sniffer(self.classification_data)
        
        # Should not raise any exceptions
        try:
            sniffer.visualize_data()
        except Exception as e:
            pytest.fail(f"visualize_data raised an exception: {e}")
    
    def test_report_method(self):
        """Test that report method doesn't crash."""
        sniffer = Sniffer(self.classification_data)
        
        # Should not raise any exceptions
        try:
            sniffer.report()
        except Exception as e:
            pytest.fail(f"report raised an exception: {e}")


class TestSnifferEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame()
        
        # Should handle empty DataFrame gracefully
        sniffer = Sniffer(empty_df)
        assert sniffer.data.empty
    
    def test_single_column_dataframe(self):
        """Test handling of single column DataFrame."""
        single_col_df = pd.DataFrame({'col1': [1, 2, 3]})
        
        sniffer = Sniffer(single_col_df)
        # Should handle gracefully - single column might be treated as clustering
        assert sniffer.target_column is None or sniffer.target_column == 'col1'
    
    def test_all_null_dataframe(self):
        """Test handling of DataFrame with all null values."""
        null_df = pd.DataFrame({
            'col1': [np.nan, np.nan, np.nan],
            'col2': [np.nan, np.nan, np.nan]
        })
        
        sniffer = Sniffer(null_df)
        # Should handle gracefully
        assert sniffer.analysis_results['basic_stats']['missing_percentage'] == 100.0
    
    def test_very_large_dataframe(self):
        """Test handling of large DataFrame."""
        large_df = pd.DataFrame({
            'feature1': np.random.normal(0, 1, 10000),
            'feature2': np.random.normal(0, 1, 10000),
            'target': np.random.choice([0, 1], 10000)
        })
        
        sniffer = Sniffer(large_df)
        # Should handle large datasets
        assert sniffer.data is not None
        assert len(sniffer.data) == 10000


if __name__ == '__main__':
    pytest.main([__file__]) 