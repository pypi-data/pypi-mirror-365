import os, sys 

from ml_genius.ml.classification.components.data_ingestion import DataIngestion
from ml_genius.ml.classification.components.data_transformation import DataTransformation
from ml_genius.ml.classification.components.model_trainer import ModelTrainer


class AutoClassification: 
    def __init__(self, path: str, filetype: str, target_column: str, **params):
        self.path = path 
        self.filetype = filetype 
        self.target_column = target_column
        self.params = params
        
    def train_model(self): 
        self.data_ingestion = DataIngestion(path=self.path, file_type=self.filetype, **self.params)
        self.data_ingestion_artifacts = self.data_ingestion.run_data_ingestion()

        self.data_transformation = DataTransformation(self.data_ingestion_artifacts, target_column=self.target_column)
        self.data_transformation_artifacts = self.data_transformation.run_data_transformation()

        self.model_trainer = ModelTrainer(self.data_transformation_artifacts)
        self.model_trainer_artifacts = self.model_trainer.train_model()

        return {
            "best_model_name": self.model_trainer_artifacts.best_model_name, 
            "model": self.model_trainer_artifacts.trained_model, 
            "model_params": self.model_trainer_artifacts.best_model_parameters, 
            "accuracy": self.model_trainer_artifacts.train_metric_artifact.accuracy, 
            "precision": self.model_trainer_artifacts.train_metric_artifact.precision_score, 
            "recall": self.model_trainer_artifacts.train_metric_artifact.recall_score, 
            "f1_score": self.model_trainer_artifacts.train_metric_artifact.f1_score
            # "models_report":self.model_trainer_artifacts.models_report 
        }