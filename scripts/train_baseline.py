#!/usr/bin/env python3
"""
Main training script for the fantasy football analytics baseline model.
Runs the complete pipeline: data collection -> feature engineering -> model training -> evaluation.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.collect_data import FantasyDataCollector
from src.features.feature_engineering import FeatureEngineer
from src.models.baseline_model import BaselineModel
from src.utils.config import load_config, ensure_directories


def main():
    """
    Run the complete fantasy football analytics pipeline.
    """
    print("=" * 60)
    print("FANTASY FOOTBALL ANALYTICS - BASELINE MODEL TRAINING")
    print("=" * 60)
    
    # Load configuration
    print("\n1. Loading configuration...")
    config = load_config()
    ensure_directories(config)
    
    # Step 1: Data Collection
    print("\n2. Collecting data...")
    collector = FantasyDataCollector()
    data = collector.collect_all_data()
    
    # Step 2: Feature Engineering
    print("\n3. Engineering features...")
    engineer = FeatureEngineer()
    rb_data = data['rb_performance']
    engineered_data = engineer.engineer_all_features(rb_data)
    
    # Save engineered data
    engineer.save_engineered_data(engineered_data)
    
    # Step 3: Model Training and Evaluation
    print("\n4. Training baseline model...")
    model = BaselineModel()
    results = model.train_and_evaluate()
    
    # Step 4: Results Summary
    print("\n" + "=" * 60)
    print("TRAINING RESULTS SUMMARY")
    print("=" * 60)
    
    print(f"Cross-validation accuracy: {results['cv_accuracy_mean']:.3f} (+/- {results['cv_accuracy_std'] * 2:.3f})")
    
    if 'test_accuracy' in results:
        print(f"Test set accuracy: {results['test_accuracy']:.3f}")
        print(f"Test set AUC: {results['test_auc']:.3f}")
    
    print(f"\nModel saved to: {results['model_path']}")
    
    # Feature importance summary
    if 'feature_importance' in results:
        print("\nTop 5 Most Important Features:")
        for i, feature in enumerate(results['feature_importance'][:5]):
            print(f"  {i+1}. {feature['feature']}: {feature['importance']:.4f}")
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("1. Review the model performance metrics")
    print("2. Analyze feature importance for insights")
    print("3. Consider adding more features (opponent stats, weather, etc.)")
    print("4. Try different algorithms (XGBoost, LightGBM)")
    print("5. Expand to other positions (WR, QB, TE)")
    
    return results


if __name__ == "__main__":
    try:
        results = main()
    except Exception as e:
        print(f"\nError during training: {e}")
        print("Please check your configuration and data files.")
        sys.exit(1)
