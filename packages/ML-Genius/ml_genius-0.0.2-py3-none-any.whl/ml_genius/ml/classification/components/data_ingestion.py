import os, sys 
import pandas as pd 
import numpy as np 

from sklearn.model_selection import train_test_split

from ml_genius.ml.preprocessor.datareader import ReadData
from ml_genius.ml.classification.entity.artifacts_entity import DataIngestionArtifacts

class DataIngestion: 
    def __init__(self, path: str, file_type: str, **params): 
        self.path = path 
        self.file_type = file_type
        self.params = params
        self.df: pd.DataFrame | None = None
        self.train_df: pd.DataFrame | None = None
        self.test_df: pd.DataFrame | None = None    

    def data_ingestion(self) -> pd.DataFrame: 
        data_reader = ReadData()
        if self.file_type == "csv": 
            self.df = data_reader.read_csv(self.path, **self.params)
        elif self.file_type == "excel": 
            self.df = data_reader.read_excel(self.path, **self.params)
        else:
            raise ValueError(f"Unsupported file type: {self.file_type}")
        return self.df

    def data_train_test_split(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        train, test = train_test_split(self.df, test_size=0.2, random_state=42) 
        return train, test

    def run_data_ingestion(self) -> DataIngestionArtifacts: 
        self.df = self.data_ingestion()
        self.train_df, self.test_df = self.data_train_test_split()
        return DataIngestionArtifacts(
            df=self.df, 
            train_df=self.train_df, 
            test_df=self.test_df 
        )
        
