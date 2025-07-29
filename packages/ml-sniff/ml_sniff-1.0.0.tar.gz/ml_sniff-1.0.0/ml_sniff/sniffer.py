"""
Core ML problem detection functionality.

This module contains the Sniffer class that automatically detects
machine learning problem types from data with advanced analytics.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Union, Dict, Any, Optional, Tuple, List
from pathlib import Path
import warnings
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class Sniffer:
    """
    Advanced ML problem detection from CSV files or pandas DataFrames.
    
    This class provides comprehensive data analysis including:
    - Automatic target detection and problem type classification
    - Feature importance and selection
    - Data quality assessment
    - Outlier detection
    - Advanced visualizations
    - Model recommendations with hyperparameter suggestions
    """
    
    def __init__(self, data: Union[str, Path, pd.DataFrame], 
                 target_column: Optional[str] = None,
                 auto_analyze: bool = True):
        """
        Initialize the Sniffer with data.
        
        Args:
            data: CSV file path (str/Path) or pandas DataFrame
            target_column: Optional manual target column specification
            auto_analyze: Whether to automatically analyze data on initialization
        """
        self.data = self._load_data(data)
        self.target_column = target_column
        self.problem_type = None
        self.suggested_model = None
        self.analysis_results = {}
        self.feature_importance = {}
        self.data_quality_report = {}
        self.outlier_info = {}
        self.clustering_analysis = {}
        
        if auto_analyze:
            self._analyze_data()
    
    def _load_data(self, data: Union[str, Path, pd.DataFrame]) -> pd.DataFrame:
        """
        Load data from file path or DataFrame.
        
        Args:
            data: CSV file path or pandas DataFrame
            
        Returns:
            Loaded pandas DataFrame
        """
        if isinstance(data, pd.DataFrame):
            return data.copy()
        elif isinstance(data, (str, Path)):
            return pd.read_csv(data)
        else:
            raise ValueError("Data must be a pandas DataFrame or file path")
    
    def _analyze_data(self) -> None:
        """Perform comprehensive data analysis."""
        self._calculate_basic_stats()
        self._assess_data_quality()
        self._detect_outliers()
        
        if self.target_column is None:
            self._identify_target_column()
        
        if self.target_column is not None:
            self._determine_problem_type()
            self._suggest_model()
            self._analyze_feature_importance()
        else:
            self._perform_clustering_analysis()
    
    def _calculate_basic_stats(self) -> None:
        """Calculate comprehensive basic statistics about the dataset."""
        total_cells = len(self.data) * len(self.data.columns)
        missing_percentage = 0.0
        if total_cells > 0:
            missing_percentage = (self.data.isnull().sum().sum() / total_cells) * 100
        
        # Calculate skewness and kurtosis for numeric columns
        numeric_stats = {}
        for col in self.data.select_dtypes(include=[np.number]).columns:
            numeric_stats[col] = {
                'skewness': self.data[col].skew(),
                'kurtosis': self.data[col].kurtosis(),
                'q1': self.data[col].quantile(0.25),
                'q3': self.data[col].quantile(0.75),
                'iqr': self.data[col].quantile(0.75) - self.data[col].quantile(0.25)
            }
        
        self.analysis_results['basic_stats'] = {
            'rows': len(self.data),
            'columns': len(self.data.columns),
            'missing_percentage': missing_percentage,
            'dtypes': self.data.dtypes.value_counts().to_dict(),
            'memory_usage_mb': self.data.memory_usage(deep=True).sum() / 1024 / 1024,
            'numeric_stats': numeric_stats,
            'categorical_columns': list(self.data.select_dtypes(include=['object', 'category']).columns),
            'numeric_columns': list(self.data.select_dtypes(include=[np.number]).columns)
        }
    
    def _assess_data_quality(self) -> None:
        """Assess data quality metrics."""
        quality_metrics = {}
        
        for col in self.data.columns:
            col_data = self.data[col]
            quality_metrics[col] = {
                'missing_count': col_data.isnull().sum(),
                'missing_percentage': (col_data.isnull().sum() / len(col_data)) * 100,
                'unique_count': col_data.nunique(),
                'unique_percentage': (col_data.nunique() / len(col_data)) * 100,
                'duplicate_count': col_data.duplicated().sum(),
                'duplicate_percentage': (col_data.duplicated().sum() / len(col_data)) * 100
            }
            
            # Add type-specific metrics
            if pd.api.types.is_numeric_dtype(col_data):
                quality_metrics[col].update({
                    'zero_count': (col_data == 0).sum(),
                    'negative_count': (col_data < 0).sum(),
                    'outlier_count': self._count_outliers(col_data)
                })
            else:
                quality_metrics[col].update({
                    'empty_string_count': (col_data == '').sum(),
                    'whitespace_count': col_data.astype(str).str.isspace().sum()
                })
        
        self.data_quality_report = quality_metrics
    
    def _count_outliers(self, series: pd.Series) -> int:
        """Count outliers using IQR method."""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return ((series < lower_bound) | (series > upper_bound)).sum()
    
    def _detect_outliers(self) -> None:
        """Detect outliers in numeric columns."""
        outlier_info = {}
        
        for col in self.data.select_dtypes(include=[np.number]).columns:
            col_data = self.data[col].dropna()
            if len(col_data) == 0:
                continue
                
            # Multiple outlier detection methods
            outliers = {}
            
            # IQR method
            Q1 = col_data.quantile(0.25)
            Q3 = col_data.quantile(0.75)
            IQR = Q3 - Q1
            iqr_outliers = col_data[(col_data < Q1 - 1.5 * IQR) | (col_data > Q3 + 1.5 * IQR)]
            outliers['iqr'] = {
                'count': len(iqr_outliers),
                'percentage': (len(iqr_outliers) / len(col_data)) * 100,
                'indices': iqr_outliers.index.tolist()
            }
            
            # Z-score method
            z_scores = np.abs(stats.zscore(col_data))
            z_outliers = col_data[z_scores > 3]
            outliers['zscore'] = {
                'count': len(z_outliers),
                'percentage': (len(z_outliers) / len(col_data)) * 100,
                'indices': z_outliers.index.tolist()
            }
            
            outlier_info[col] = outliers
        
        self.outlier_info = outlier_info
    
    def _identify_target_column(self) -> None:
        """
        Identify the most likely target column using advanced heuristics.
        
        Heuristics:
        1. Column named 'target' or similar (highest priority)
        2. Column with lowest null percentage
        3. Column with highest correlation with other features
        4. Column with most variation (for numeric columns)
        5. Column with balanced distribution (for classification)
        """
        # Calculate null percentages
        null_percentages = (self.data.isnull().sum() / len(self.data)) * 100
        
        # Calculate correlations for numeric columns
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        correlations = {}
        
        if len(numeric_cols) > 1:
            corr_matrix = self.data[numeric_cols].corr()
            for col in numeric_cols:
                # Average absolute correlation with other columns
                other_corrs = corr_matrix[col].drop(col).abs()
                correlations[col] = other_corrs.mean() if len(other_corrs) > 0 else 0
        
        # Calculate variation for numeric columns
        variations = {}
        for col in numeric_cols:
            if self.data[col].std() > 0:
                variations[col] = self.data[col].std() / self.data[col].mean()
            else:
                variations[col] = 0
        
        # Calculate distribution balance for potential classification targets
        distribution_scores = {}
        for col in self.data.columns:
            col_data = self.data[col]
            if col_data.nunique() <= 20:  # Potential classification target
                value_counts = col_data.value_counts()
                # Calculate balance score (lower is more balanced)
                balance_score = 1 - (value_counts.max() - value_counts.min()) / value_counts.sum()
                distribution_scores[col] = balance_score
            else:
                distribution_scores[col] = 0
        
        # Score each column
        scores = {}
        for col in self.data.columns:
            score = 0
            
            # Priority for columns named 'target' or similar
            col_lower = col.lower()
            if 'target' in col_lower or 'label' in col_lower or 'class' in col_lower or 'y' == col_lower:
                score += 1000  # High priority for target-like names
            else:
                # For non-target-like names, use much lower base scores
                score += 50  # Base score for features
                
                # Lower null percentage is better
                null_score = 100 - null_percentages[col]
                score += null_score * 0.1
                
                # Higher correlation is better (for numeric columns)
                if col in correlations:
                    score += correlations[col] * 50 * 0.1
                
                # Higher variation is better (for numeric columns)
                if col in variations:
                    score += variations[col] * 50 * 0.1
                
                # Better distribution balance for classification
                score += distribution_scores[col] * 100
            
            scores[col] = score
        
        # Select the column with highest score
        if scores:
            best_column = max(scores, key=scores.get)
            best_score = scores[best_column]
            
            # If the best score is too low, treat as clustering problem
            if best_score < 200:  # No target-like names found (1000+ score)
                self.target_column = None
            else:
                self.target_column = best_column
        else:
            self.target_column = None
    
    def _determine_problem_type(self) -> None:
        """
        Determine the ML problem type based on target column characteristics.
        """
        if self.target_column is None:
            self.problem_type = "Clustering"
            return
        
        target_data = self.data[self.target_column]
        
        # Check if target is numeric
        if pd.api.types.is_numeric_dtype(target_data):
            # Count unique values
            unique_count = target_data.nunique()
            
            # For small datasets, use a lower threshold
            if len(target_data) < 50:
                threshold = min(10, len(target_data) // 2)
            else:
                threshold = 30
            
            if unique_count <= threshold:
                self.problem_type = "Classification"
            else:
                self.problem_type = "Regression"
        else:
            # Categorical data is always classification
            self.problem_type = "Classification"
    
    def _suggest_model(self) -> None:
        """Suggest appropriate model based on problem type with hyperparameters."""
        if self.problem_type == "Classification":
            target_data = self.data[self.target_column]
            unique_count = target_data.nunique()
            
            if unique_count == 2:
                self.suggested_model = {
                    'name': 'RandomForestClassifier',
                    'hyperparameters': {
                        'n_estimators': 100,
                        'max_depth': 10,
                        'random_state': 42
                    },
                    'alternatives': ['LogisticRegression', 'SVM', 'XGBClassifier']
                }
            else:
                self.suggested_model = {
                    'name': 'RandomForestClassifier',
                    'hyperparameters': {
                        'n_estimators': 100,
                        'max_depth': 10,
                        'random_state': 42
                    },
                    'alternatives': ['SVM', 'KNeighborsClassifier', 'XGBClassifier']
                }
                
        elif self.problem_type == "Regression":
            self.suggested_model = {
                'name': 'RandomForestRegressor',
                'hyperparameters': {
                    'n_estimators': 100,
                    'max_depth': 10,
                    'random_state': 42
                },
                'alternatives': ['LinearRegression', 'XGBRegressor', 'SVR']
            }
            
        elif self.problem_type == "Clustering":
            self.suggested_model = {
                'name': 'KMeans',
                'hyperparameters': {
                    'n_clusters': 3,
                    'random_state': 42
                },
                'alternatives': ['DBSCAN', 'HierarchicalClustering', 'GaussianMixture']
            }
            
        else:
            self.suggested_model = {
                'name': 'Unknown',
                'hyperparameters': {},
                'alternatives': []
            }
    
    def _analyze_feature_importance(self) -> None:
        """Analyze feature importance using multiple methods."""
        if self.target_column is None:
            return
        
        # Prepare data
        X = self.data.drop(columns=[self.target_column])
        y = self.data[self.target_column]
        
        # Remove non-numeric columns for now
        X_numeric = X.select_dtypes(include=[np.number])
        if len(X_numeric.columns) == 0:
            return
        
        # Fill missing values
        X_numeric = X_numeric.fillna(X_numeric.mean())
        y = y.fillna(y.mode()[0] if len(y.mode()) > 0 else y.mean())
        
        feature_importance = {}
        
        # Random Forest importance
        if self.problem_type == "Classification":
            rf = RandomForestClassifier(n_estimators=50, random_state=42)
            mi_scores = mutual_info_classif(X_numeric, y, random_state=42)
        else:
            rf = RandomForestRegressor(n_estimators=50, random_state=42)
            mi_scores = mutual_info_regression(X_numeric, y, random_state=42)
        
        rf.fit(X_numeric, y)
        
        feature_importance['random_forest'] = dict(zip(X_numeric.columns, rf.feature_importances_))
        feature_importance['mutual_info'] = dict(zip(X_numeric.columns, mi_scores))
        
        # Correlation-based importance
        correlations = {}
        for col in X_numeric.columns:
            if self.problem_type == "Classification":
                # For classification, use correlation with encoded target
                corr = abs(X_numeric[col].corr(pd.get_dummies(y).iloc[:, 0]))
            else:
                corr = abs(X_numeric[col].corr(y))
            correlations[col] = corr if not pd.isna(corr) else 0
        
        feature_importance['correlation'] = correlations
        
        self.feature_importance = feature_importance
    
    def _perform_clustering_analysis(self) -> None:
        """Perform clustering analysis when no target is identified."""
        # Use only numeric columns
        numeric_data = self.data.select_dtypes(include=[np.number])
        if len(numeric_data.columns) == 0:
            return
        
        # Fill missing values
        numeric_data = numeric_data.fillna(numeric_data.mean())
        
        # Standardize data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_data)
        
        # Try different numbers of clusters
        silhouette_scores = []
        inertias = []
        k_range = range(2, min(11, len(numeric_data) // 2))
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42)
            cluster_labels = kmeans.fit_predict(scaled_data)
            
            if len(np.unique(cluster_labels)) > 1:
                silhouette_scores.append(silhouette_score(scaled_data, cluster_labels))
                inertias.append(kmeans.inertia_)
            else:
                silhouette_scores.append(0)
                inertias.append(float('inf'))
        
        # Find optimal k
        if silhouette_scores:
            optimal_k = k_range[np.argmax(silhouette_scores)]
        else:
            optimal_k = 2
        
        self.clustering_analysis = {
            'optimal_clusters': optimal_k,
            'silhouette_scores': dict(zip(k_range, silhouette_scores)),
            'inertias': dict(zip(k_range, inertias)),
            'best_silhouette_score': max(silhouette_scores) if silhouette_scores else 0
        }
    
    def get_label_distribution(self) -> Optional[Dict[str, int]]:
        """
        Get label distribution for classification problems.
        
        Returns:
            Dictionary with label counts or None if not classification
        """
        if self.problem_type != "Classification" or self.target_column is None:
            return None
        
        return self.data[self.target_column].value_counts().to_dict()
    
    def get_feature_importance(self, method: str = 'random_forest') -> Optional[Dict[str, float]]:
        """
        Get feature importance scores.
        
        Args:
            method: 'random_forest', 'mutual_info', or 'correlation'
            
        Returns:
            Dictionary of feature importance scores
        """
        if method not in self.feature_importance:
            return None
        
        return self.feature_importance[method]
    
    def get_top_features(self, n: int = 5, method: str = 'random_forest') -> List[str]:
        """
        Get top n most important features.
        
        Args:
            n: Number of top features to return
            method: Feature importance method to use
            
        Returns:
            List of top feature names
        """
        importance = self.get_feature_importance(method)
        if not importance:
            return []
        
        sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        return [feature for feature, score in sorted_features[:n]]
    
    def get_data_quality_summary(self) -> Dict[str, Any]:
        """
        Get a summary of data quality issues.
        
        Returns:
            Dictionary with data quality summary
        """
        issues = {
            'high_missing': [],
            'high_duplicates': [],
            'low_variance': [],
            'many_outliers': []
        }
        
        for col, metrics in self.data_quality_report.items():
            if metrics['missing_percentage'] > 20:
                issues['high_missing'].append(col)
            if metrics['duplicate_percentage'] > 50:
                issues['high_duplicates'].append(col)
            if metrics['unique_percentage'] < 5:
                issues['low_variance'].append(col)
            
            # Check outliers
            if col in self.outlier_info:
                outlier_pct = self.outlier_info[col]['iqr']['percentage']
                if outlier_pct > 10:
                    issues['many_outliers'].append(col)
        
        return issues
    
    def visualize_data(self, figsize: Tuple[int, int] = (15, 10)) -> None:
        """
        Create comprehensive visualizations for the dataset.
        
        Args:
            figsize: Figure size as (width, height)
        """
        fig, axes = plt.subplots(3, 3, figsize=figsize)
        fig.suptitle('ML Sniff Advanced Data Analysis', fontsize=16)
        
        # 1. Missing data heatmap
        missing_data = self.data.isnull()
        if missing_data.sum().sum() > 0:
            sns.heatmap(missing_data, cbar=True, ax=axes[0, 0])
            axes[0, 0].set_title('Missing Data Heatmap')
        else:
            axes[0, 0].text(0.5, 0.5, 'No Missing Data', ha='center', va='center')
            axes[0, 0].set_title('Missing Data')
        
        # 2. Target distribution (if target exists)
        if self.target_column:
            if self.problem_type == "Classification":
                self.data[self.target_column].value_counts().plot(kind='bar', ax=axes[0, 1])
                axes[0, 1].set_title(f'Target Distribution: {self.target_column}')
                axes[0, 1].tick_params(axis='x', rotation=45)
            else:
                self.data[self.target_column].hist(ax=axes[0, 1], bins=30)
                axes[0, 1].set_title(f'Target Distribution: {self.target_column}')
        else:
            axes[0, 1].text(0.5, 0.5, 'No Target Column', ha='center', va='center')
            axes[0, 1].set_title('Target Distribution')
        
        # 3. Correlation heatmap (for numeric columns)
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = self.data[numeric_cols].corr()
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=axes[0, 2])
            axes[0, 2].set_title('Correlation Matrix')
        else:
            axes[0, 2].text(0.5, 0.5, 'Insufficient numeric data', ha='center', va='center')
            axes[0, 2].set_title('Correlation Matrix')
        
        # 4. Data types summary
        dtype_counts = self.data.dtypes.value_counts()
        dtype_counts.plot(kind='bar', ax=axes[1, 0])
        axes[1, 0].set_title('Data Types Distribution')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 5. Feature importance (if available)
        if self.feature_importance:
            importance = self.get_feature_importance('random_forest')
            if importance:
                features = list(importance.keys())
                scores = list(importance.values())
                axes[1, 1].barh(features, scores)
                axes[1, 1].set_title('Feature Importance (Random Forest)')
        else:
            axes[1, 1].text(0.5, 0.5, 'No Feature Importance', ha='center', va='center')
            axes[1, 1].set_title('Feature Importance')
        
        # 6. Outlier analysis
        if self.outlier_info:
            outlier_counts = []
            outlier_labels = []
            for col, info in self.outlier_info.items():
                outlier_counts.append(info['iqr']['count'])
                outlier_labels.append(col)
            
            if outlier_counts:
                axes[1, 2].bar(outlier_labels, outlier_counts)
                axes[1, 2].set_title('Outlier Count (IQR Method)')
                axes[1, 2].tick_params(axis='x', rotation=45)
            else:
                axes[1, 2].text(0.5, 0.5, 'No Outliers Detected', ha='center', va='center')
                axes[1, 2].set_title('Outlier Analysis')
        else:
            axes[1, 2].text(0.5, 0.5, 'No Outlier Data', ha='center', va='center')
            axes[1, 2].set_title('Outlier Analysis')
        
        # 7. Data quality issues
        quality_issues = self.get_data_quality_summary()
        issue_counts = [len(issues) for issues in quality_issues.values()]
        issue_labels = ['High Missing', 'High Duplicates', 'Low Variance', 'Many Outliers']
        
        axes[2, 0].bar(issue_labels, issue_counts)
        axes[2, 0].set_title('Data Quality Issues')
        axes[2, 0].tick_params(axis='x', rotation=45)
        
        # 8. Clustering analysis (if applicable)
        if self.clustering_analysis:
            k_values = list(self.clustering_analysis['silhouette_scores'].keys())
            silhouette_scores = list(self.clustering_analysis['silhouette_scores'].values())
            axes[2, 1].plot(k_values, silhouette_scores, marker='o')
            axes[2, 1].set_title('Clustering Silhouette Scores')
            axes[2, 1].set_xlabel('Number of Clusters')
            axes[2, 1].set_ylabel('Silhouette Score')
        else:
            axes[2, 1].text(0.5, 0.5, 'No Clustering Analysis', ha='center', va='center')
            axes[2, 1].set_title('Clustering Analysis')
        
        # 9. Distribution of first numeric column
        if len(numeric_cols) > 0:
            first_numeric = numeric_cols[0]
            self.data[first_numeric].hist(ax=axes[2, 2], bins=20)
            axes[2, 2].set_title(f'Distribution: {first_numeric}')
        else:
            axes[2, 2].text(0.5, 0.5, 'No Numeric Data', ha='center', va='center')
            axes[2, 2].set_title('Data Distribution')
        
        plt.tight_layout()
        plt.show()
    
    def create_interactive_dashboard(self) -> None:
        """Create an interactive Plotly dashboard."""
        if not self.data_quality_report:
            print("No data quality analysis available. Run analyze_data() first.")
            return
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Missing Data Heatmap', 'Target Distribution', 
                          'Feature Importance', 'Correlation Matrix',
                          'Data Quality Issues', 'Outlier Analysis'),
            specs=[[{"type": "heatmap"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "heatmap"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # 1. Missing data heatmap
        missing_data = self.data.isnull()
        if missing_data.sum().sum() > 0:
            fig.add_trace(
                go.Heatmap(z=missing_data.values, 
                          x=missing_data.columns, 
                          y=missing_data.index,
                          colorscale='Reds'),
                row=1, col=1
            )
        
        # 2. Target distribution
        if self.target_column:
            target_counts = self.data[self.target_column].value_counts()
            fig.add_trace(
                go.Bar(x=target_counts.index, y=target_counts.values),
                row=1, col=2
            )
        
        # 3. Feature importance
        if self.feature_importance:
            importance = self.get_feature_importance('random_forest')
            if importance:
                fig.add_trace(
                    go.Bar(x=list(importance.keys()), y=list(importance.values())),
                    row=2, col=1
                )
        
        # 4. Correlation matrix
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = self.data[numeric_cols].corr()
            fig.add_trace(
                go.Heatmap(z=corr_matrix.values, 
                          x=corr_matrix.columns, 
                          y=corr_matrix.index,
                          colorscale='RdBu'),
                row=2, col=2
            )
        
        # 5. Data quality issues
        quality_issues = self.get_data_quality_summary()
        issue_counts = [len(issues) for issues in quality_issues.values()]
        issue_labels = ['High Missing', 'High Duplicates', 'Low Variance', 'Many Outliers']
        
        fig.add_trace(
            go.Bar(x=issue_labels, y=issue_counts),
            row=3, col=1
        )
        
        # 6. Outlier analysis
        if self.outlier_info:
            outlier_counts = []
            outlier_labels = []
            for col, info in self.outlier_info.items():
                outlier_counts.append(info['iqr']['count'])
                outlier_labels.append(col)
            
            if outlier_counts:
                fig.add_trace(
                    go.Bar(x=outlier_labels, y=outlier_counts),
                    row=3, col=2
                )
        
        fig.update_layout(height=900, title_text="ML Sniff Interactive Dashboard")
        fig.show()
    
    def report(self) -> None:
        """
        Print a comprehensive analysis report.
        """
        print("=" * 80)
        print("ML SNIFF - ADVANCED ML PROBLEM DETECTION")
        print("=" * 80)
        print()
        
        # Basic Statistics
        stats = self.analysis_results['basic_stats']
        print("📊 BASIC STATISTICS:")
        print(f"   • Rows: {stats['rows']:,}")
        print(f"   • Columns: {stats['columns']}")
        print(f"   • Missing Data: {stats['missing_percentage']:.2f}%")
        print(f"   • Memory Usage: {stats['memory_usage_mb']:.2f} MB")
        print(f"   • Numeric Columns: {len(stats['numeric_columns'])}")
        print(f"   • Categorical Columns: {len(stats['categorical_columns'])}")
        print()
        
        # Data Types
        print("📋 DATA TYPES:")
        for dtype, count in stats['dtypes'].items():
            print(f"   • {dtype}: {count} columns")
        print()
        
        # Data Quality Summary
        quality_issues = self.get_data_quality_summary()
        print("🔍 DATA QUALITY ASSESSMENT:")
        for issue_type, columns in quality_issues.items():
            if columns:
                print(f"   • {issue_type.replace('_', ' ').title()}: {', '.join(columns)}")
        if not any(quality_issues.values()):
            print("   • No major quality issues detected")
        print()
        
        # Target Column Analysis
        if self.target_column:
            print("🎯 TARGET COLUMN ANALYSIS:")
            print(f"   • Identified Target: '{self.target_column}'")
            print(f"   • Problem Type: {self.problem_type}")
            print(f"   • Suggested Model: {self.suggested_model['name']}")
            print()
            
            # Target statistics
            target_data = self.data[self.target_column]
            print(f"   • Target Statistics:")
            print(f"     - Data Type: {target_data.dtype}")
            print(f"     - Unique Values: {target_data.nunique()}")
            print(f"     - Missing Values: {target_data.isnull().sum()}")
            
            if pd.api.types.is_numeric_dtype(target_data):
                print(f"     - Mean: {target_data.mean():.4f}")
                print(f"     - Std: {target_data.std():.4f}")
                print(f"     - Min: {target_data.min():.4f}")
                print(f"     - Max: {target_data.max():.4f}")
                print(f"     - Skewness: {target_data.skew():.4f}")
                print(f"     - Kurtosis: {target_data.kurtosis():.4f}")
            
            # Label distribution for classification
            if self.problem_type == "Classification":
                label_dist = self.get_label_distribution()
                if label_dist:
                    print(f"     - Label Distribution:")
                    for label, count in label_dist.items():
                        percentage = (count / len(target_data)) * 100
                        print(f"       * {label}: {count} ({percentage:.1f}%)")
        else:
            print("🎯 TARGET COLUMN ANALYSIS:")
            print("   • No clear target column identified")
            print("   • Problem Type: Clustering")
            print("   • Suggested Model: KMeans")
            
            if self.clustering_analysis:
                print(f"   • Optimal Clusters: {self.clustering_analysis['optimal_clusters']}")
                print(f"   • Best Silhouette Score: {self.clustering_analysis['best_silhouette_score']:.3f}")
        print()
        
        # Feature Importance
        if self.feature_importance:
            print("🏆 FEATURE IMPORTANCE:")
            top_features = self.get_top_features(5, 'random_forest')
            for i, feature in enumerate(top_features, 1):
                importance = self.feature_importance['random_forest'][feature]
                print(f"   {i}. {feature}: {importance:.4f}")
        print()
        
        # Model Recommendations
        print("💡 MODEL RECOMMENDATIONS:")
        if self.suggested_model['name'] != 'Unknown':
            print(f"   • Primary Model: {self.suggested_model['name']}")
            print(f"   • Hyperparameters: {self.suggested_model['hyperparameters']}")
            print(f"   • Alternative Models: {', '.join(self.suggested_model['alternatives'])}")
            
            if self.problem_type == "Classification":
                print("   • Consider class imbalance if present")
                print("   • Use metrics like accuracy, precision, recall, F1-score")
            elif self.problem_type == "Regression":
                print("   • Consider feature scaling")
                print("   • Use metrics like MSE, MAE, R²")
            elif self.problem_type == "Clustering":
                print("   • Consider feature scaling")
                print("   • Use metrics like silhouette score, inertia")
        
        print()
        print("=" * 80)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary dictionary of the analysis results.
        
        Returns:
            Dictionary containing all analysis results
        """
        return {
            'target_column': self.target_column,
            'problem_type': self.problem_type,
            'suggested_model': self.suggested_model,
            'basic_stats': self.analysis_results['basic_stats'],
            'label_distribution': self.get_label_distribution(),
            'feature_importance': self.feature_importance,
            'data_quality_report': self.data_quality_report,
            'outlier_info': self.outlier_info,
            'clustering_analysis': self.clustering_analysis,
            'quality_issues': self.get_data_quality_summary()
        }
    
    def export_report(self, filename: str, format: str = 'json') -> None:
        """
        Export analysis report to file.
        
        Args:
            filename: Output filename
            format: 'json', 'csv', or 'txt'
        """
        summary = self.get_summary()
        
        if format == 'json':
            import json
            # Convert numpy types to native Python types for JSON serialization
            def convert_numpy(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, pd.Series):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {str(k): convert_numpy(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy(item) for item in obj]
                else:
                    return obj
            
            converted_summary = convert_numpy(summary)
            with open(filename, 'w') as f:
                json.dump(converted_summary, f, indent=2, default=str)
        elif format == 'csv':
            # Export key metrics to CSV
            metrics_df = pd.DataFrame({
                'Metric': ['Target Column', 'Problem Type', 'Model', 'Rows', 'Columns'],
                'Value': [
                    summary['target_column'],
                    summary['problem_type'],
                    summary['suggested_model']['name'],
                    summary['basic_stats']['rows'],
                    summary['basic_stats']['columns']
                ]
            })
            metrics_df.to_csv(filename, index=False)
        elif format == 'txt':
            with open(filename, 'w') as f:
                f.write("ML SNIFF ANALYSIS REPORT\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Target Column: {summary['target_column']}\n")
                f.write(f"Problem Type: {summary['problem_type']}\n")
                f.write(f"Suggested Model: {summary['suggested_model']['name']}\n")
                f.write(f"Rows: {summary['basic_stats']['rows']}\n")
                f.write(f"Columns: {summary['basic_stats']['columns']}\n")
        
        print(f"Report exported to {filename}")
    
    def suggest_preprocessing(self) -> Dict[str, List[str]]:
        """
        Suggest preprocessing steps based on data analysis.
        
        Returns:
            Dictionary with preprocessing suggestions
        """
        suggestions = {
            'missing_data': [],
            'outliers': [],
            'scaling': [],
            'encoding': [],
            'feature_selection': []
        }
        
        # Missing data suggestions
        for col, metrics in self.data_quality_report.items():
            if metrics['missing_percentage'] > 0:
                if metrics['missing_percentage'] < 10:
                    suggestions['missing_data'].append(f"Impute missing values in '{col}'")
                else:
                    suggestions['missing_data'].append(f"Consider dropping or advanced imputation for '{col}'")
        
        # Outlier suggestions
        for col, info in self.outlier_info.items():
            if info['iqr']['percentage'] > 5:
                suggestions['outliers'].append(f"Handle outliers in '{col}' (IQR method)")
        
        # Scaling suggestions
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            suggestions['scaling'].append("Apply StandardScaler or MinMaxScaler to numeric features")
        
        # Encoding suggestions
        categorical_cols = self.data.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            suggestions['encoding'].append("Apply LabelEncoder or OneHotEncoder to categorical features")
        
        # Feature selection suggestions
        if self.feature_importance:
            low_importance_features = self.get_top_features(len(numeric_cols), 'random_forest')[-3:]
            if low_importance_features:
                suggestions['feature_selection'].append(f"Consider removing low-importance features: {low_importance_features}")
        
        return suggestions 