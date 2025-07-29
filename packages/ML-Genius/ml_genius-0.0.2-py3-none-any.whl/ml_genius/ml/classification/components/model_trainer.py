import os 
import sys 
import pandas as pd 
import numpy as np 
import logging

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import AdaBoostClassifier

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from ml_genius.ml.classification.entity.artifacts_entity import ClassificationMetricArtifact, ModelTrainerArtifact, DataTransformationArtifacts


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

            train_model_score = accuracy_score(y_train, y_train_pred)
            test_model_score = accuracy_score(y_test, y_test_pred)

            report[model_name] = test_model_score

        return report, tuned_models  # ✅ Return both

    
    # def train_model(self, X_train, y_train, X_test, y_test):
    def train_model(self):
        models = {
            "Logistic Regression": LogisticRegression(), 
            "KNN": KNeighborsClassifier(), 
            "Naive Bayes": GaussianNB(), 
            "Decision Tree": DecisionTreeClassifier(), 
            "Random Forest": RandomForestClassifier(verbose=1), 
            "Gradiant Boosting": GradientBoostingClassifier(verbose=1), 
            "ADA Boost": AdaBoostClassifier()
        }

        model_params = {
            "Logistic Regression": {
                'penalty': ['l1', 'l2', 'elasticnet'], 
                'C': np.logspace(-4, 4, 20), 
                'solver': ['liblinear', 'saga'], 
                'max_iter': [100, 200, 500, 1000] 
            },

            "KNN": {
                'n_neighbors': np.arange(1, 10), 
                'weights': ['uniform', 'distance'], 
                'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'], 
                'p': [1, 2] 
            }, 

            "Naive Bayes": {}, 

            "Decision Tree": {
                'criterion': ['gini', 'entropy'], 
                'max_depth': [5, 10, 15, 20], 
                'min_samples_split': [2, 5, 10], 
                'min_samples_leaf': [1, 2, 4], 
                'max_features': ['sqrt', 'log2'] 
            },

            "Random Forest": {
                'n_estimators': [50, 100, 200], 
                'max_depth': [5, 10, 15], 
                'min_samples_split': [2, 5, 10], 
                'min_samples_leaf': [1, 2, 4], 
                'max_features': ['sqrt', 'log2'], 
                'bootstrap': [True, False] 
            },

            "Gradient Boosting": {
                'n_estimators': [50, 100, 200, 300],
                'learning_rate': [0.01, 0.05, 0.1, 0.2],
                'max_depth': [3, 5, 7], 
                'subsample': [0.7, 0.8, 0.9, 1.0],
                'max_features': ['sqrt', 'log2'] 
            },

            "ADA Boost": {
                'n_estimators': [50, 100, 200, 300],
                'learning_rate': [0.01, 0.05, 0.1, 0.2],
                # 'base_estimator': [DecisionTreeClassifier(max_depth=1), DecisionTreeClassifier(max_depth=2)] # Consider a shallow Decision Tree.
            }
        }

        model_report, tuned_models  = self.evaluate_models(X_train=self.X_train, y_train=self.y_train, X_test=self.X_test, y_test=self.y_test, models=models, params=model_params)

        ## To get best model score from dict 
        # best_model_score = max(sorted(model_report.values()))
        best_model_score = max(sorted(model_report.values()))

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

        train_accuracy = accuracy_score(self.y_train, y_train_pred)
        train_precision = precision_score(self.y_train, y_train_pred)
        train_recall = recall_score(self.y_train, y_train_pred)
        train_f1score = f1_score(self.y_train, y_train_pred)

        train_cls_metrix = ClassificationMetricArtifact(
            accuracy=train_accuracy, 
            f1_score=train_f1score, 
            recall_score=train_recall, 
            precision_score=train_precision
        )

        test_accuracy = accuracy_score(self.y_test, y_test_pred)
        test_precision = precision_score(self.y_test, y_test_pred)
        test_recall = recall_score(self.y_test, y_test_pred)
        test_f1score = f1_score(self.y_test, y_test_pred)

        test_cls_metrix = ClassificationMetricArtifact(
            accuracy=test_accuracy, 
            f1_score=test_f1score, 
            recall_score=test_recall, 
            precision_score=test_precision
        )

        model_trainer_artifact = ModelTrainerArtifact(
             trained_model=best_model,
             best_model_name=best_model_name, 
             best_model_parameters=best_params, 
             models_report=model_report, 
             train_metric_artifact=train_cls_metrix, 
             test_metric_artifact=test_cls_metrix
             )

        return model_trainer_artifact