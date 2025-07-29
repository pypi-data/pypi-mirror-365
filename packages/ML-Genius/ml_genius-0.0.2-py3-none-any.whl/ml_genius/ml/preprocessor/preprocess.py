import os, sys 
import joblib 
import numpy as np 
import pandas as pd 

from ml_genius.ml.preprocessor.datareader import ReadData
from ml_genius.ml.preprocessor.datadescriber import DataDescribe
from ml_genius.ml.preprocessor.auto_preprocess import AutoPreprocessor
from ml_genius.ml.preprocessor.processor import Preprocess


class AutoPreprocess: 
    def __init__(self, path: str, file_type: str, store_path: str, preprocessor_store_path: str,  target_column: str, **params): 
        self.path = path
        self.file_type = file_type
        self.store_path = store_path
        self.target_column = target_column
        self.preprocessor_store_path = preprocessor_store_path
        self.params = params
        self.df = None
        self.description = None
        self.preprocessed_df = None
        self.encoder = None
        self.scaler = None

    def read_file(self):
        read_data = ReadData()
        if self.file_type == "csv": 
            self.df = read_data.read_csv(self.path, **self.params)
        elif self.file_type == "excel": 
            self.df = read_data.read_excel(self.path, **self.params)
        return self.df
    
    def describe_data(self, df: pd.DataFrame, target_column: str):
        data_describer = DataDescribe(df, target_column)
        data_describer.summarize()
        description = data_describer.get_summary_dict()
        return description

    def preprocess_data(self): 
        data_processor = Preprocess(self.df, self.target_column, self.store_path, self.preprocessor_store_path)
        self.preprocessed_df =  data_processor.fit()
        return self.preprocessed_df

    def process(self): 
        self.df = self.read_file()
        self.description = self.describe_data(self.df, self.target_column)
        self.preprocessed_df = self.preprocess_data()
        return self.preprocessed_df
