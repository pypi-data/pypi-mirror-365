import pandas as pd 
from dataclasses import dataclass 

@dataclass
class DataIngestionArtifacts:
    df: pd.DataFrame
    train_df: pd.DataFrame 
    test_df: pd.DataFrame

@dataclass
class DataTransformationArtifacts: 
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.DataFrame
    y_test:pd.DataFrame

@dataclass
class RegressionMetrixArtifacts: 
    mse: str 
    rmse: str 
    r2_score: str

@dataclass 
class ClassificationMetricArtifact: 
    accuracy: str
    f1_score: str 
    precision_score: str 
    recall_score: str 

@dataclass 
class ModelTrainerArtifact: 
    trained_model: object 
    best_model_name: str
    best_model_parameters: dict
    models_report: dict
    train_metric_artifact: ClassificationMetricArtifact | RegressionMetrixArtifacts
    test_metric_artifact: ClassificationMetricArtifact | RegressionMetrixArtifacts

