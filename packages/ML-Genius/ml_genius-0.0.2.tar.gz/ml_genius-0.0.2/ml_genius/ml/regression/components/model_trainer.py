import os 
import sys 
import pandas as pd 
import numpy as np 
import logging

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.metrics import mean_squared_error, r2_score

from ml_genius.ml.regression.entity.artifacts_entity import RegressionMetrixArtifacts, ModelTrainerArtifact, DataTransformationArtifacts


class ModelTrainer: 
    def __init__(self, data_transformation_artifacts: DataTransformationArtifacts): 
        self.data_transformation_artifacts = data_transformation_artifacts
        self.X_train = self.data_transformation_artifacts.X_train
        self.X_test = self.data_transformation_artifacts.X_test
        self.y_train = self.data_transformation_artifacts.y_train
        self.y_test = self.data_transformation_artifacts.y_test


    def evaluate_models(self, X_train, y_train, X_test, y_test, models, params): 
        report = {}
        tuned_models = {}  # NEW: to store best estimators

        for i in range(len(list(models))): 
            model_name = list(models.keys())[i]
            model = list(models.values())[i]
            para = params.get(model_name, {})

            # gs = GridSearchCV(model, para, cv=3, n_jobs=-1, verbose=1)
            # gs.fit(X_train, y_train)
            # best_model = gs.best_estimator_  # ✅ Get tuned model

            if para:
                rs = RandomizedSearchCV(model, param_distributions=para, n_iter=20, cv=3, n_jobs=-1, verbose=1, random_state=42)
                rs.fit(X_train, y_train)
                best_model = rs.best_estimator_
            else:
                model.fit(X_train, y_train)
                best_model = model

            tuned_models[model_name] = best_model  # ✅ Store tuned model

            y_train_pred = best_model.predict(X_train)
            y_test_pred = best_model.predict(X_test)

            train_model_score = np.sqrt(mean_squared_error(y_train, y_train_pred))
            test_model_score = np.sqrt(mean_squared_error(y_test, y_test_pred))

            report[model_name] = test_model_score

        return report, tuned_models  # ✅ Return both

    
    # def train_model(self, X_train, y_train, X_test, y_test):
    def train_model(self):
        models = {
            "Linear Regression": LinearRegression(), 
            "Ridge Regression": Ridge(), 
            "Decision Tree": DecisionTreeRegressor(), 
            "Random Forest": RandomForestRegressor(verbose=1), 
            "Gradiant Boosting": GradientBoostingRegressor(verbose=1), 
        }

        model_params = {
            "Linear Regression": {},

            "Decision Tree": {
                "max_depth": [None, 5, 10],
                "min_samples_split": [2, 5, 10, 20],
                "min_samples_leaf": [1, 5, 10, 20],
                "max_features": ["sqrt", "log2"],
                "criterion": ["squared_error", "friedman_mse"]
            },

            "Random Forest": {
                "n_estimators": [100, 200],
                "max_depth": [None, 5, 10],
                "min_samples_split": [2, 5],
                "min_samples_leaf": [1, 2, 4],
                "max_features": ["sqrt", "log2"],
                "bootstrap": [True, False]
            },

            "Gradient Boosting": {
                "n_estimators": [100, 200],
                "learning_rate": [0.01, 0.1],
                "max_depth": [3, 5],
                "min_samples_split": [2, 5],
                "min_samples_leaf": [1, 3],
                "max_features": ["sqrt", "log2"],
                "subsample": [0.7, 0.8]
            },

            "Ridge Regression": {
                "alpha": [0.001, 0.01]
            }
        }

        model_report, tuned_models  = self.evaluate_models(X_train=self.X_train, y_train=self.y_train, X_test=self.X_test, y_test=self.y_test, models=models, params=model_params)

        ## To get best model score from dict 
        # best_model_score = max(sorted(model_report.values()))
        best_model_score = min(sorted(model_report.values()))

        ## To get best model name from dict 
        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]

        # print(best_model_name)
        logging.info(f"Best model found: {best_model_name}")

        # best_model = models[best_model_name] 
        best_model = tuned_models[best_model_name]
        best_params = best_model.get_params()

        y_train_pred = best_model.predict(self.X_train)
        y_test_pred = best_model.predict(self.X_test)
        # classification_test_metric=get_classification_score(y_true=y_test, y_pred=y_test_pred)

        train_mse = mean_squared_error(self.y_train, y_train_pred)
        train_rmse = np.sqrt(train_mse)
        train_r2 = r2_score(self.y_train, y_train_pred)

        train_reg_metrix = RegressionMetrixArtifacts(
             mse=train_mse, 
             rmse=train_rmse, 
             r2_score=train_r2
        )

        test_mse = mean_squared_error(self.y_test, y_test_pred)
        test_rmse = np.sqrt(test_mse)
        test_r2 = r2_score(self.y_test, y_test_pred)

        test_reg_metrix = RegressionMetrixArtifacts(
             mse=test_mse, 
             rmse=test_rmse, 
             r2_score=test_r2
        )

        model_trainer_artifact = ModelTrainerArtifact(
             trained_model=best_model,
             best_model_name=best_model_name, 
             best_model_parameters=best_params, 
             models_report=model_report, 
             train_metric_artifact=train_reg_metrix, 
             test_metric_artifact=test_reg_metrix
             )

        return model_trainer_artifact