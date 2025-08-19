#!/usr/bin/env python3
"""
Training script using real NFL data from the hvpkod/NFL-Data repository.
This script demonstrates how to use actual fantasy football data for model training.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.nfl_data_integration import NFLDataIntegrator
from src.features.feature_engineering import FeatureEngineer
from src.models.baseline_model import BaselineModel
from src.utils.config import load_config, ensure_directories


def main():
    """
    Run the complete fantasy football analytics pipeline with real NFL data.
    """
    print("=" * 60)
    print("FANTASY FOOTBALL ANALYTICS - REAL NFL DATA TRAINING")
    print("=" * 60)
    
    # Load configuration
    print("\n1. Loading configuration...")
    config = load_config()
    ensure_directories(config)
    
    # Step 1: Integrate Real NFL Data
    print("\n2. Integrating real NFL data...")
    integrator = NFLDataIntegrator()
    
    # Check available data
    available_data = integrator.get_available_data()
    print(f"Available seasons: {list(available_data.keys())}")
    
    # Collect offensive position data with age information (excluding defensive positions DB, LB)
    print("\n3. Collecting offensive position data with age for 2022-2023...")
    offensive_data = integrator.collect_offensive_positions_data_with_age(
        positions=["RB", "WR", "QB", "TE"],  # Offensive positions only
        seasons=[2022, 2023], 
        weeks=list(range(1, 19))  # All weeks
    )
    
    # Save raw integrated data
    integrator.save_integrated_data(offensive_data, "OFFENSIVE", "nfl_offensive_2022_2023.csv")
    
    # Step 2: Feature Engineering
    print("\n4. Engineering features...")
    engineer = FeatureEngineer()
    engineered_data = engineer.engineer_all_features(offensive_data)
    
    # Save engineered data
    engineer.save_engineered_data(engineered_data, "nfl_offensive_engineered.csv")
    
    # Step 3: Model Training and Evaluation
    print("\n5. Training baseline model...")
    model = BaselineModel()
    results = model.train_and_evaluate("data/processed/nfl_offensive_engineered.csv")
    
    # Step 4: Results Summary
    print("\n" + "=" * 60)
    print("REAL NFL DATA TRAINING RESULTS")
    print("=" * 60)
    
    print(f"Cross-validation accuracy: {results['cv_accuracy_mean']:.3f} (+/- {results['cv_accuracy_std'] * 2:.3f})")
    
    if 'test_accuracy' in results:
        print(f"Test set accuracy: {results['test_accuracy']:.3f}")
        print(f"Test set AUC: {results['test_auc']:.3f}")
    
    print(f"\nModel saved to: {results['model_path']}")
    
    # Feature importance summary
    if 'feature_importance' in results:
        print("\nTop 10 Most Important Features:")
        for i, feature in enumerate(results['feature_importance'][:10]):
            print(f"  {i+1}. {feature['feature']}: {feature['importance']:.4f}")
    
    # Data quality insights
    print(f"\nData Quality Insights:")
    print(f"- Total records: {len(engineered_data)}")
    print(f"- Unique players: {engineered_data['player_name'].nunique()}")
    print(f"- Positions: {engineered_data['position'].unique()}")
    print(f"- Seasons: {engineered_data['season'].unique()}")
    print(f"- Target distribution: {engineered_data['target'].value_counts().to_dict()}")
    
    # Age data insights
    if 'player_age' in engineered_data.columns:
        age_data = engineered_data['player_age'].dropna()
        if not age_data.empty:
            print(f"- Players with age data: {len(age_data.unique())}")
            print(f"- Average player age: {age_data.mean():.1f}")
            print(f"- Age range: {age_data.min():.0f}-{age_data.max():.0f}")
            print(f"- Age categories: {engineered_data['age_category'].value_counts().to_dict()}")
    
    print("\n" + "=" * 60)
    print("REAL DATA PIPELINE COMPLETE!")
    print("=" * 60)
    
    print("\nKey Differences from Sample Data:")
    print("1. Real performance patterns and variance")
    print("2. Actual projection accuracy challenges")
    print("3. More realistic model performance metrics")
    print("4. Real player names and teams")
    print("5. Actual opponent matchups")
    print("6. Multiple offensive positions (RB, WR, QB, TE)")
    print("7. Excludes defensive positions (DB, LB)")
    print("8. Player age and experience data")
    print("9. Age-based feature engineering")
    
    print("\nNext steps:")
    print("1. Analyze feature importance for real insights")
    print("2. Add opponent defensive stats")
    print("3. Include weather and injury data")
    print("4. Try different algorithms")
    print("5. Expand to other positions")
    
    return results


if __name__ == "__main__":
    try:
        results = main()
    except Exception as e:
        print(f"\nError during training: {e}")
        print("Please check your configuration and data files.")
        sys.exit(1)
