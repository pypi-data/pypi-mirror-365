import pandas as pd 
import numpy as np

class DataDescribe:
    def __init__(self, df, target_column=None):
        self.df = df
        self.target_column = target_column

        self.num_rows = df.shape[0]
        self.num_cols = df.shape[1]
        self.column_names = df.columns.tolist()

        self.dtypes = df.dtypes.to_dict()

        self.categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        self.numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

        self.num_categorical_columns = len(self.categorical_columns)
        self.num_numerical_columns = len(self.numerical_columns)

        self.missing_values = df.isnull().sum().to_dict()
        self.missing_percentage = (df.isnull().mean() * 100).to_dict()

        self.unique_values = df.nunique().to_dict()

        self.basic_stats = df.describe().to_dict()

        self.correlation_matrix = df.corr(numeric_only=True).to_dict()

        if target_column and target_column in df.columns:
            self.target_info = {
                "type": "classification" if df[target_column].nunique() <= 20 else "regression",
                "distribution": df[target_column].value_counts().to_dict()
            }
        else:
            self.target_info = {
                "type": "unknown"
            }

    def get_summary_dict(self):
        return {
            "num_rows": self.num_rows,
            "num_columns": self.num_cols,
            "column_names": self.column_names,
            "numerical_columns": self.numerical_columns,
            "categorical_columns": self.categorical_columns,
            "num_numerical_columns": self.num_numerical_columns,
            "num_categorical_columns": self.num_categorical_columns,
            "data_types": {k: str(v) for k, v in self.dtypes.items()},
            "missing_values": self.missing_values,
            "missing_percentage": {k: round(v, 2) for k, v in self.missing_percentage.items()},
            "unique_values": self.unique_values,
            "basic_statistics": {k: {col: round(v, 2) for col, v in cols.items()} for k, cols in self.basic_stats.items()},
            "correlation_matrix": {
                col: {k: round(v, 2) for k, v in corr.items()} for col, corr in self.correlation_matrix.items()
            },
            "target_info": self.target_info
        }

    def summarize(self):
        summary = self.get_summary_dict()
        print("📊 DATASET SUMMARY")
        print("="*50)
        print(f"🧾 Rows: {summary['num_rows']}")
        print(f"📐 Columns: {summary['num_columns']}")
        print(f"🔢 Numerical Columns ({summary['num_numerical_columns']}): {summary['numerical_columns']}")
        print(f"🔤 Categorical Columns ({summary['num_categorical_columns']}): {summary['categorical_columns']}")
        print()

        print("🧪 Data Types:")
        for col, dtype in summary['data_types'].items():
            print(f"   - {col}: {dtype}")
        print()

        print("🕳️ Missing Values:")
        missing = summary['missing_values']
        percent = summary['missing_percentage']
        for col in missing:
            if missing[col] > 0:
                print(f"   - {col}: {missing[col]} missing ({percent[col]}%)")
        if all(v == 0 for v in missing.values()):
            print("   - No missing values.")
        print()

        print("🔁 Unique Values:")
        for col, val in summary['unique_values'].items():
            print(f"   - {col}: {val} unique values")
        print()

        print("📈 Basic Statistics (Numerical):")
        for stat, values in summary['basic_statistics'].items():
            print(f"   {stat}:")
            for col, val in values.items():
                print(f"     - {col}: {val}")
        print()

        print("🔗 Correlation Matrix:")
        for col, corr_dict in summary['correlation_matrix'].items():
            print(f"   {col}:")
            for target_col, corr_val in corr_dict.items():
                if col != target_col:
                    print(f"     - {target_col}: {corr_val}")
        print()

        if summary['target_info']:
            print("🎯 Target Info:")
            print(f"   - Type: {summary['target_info']['type']}")
            # print(f"   - Distribution:")
            # for label, count in summary['target_info']['distribution'].items():
            #     print(f"     - {label}: {count}")
        print("="*50)
