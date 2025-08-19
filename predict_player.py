#!/usr/bin/env python3
"""
Interactive Player Prediction Tool
Predicts whether a player will over-perform their fantasy projection.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.models.baseline_model import BaselineModel
from src.data.nfl_data_integration import NFLDataIntegrator
from src.features.feature_engineering import FeatureEngineer


class PlayerPredictor:
    """Interactive tool for predicting player performance."""
    
    def __init__(self, model_path: str = "models/baseline_rf_model.joblib"):
        """Initialize the predictor with a trained model."""
        self.model_path = Path(model_path)
        self.model = None
        self.feature_engineer = FeatureEngineer()
        
        if not self.model_path.exists():
            print(f"❌ Model not found at {model_path}")
            print("💡 Please run 'python train_baseline.py' or 'python train_with_real_data.py' first")
            sys.exit(1)
        
        # Load the trained model
        self.load_model()
    
    def load_model(self):
        """Load the trained machine learning model."""
        try:
            self.model = BaselineModel()
            self.model.load_model(self.model_path)
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            sys.exit(1)
    
    def get_player_data(self, player_name: str, week: int, season: int = 2023) -> Optional[pd.DataFrame]:
        """Get player data for prediction."""
        try:
            # Load recent player data
            integrator = NFLDataIntegrator()
            
            # Get player's recent performance data
            # This is a simplified version - in practice, you'd need more sophisticated data loading
            print(f"🔍 Looking for data for {player_name}...")
            
            # For now, we'll create a sample prediction
            # In a real implementation, you'd load actual player data
            sample_data = self.create_sample_player_data(player_name, week, season)
            
            return sample_data
            
        except Exception as e:
            print(f"❌ Error getting player data: {e}")
            return None
    
    def create_sample_player_data(self, player_name: str, week: int, season: int) -> pd.DataFrame:
        """Create sample player data for demonstration."""
        # This is a placeholder - in reality, you'd load actual player data
        sample_data = pd.DataFrame({
            'player_name': [player_name],
            'week': [week],
            'season': [season],
            'position': ['RB'],  # Default to RB
            'team': ['UNK'],
            'opponent': ['UNK'],
            'rushing_yards': [100],
            'rushing_touchdowns': [1],
            'receptions': [3],
            'receiving_yards': [25],
            'receiving_touchdowns': [0],
            'fumbles_lost': [0],
            'carries': [20],
            'targets': [5],
            'fantasy_points': [18.5],
            'projection': [15.0],
            'player_id': [f"{player_name.lower().replace(' ', '_')}_{season}"]
        })
        
        return sample_data
    
    def predict_player(self, player_name: str, week: int, season: int = 2023) -> Dict:
        """Predict whether a player will over-perform their projection."""
        print(f"🏈 Predicting performance for {player_name} (Week {week}, {season})")
        print("=" * 50)
        
        # Get player data
        player_data = self.get_player_data(player_name, week, season)
        
        if player_data is None:
            return {"error": "Could not load player data"}
        
        # Engineer features
        print("🔧 Engineering features...")
        try:
            engineered_data = self.feature_engineer.engineer_all_features(player_data)
        except Exception as e:
            print(f"❌ Error engineering features: {e}")
            return {"error": f"Feature engineering failed: {e}"}
        
        # Make prediction
        print("🎯 Making prediction...")
        try:
            prediction = self.model.predict_single_player(engineered_data.iloc[0])
            probability = self.model.predict_proba_single_player(engineered_data.iloc[0])
            
            # Get feature importance for this prediction
            feature_importance = self.model.get_feature_importance()
            
            return {
                "player_name": player_name,
                "week": week,
                "season": season,
                "projection": player_data.iloc[0]['projection'],
                "prediction": prediction,
                "over_perform_probability": probability[1] if len(probability) > 1 else probability[0],
                "confidence": self.get_confidence_level(probability[1] if len(probability) > 1 else probability[0]),
                "recommendation": self.get_recommendation(prediction, probability[1] if len(probability) > 1 else probability[0]),
                "key_features": self.get_key_features(engineered_data.iloc[0], feature_importance)
            }
            
        except Exception as e:
            print(f"❌ Error making prediction: {e}")
            return {"error": f"Prediction failed: {e}"}
    
    def get_confidence_level(self, probability: float) -> str:
        """Get confidence level based on probability."""
        if probability >= 0.8:
            return "HIGH"
        elif probability >= 0.6:
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_recommendation(self, prediction: int, probability: float) -> str:
        """Get recommendation based on prediction."""
        if prediction == 1:
            if probability >= 0.7:
                return "STRONG START"
            else:
                return "CONSIDER STARTING"
        else:
            if probability >= 0.7:
                return "AVOID"
            else:
                return "CONSIDER BENCHING"
    
    def get_key_features(self, player_features: pd.Series, feature_importance: list) -> list:
        """Get key features that influenced the prediction."""
        # Get top 5 most important features
        top_features = feature_importance[:5]
        
        key_features = []
        for feature_info in top_features:
            feature_name = feature_info['feature']
            if feature_name in player_features.index:
                value = player_features[feature_name]
                key_features.append({
                    "feature": feature_name,
                    "value": value,
                    "importance": feature_info['importance']
                })
        
        return key_features
    
    def display_prediction(self, result: Dict):
        """Display the prediction results in a user-friendly format."""
        if "error" in result:
            print(f"❌ {result['error']}")
            return
        
        print("\n" + "=" * 50)
        print("🎯 PREDICTION RESULTS")
        print("=" * 50)
        
        print(f"Player: {result['player_name']}")
        print(f"Week: {result['week']} ({result['season']})")
        print(f"Projection: {result['projection']:.1f} fantasy points")
        print(f"Prediction: {'OVER-PERFORM' if result['prediction'] == 1 else 'UNDER-PERFORM'}")
        print(f"Confidence: {result['confidence']} ({result['over_perform_probability']:.1%})")
        print(f"Recommendation: {result['recommendation']}")
        
        if result['key_features']:
            print(f"\n🔍 Key Factors:")
            for feature in result['key_features']:
                print(f"  • {feature['feature']}: {feature['value']:.2f}")
        
        print("\n" + "=" * 50)


def main():
    """Main function for the interactive predictor."""
    parser = argparse.ArgumentParser(description="Fantasy Football Player Predictor")
    parser.add_argument("--player", "-p", required=True, help="Player name (e.g., 'Christian McCaffrey')")
    parser.add_argument("--week", "-w", type=int, required=True, help="Week number (1-18)")
    parser.add_argument("--season", "-s", type=int, default=2023, help="Season year (default: 2023)")
    parser.add_argument("--model", "-m", default="models/baseline_rf_model.joblib", help="Path to trained model")
    
    args = parser.parse_args()
    
    # Validate inputs
    if args.week < 1 or args.week > 18:
        print("❌ Week must be between 1 and 18")
        sys.exit(1)
    
    # Initialize predictor
    predictor = PlayerPredictor(args.model)
    
    # Make prediction
    result = predictor.predict_player(args.player, args.week, args.season)
    
    # Display results
    predictor.display_prediction(result)


if __name__ == "__main__":
    main()
