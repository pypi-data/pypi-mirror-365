import os
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.experimental import enable_iterative_imputer  # ✅ This enables the feature of IterativeImputer
from sklearn.impute import SimpleImputer, IterativeImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder
from sklearn.linear_model import BayesianRidge


class Preprocess: 
    def __init__(self, df: pd.DataFrame, target_column: str , data_store_path: str, pre_processor_store_path: str): 
        self.df = df 
        self.target_column = target_column
        self.data_store_path = data_store_path
        self.pre_processor_store_path = pre_processor_store_path
        self.preprocessor = None
        self.categorical_columns = None 
        self.numerical_columns = None 

    def fit(self) -> pd.DataFrame: 
        df_copy = self.df.copy()

        if self.target_column: 
            X = df_copy.drop(columns=[self.target_column])
            y = df_copy[self.target_column]

        else: 
            X = df_copy

        # Identify column types
        self.categorical_columns = X.select_dtypes(include=['object', 'category']).columns.tolist()
        self.numerical_columns = X.select_dtypes(include=['int64', 'float64']).columns.tolist()

        # Categorical column 
        cat_pipeline = Pipeline(steps=[
            ('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)),
            ('imputer', SimpleImputer(strategy='most_frequent'))
        ])

        # Pipeline for numerical: just pass (IterativeImputer will handle it)
        num_pipeline = 'passthrough'

        # ColumnTransformer: preprocess categorical only
        preprocessor = ColumnTransformer(transformers=[
            ('cat', cat_pipeline, self.categorical_columns),
            ('num', num_pipeline, self.numerical_columns)
        ])

        # Full pipeline with IterativeImputer
        full_pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('imputer', IterativeImputer(estimator=BayesianRidge(), random_state=0))
        ])

        # Transform data
        X_transformed = full_pipeline.fit_transform(X)

        # Convert to DataFrame
        X_transformed = pd.DataFrame(X_transformed, columns=self.categorical_columns + self.numerical_columns)
        final_df = pd.concat([X_transformed.reset_index(drop=True), y.reset_index(drop=True)], axis=1)

        # Save the data and preprocessor object to a file
        data_dir = os.path.dirname(self.data_store_path)
        os.makedirs(data_dir, exist_ok=True)

        processor_dir = os.path.dirname(self.pre_processor_store_path)
        os.makedirs(processor_dir, exist_ok=True)
       
        final_df.to_csv(self.data_store_path, index=False)
        joblib.dump(preprocessor, self.pre_processor_store_path)

        return final_df

