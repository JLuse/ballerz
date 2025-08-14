"""
Baseline model for fantasy football analytics.
Implements a Random Forest classifier to predict over/under performance.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, Dict, Any

from ..utils.config import load_config, get_model_config, get_data_paths
from ..features.feature_engineering import FeatureEngineer


class BaselineModel:
    """
    Baseline Random Forest model for fantasy football predictions.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the baseline model.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.model_config = get_model_config(self.config)
        self.paths = get_data_paths(self.config)
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        
    def load_data(self, data_path: str = "data/processed/engineered_rb_data.csv") -> pd.DataFrame:
        """
        Load engineered data for training.
        
        Args:
            data_path: Path to engineered data file
            
        Returns:
            DataFrame with engineered features
        """
        print(f"Loading data from: {data_path}")
        
        data_file = Path(data_path)
        if not data_file.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")
        
        df = pd.read_csv(data_file)
        print(f"Loaded {len(df)} records with {len(df.columns)} columns")
        
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features and target for training.
        
        Args:
            df: DataFrame with engineered features
            
        Returns:
            Tuple of (features, target)
        """
        print("Preparing features and target...")
        
        # Get feature columns
        engineer = FeatureEngineer()
        self.feature_columns = engineer.get_feature_columns(df)
        
        # Select features and target
        X = df[self.feature_columns].copy()
        y = df['target']
        
        # Handle missing values
        X = X.fillna(0)  # Simple imputation for MVP
        
        print(f"Prepared {len(X)} samples with {len(self.feature_columns)} features")
        print(f"Target distribution: {y.value_counts().to_dict()}")
        
        return X, y
    
    def train_model(self, X: pd.DataFrame, y: pd.Series) -> RandomForestClassifier:
        """
        Train the Random Forest model.
        
        Args:
            X: Feature matrix
            y: Target variable
            
        Returns:
            Trained Random Forest model
        """
        print("Training Random Forest model...")
        
        # Get model parameters from config
        rf_params = self.model_config.get('random_forest', {})
        
        # Create and train model
        self.model = RandomForestClassifier(
            n_estimators=rf_params.get('n_estimators', 100),
            max_depth=rf_params.get('max_depth', 10),
            min_samples_split=rf_params.get('min_samples_split', 5),
            min_samples_leaf=rf_params.get('min_samples_leaf', 2),
            random_state=self.model_config.get('random_state', 42),
            n_jobs=-1
        )
        
        # Train the model
        self.model.fit(X, y)
        
        print("Model training complete!")
        print(f"Model parameters: {self.model.get_params()}")
        
        return self.model
    
    def evaluate_model(self, X: pd.DataFrame, y: pd.Series, X_test: pd.DataFrame = None, y_test: pd.Series = None) -> Dict[str, float]:
        """
        Evaluate model performance using cross-validation and test set.
        
        Args:
            X: Training features
            y: Training target
            X_test: Test features (optional)
            y_test: Test target (optional)
            
        Returns:
            Dictionary of evaluation metrics
        """
        print("Evaluating model performance...")
        
        # Cross-validation
        cv_folds = self.config.get('evaluation', {}).get('cross_validation_folds', 5)
        cv_scores = cross_val_score(self.model, X, y, cv=cv_folds, scoring='accuracy')
        
        print(f"Cross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Test set evaluation (if provided)
        results = {
            'cv_accuracy_mean': cv_scores.mean(),
            'cv_accuracy_std': cv_scores.std(),
            'cv_accuracy_scores': cv_scores.tolist()
        }
        
        if X_test is not None and y_test is not None:
            # Make predictions on test set
            y_pred = self.model.predict(X_test)
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            test_accuracy = (y_pred == y_test).mean()
            test_auc = roc_auc_score(y_test, y_pred_proba)
            
            print(f"Test set accuracy: {test_accuracy:.3f}")
            print(f"Test set AUC: {test_auc:.3f}")
            
            # Classification report
            print("\nClassification Report:")
            print(classification_report(y_test, y_pred))
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            print("\nConfusion Matrix:")
            print(cm)
            
            results.update({
                'test_accuracy': test_accuracy,
                'test_auc': test_auc,
                'test_predictions': y_pred.tolist(),
                'test_probabilities': y_pred_proba.tolist()
            })
        
        return results
    
    def feature_importance_analysis(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze and display feature importance.
        
        Args:
            X: Feature matrix
            
        Returns:
            DataFrame with feature importance scores
        """
        print("Analyzing feature importance...")
        
        if self.model is None:
            raise ValueError("Model must be trained before analyzing feature importance")
        
        # Get feature importance
        importance = self.model.feature_importances_
        feature_importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Most Important Features:")
        print(feature_importance_df.head(10))
        
        return feature_importance_df
    
    def save_model(self, model_name: str = "baseline_rf_model.joblib") -> Path:
        """
        Save the trained model to disk.
        
        Args:
            model_name: Name of the model file
            
        Returns:
            Path to saved model file
        """
        if self.model is None:
            raise ValueError("No trained model to save")
        
        # Create models directory if it doesn't exist
        models_dir = self.paths['models']
        models_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model
        model_path = models_dir / model_name
        joblib.dump(self.model, model_path)
        
        # Save feature columns
        feature_path = models_dir / "feature_columns.txt"
        with open(feature_path, 'w') as f:
            for col in self.feature_columns:
                f.write(f"{col}\n")
        
        print(f"Model saved to: {model_path}")
        print(f"Feature columns saved to: {feature_path}")
        
        return model_path
    
    def train_and_evaluate(self, data_path: str = "data/processed/engineered_rb_data.csv") -> Dict[str, Any]:
        """
        Complete training and evaluation pipeline.
        
        Args:
            data_path: Path to engineered data
            
        Returns:
            Dictionary with training results and metrics
        """
        print("Starting complete training and evaluation pipeline...")
        
        # Load data
        df = self.load_data(data_path)
        
        # Prepare features
        X, y = self.prepare_features(df)
        
        # Split data
        test_size = self.model_config.get('test_size', 0.2)
        random_state = self.model_config.get('random_state', 42)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # Train model
        self.train_model(X_train, y_train)
        
        # Evaluate model
        results = self.evaluate_model(X_train, y_train, X_test, y_test)
        
        # Feature importance
        feature_importance = self.feature_importance_analysis(X_train)
        results['feature_importance'] = feature_importance.to_dict('records')
        
        # Save model
        model_path = self.save_model()
        results['model_path'] = str(model_path)
        
        print("\nTraining and evaluation complete!")
        return results


def main():
    """Main function to run the complete training pipeline."""
    model = BaselineModel()
    results = model.train_and_evaluate()
    
    print("\nTraining Results Summary:")
    print(f"CV Accuracy: {results['cv_accuracy_mean']:.3f} (+/- {results['cv_accuracy_std'] * 2:.3f})")
    if 'test_accuracy' in results:
        print(f"Test Accuracy: {results['test_accuracy']:.3f}")
        print(f"Test AUC: {results['test_auc']:.3f}")


if __name__ == "__main__":
    main()
