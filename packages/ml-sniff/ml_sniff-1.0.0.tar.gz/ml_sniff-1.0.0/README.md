# ML Sniff 🕵️‍♂️

**Advanced Machine Learning Problem Detection from CSV files and DataFrames**

*By [Sherin Joseph Roy](https://sherin-sef-ai.github.io/) - Startup Founder & Hardware/IoT Enthusiast*

ML Sniff is a comprehensive Python package that automatically analyzes your data to determine the most likely machine learning problem type, identifies the target column, suggests appropriate models, and provides advanced data analytics.

## 🚀 Features

- 🔍 **Automatic Target Detection**: Uses advanced heuristics to identify the most likely target column
- 🎯 **Problem Type Classification**: Determines if your data is Classification, Regression, or Clustering
- 🤖 **Model Suggestions**: Recommends appropriate algorithms with hyperparameters
- 📊 **Comprehensive Analysis**: Provides detailed statistics and visualizations
- 🏆 **Feature Importance**: Multiple methods (Random Forest, Mutual Information, Correlation)
- 🔍 **Data Quality Assessment**: Missing data, duplicates, outliers, and variance analysis
- 📈 **Advanced Visualizations**: Static plots and interactive Plotly dashboards
- 🖥️ **CLI Support**: Analyze files directly from the command line
- 🖥️ **Web GUI**: Beautiful Streamlit interface with interactive dashboards
- 📤 **Export Capabilities**: Export reports in JSON, CSV, or TXT formats
- 🛠️ **Preprocessing Suggestions**: Automated recommendations for data preparation

## 📦 Installation

### From PyPI (when published)
```bash
pip install ml-sniff
```

### From Source
```bash
git clone https://github.com/Sherin-SEF-AI/ml-sniffer.git
cd ml-sniffer
pip install .
```

## 🚀 Quick Start

### Command Line Interface

Basic analysis:
```bash
ml-sniff your_data.csv
```

Show visualizations:
```bash
ml-sniff your_data.csv --visualize
```

Create interactive dashboard:
```bash
ml-sniff your_data.csv --interactive
```

Export detailed report:
```bash
ml-sniff your_data.csv --export report.json --format json
```

Show preprocessing suggestions:
```bash
ml-sniff your_data.csv --preprocessing
```

Show feature importance:
```bash
ml-sniff your_data.csv --feature-importance
```

Show data quality report:
```bash
ml-sniff your_data.csv --data-quality
```

Specify target column manually:
```bash
ml-sniff your_data.csv --target target_column
```

### Web Interface (GUI)

Launch the beautiful Streamlit web interface:

```bash
# Method 1: Using the launcher script
python run_gui.py

# Method 2: Direct streamlit command
streamlit run streamlit_app.py

# Method 3: Using the command line entry point
ml-sniff-gui
```

The GUI will open in your browser at `http://localhost:8501` and provides:

- 📁 **File Upload**: Drag and drop CSV files
- 🎯 **Interactive Analysis**: Real-time analysis with visual feedback
- 📊 **Interactive Charts**: Plotly visualizations with zoom, pan, and hover
- 🏆 **Feature Analysis**: Multiple importance methods with interactive charts
- 🔍 **Data Quality**: Comprehensive quality assessment with detailed reports
- 📈 **Visualizations**: Correlation matrices, distributions, and outlier analysis
- 📤 **Export**: Download reports in multiple formats
- ⚙️ **Customization**: Toggle features and analysis options

### Python API

```python
from ml_sniff import Sniffer

# Basic analysis
sniffer = Sniffer("your_data.csv")
sniffer.report()

# Advanced analysis with manual target
sniffer = Sniffer("your_data.csv", target_column="target")
sniffer.report()

# Get feature importance
top_features = sniffer.get_top_features(5, method='random_forest')
print(f"Top features: {top_features}")

# Get preprocessing suggestions
suggestions = sniffer.suggest_preprocessing()
print(suggestions)

# Create visualizations
sniffer.visualize_data()
sniffer.create_interactive_dashboard()

# Export report
sniffer.export_report("analysis.json", format="json")
```

## 🔧 Advanced Features

### Feature Importance Analysis

ML Sniff provides multiple methods for feature importance:

```python
# Random Forest importance
rf_importance = sniffer.get_feature_importance('random_forest')

# Mutual Information
mi_importance = sniffer.get_feature_importance('mutual_info')

# Correlation-based
corr_importance = sniffer.get_feature_importance('correlation')

# Get top features
top_features = sniffer.get_top_features(5, method='random_forest')
```

### Data Quality Assessment

Comprehensive data quality analysis:

```python
# Get data quality summary
quality_issues = sniffer.get_data_quality_summary()

# Access detailed quality metrics
quality_report = sniffer.data_quality_report

# Check for specific issues
missing_columns = quality_issues['high_missing']
outlier_columns = quality_issues['many_outliers']
```

### Preprocessing Suggestions

Automated recommendations for data preparation:

```python
suggestions = sniffer.suggest_preprocessing()

# Missing data handling
missing_suggestions = suggestions['missing_data']

# Outlier handling
outlier_suggestions = suggestions['outliers']

# Feature scaling
scaling_suggestions = suggestions['scaling']

# Categorical encoding
encoding_suggestions = suggestions['encoding']

# Feature selection
selection_suggestions = suggestions['feature_selection']
```

### Interactive Dashboard

Create interactive Plotly dashboards:

```python
# Create interactive dashboard
sniffer.create_interactive_dashboard()
```

## 📊 Example Output

```
================================================================================
ML SNIFF - ADVANCED ML PROBLEM DETECTION
================================================================================

📊 BASIC STATISTICS:
   • Rows: 1,000
   • Columns: 10
   • Missing Data: 2.50%
   • Memory Usage: 0.78 MB
   • Numeric Columns: 6
   • Categorical Columns: 1

📋 DATA TYPES:
   • float64: 6 columns
   • int64: 3 columns
   • object: 1 columns

🔍 DATA QUALITY ASSESSMENT:
   • High Missing: feature3
   • Many Outliers: feature1, feature2

🎯 TARGET COLUMN ANALYSIS:
   • Identified Target: 'target'
   • Problem Type: Classification
   • Suggested Model: RandomForestClassifier

   • Target Statistics:
     - Data Type: int64
     - Unique Values: 3
     - Missing Values: 0
     - Mean: 1.2000
     - Std: 0.8165
     - Min: 0.0000
     - Max: 2.0000
     - Skewness: 0.0000
     - Kurtosis: -1.5000
     - Label Distribution:
       * 0: 400 (40.0%)
       * 1: 350 (35.0%)
       * 2: 250 (25.0%)

🏆 FEATURE IMPORTANCE:
   1. feature1: 0.3800
   2. feature3: 0.2628
   3. feature4: 0.2000
   4. feature2: 0.1572

💡 MODEL RECOMMENDATIONS:
   • Primary Model: RandomForestClassifier
   • Hyperparameters: {'n_estimators': 100, 'max_depth': 10, 'random_state': 42}
   • Alternative Models: LogisticRegression, SVM, XGBClassifier
   • Consider class imbalance if present
   • Use metrics like accuracy, precision, recall, F1-score

================================================================================
```

## 🛠️ CLI Options

```bash
ml-sniff [OPTIONS] FILE

Options:
  --target, -t TEXT           Manually specify target column name
  --visualize, -v            Show data visualizations
  --interactive, -i          Create interactive Plotly dashboard
  --output, -o TEXT          Save report to file instead of printing to console
  --export, -e TEXT          Export detailed analysis report to file
  --format, -f [json|csv|txt] Export format (default: json)
  --summary, -s              Show only summary information
  --preprocessing, -p        Show preprocessing suggestions
  --no-auto-analyze          Skip automatic analysis on initialization
  --feature-importance       Show feature importance analysis
  --data-quality             Show detailed data quality report
```

## 📈 Sample Data

Create sample datasets to test the package:

```python
import pandas as pd
import numpy as np

# Classification dataset
np.random.seed(42)
n_samples = 1000

classification_data = {
    'feature1': np.random.normal(0, 1, n_samples),
    'feature2': np.random.normal(0, 1, n_samples),
    'feature3': np.random.normal(0, 1, n_samples),
    'feature4': np.random.normal(0, 1, n_samples),
    'categorical_feature': np.random.choice(['A', 'B', 'C'], n_samples),
    'target': np.random.choice([0, 1, 2], n_samples, p=[0.4, 0.35, 0.25])
}

df = pd.DataFrame(classification_data)
df.to_csv('classification_sample.csv', index=False)

# Regression dataset
regression_data = {
    'feature1': np.random.normal(0, 1, n_samples),
    'feature2': np.random.normal(0, 1, n_samples),
    'feature3': np.random.normal(0, 1, n_samples),
    'target': np.random.normal(0, 1, n_samples)
}

df_reg = pd.DataFrame(regression_data)
df_reg.to_csv('regression_sample.csv', index=False)
```

## 🔬 API Reference

### Sniffer Class

#### `__init__(data, target_column=None, auto_analyze=True)`
Initialize the Sniffer with data.

**Parameters:**
- `data`: CSV file path (str/Path) or pandas DataFrame
- `target_column`: Optional manual target column specification
- `auto_analyze`: Whether to automatically analyze data on initialization

#### `report()`
Print a comprehensive analysis report to console.

#### `get_summary()`
Get analysis results as a dictionary.

**Returns:**
- Dictionary with keys: `target_column`, `problem_type`, `suggested_model`, `basic_stats`, `label_distribution`, `feature_importance`, `data_quality_report`, `outlier_info`, `clustering_analysis`, `quality_issues`

#### `get_feature_importance(method='random_forest')`
Get feature importance scores.

**Parameters:**
- `method`: 'random_forest', 'mutual_info', or 'correlation'

**Returns:**
- Dictionary of feature importance scores

#### `get_top_features(n=5, method='random_forest')`
Get top n most important features.

**Parameters:**
- `n`: Number of top features to return
- `method`: Feature importance method to use

**Returns:**
- List of top feature names

#### `get_data_quality_summary()`
Get a summary of data quality issues.

**Returns:**
- Dictionary with data quality summary

#### `suggest_preprocessing()`
Suggest preprocessing steps based on data analysis.

**Returns:**
- Dictionary with preprocessing suggestions

#### `visualize_data(figsize=(15, 10))`
Generate comprehensive data visualizations.

#### `create_interactive_dashboard()`
Create an interactive Plotly dashboard.

#### `export_report(filename, format='json')`
Export analysis report to file.

**Parameters:**
- `filename`: Output filename
- `format`: 'json', 'csv', or 'txt'

## 🧪 Development

### Setup Development Environment

```bash
git clone https://github.com/ml-sniff/ml-sniff.git
cd ml-sniff
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black ml_sniff/
flake8 ml_sniff/
```

## 📋 Dependencies

- pandas >= 1.3.0
- numpy >= 1.20.0
- matplotlib >= 3.3.0
- seaborn >= 0.11.0
- scikit-learn >= 1.0.0
- scipy >= 1.7.0
- plotly >= 5.0.0

## 🚀 Roadmap

- [ ] Support for more file formats (Excel, JSON, etc.)
- [ ] Advanced feature engineering suggestions
- [ ] Model performance estimation
- [ ] Integration with popular ML libraries
- [ ] Web interface
- [ ] Batch processing capabilities
- [ ] Time series analysis
- [ ] Anomaly detection
- [ ] AutoML integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions, please:

1. Check the [documentation](https://github.com/ml-sniff/ml-sniff#readme)
2. Search [existing issues](https://github.com/ml-sniff/ml-sniff/issues)
3. Create a [new issue](https://github.com/ml-sniff/ml-sniff/issues/new)

---

**Made with ❤️ for the ML community** 