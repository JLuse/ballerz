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
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.baseline_model import BaselineModel
from src.data.nfl_data_integration import NFLDataIntegrator
from src.features.feature_engineering import FeatureEngineer
from src.data.player_metadata import PlayerMetadataIntegrator


class PlayerPredictor:
    """Interactive tool for predicting player performance."""
    
    def __init__(self, model_path: str = "outputs/models/baseline_rf_model.joblib"):
        """Initialize the predictor with a trained model."""
        self.model_path = Path(model_path)
        self.model = None
        self.feature_engineer = FeatureEngineer()
        # Load player metadata to recognize known players
        try:
            self.player_metadata = PlayerMetadataIntegrator()
            self.known_players = set(self.player_metadata.metadata_df['Player'].astype(str).str.strip().unique())
        except Exception:
            self.player_metadata = None
            self.known_players = set()
        
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
        """Get player data for prediction.
        Tries real history first; falls back to sample if unavailable.
        """
        try:
            # Load recent player data
            integrator = NFLDataIntegrator()
            
            print(f"🔍 Looking for data for {player_name}...")

            # Try to assemble history: last K weeks spanning seasons
            K = 6
            seasons = sorted({season, season-1})
            weeks = list(range(1, 19))
            history = integrator.load_player_history(player_name, ["RB","WR","QB","TE"], seasons, weeks)
            if not history.empty:
                # Keep only needed columns and sort
                history = history.sort_values(["season","week"]).reset_index(drop=True)

                # For feature engineering, include simplified base stats for past rows
                # Ensure required base columns exist
                for base, source in [
                    ('rushing_yards','RushingYDS_actual'),
                    ('rushing_touchdowns','RushingTD_actual'),
                    ('receptions','ReceivingRec_actual'),
                    ('receiving_yards','ReceivingYDS_actual'),
                    ('receiving_touchdowns','ReceivingTD_actual'),
                    ('fumbles_lost','Fum_actual'),
                    ('carries','TouchCarries'),
                    ('targets','TargetsReceptions'),
                ]:
                    if base not in history.columns and source in history.columns:
                        history[base] = history[source]

                # Determine if requested current week exists in data
                has_current = not history[
                    (history['season'] == season) & (history['week'] == week)
                ].empty

                if has_current:
                    # Use history up to and including the current row
                    mask = (history['season'] < season) | ((history['season'] == season) & (history['week'] <= week))
                    subset = history[mask]
                    # Keep last K rows to compute rolling features
                    data_for_inference = subset.tail(K).reset_index(drop=True)
                else:
                    # Build a current-week row using last known context and projection
                    current = {
                        'player_name': player_name,
                        'season': season,
                        'week': week,
                        'team': history.iloc[-1]['team'],
                        'position': history.iloc[-1]['position'],
                        'opponent': history.iloc[-1]['opponent'] if 'opponent' in history.columns else 'UNK',
                        'projection': history.iloc[-1]['projection'] if 'projection' in history.columns else float(history['projection'].tail(1).fillna(0))
                    }
                    current_df = pd.DataFrame([current])
                    data_for_inference = pd.concat([history.tail(K-1), current_df], ignore_index=True, sort=False)

                # Attach age/experience features to align with trained model
                try:
                    if self.player_metadata is not None:
                        data_for_inference = self.player_metadata.add_player_metadata(data_for_inference)
                        data_for_inference = self.player_metadata.create_age_features(data_for_inference)
                except Exception:
                    # If metadata fails, continue without it; downstream will fill NaNs
                    pass

                return data_for_inference

            # Fallback: synthetic sample
            sample_data = self.create_sample_player_data(player_name, week, season)
            return sample_data
            
        except Exception as e:
            print(f"❌ Error getting player data: {e}")
            return None
    
    def create_sample_player_data(self, player_name: str, week: int, season: int) -> pd.DataFrame:
        """Create varied sample player data for demonstration."""
        # Create different data based on player name to simulate real differences
        import hashlib
        
        # Be conservative: assume unknown unless we positively match a known player
        unknown_player = True
        if self.known_players:
            # Basic membership check (case-insensitive)
            name_norm = player_name.strip().lower()
            unknown_player = all(p.lower() != name_norm for p in self.known_players)
        
        # Use player name to generate consistent but different data
        name_hash = int(hashlib.md5(player_name.encode()).hexdigest()[:8], 16)
        np.random.seed(name_hash + week + season)  # Consistent but varied per player
        
        # Generate varied stats based on player name
        if unknown_player:
            # For unknown players, simulate very low usage
            base_rushing = 5 + (name_hash % 6)   # 5-10 yards
            base_receiving = 2 + (name_hash % 3) # 2-4 yards
            base_projection = 1 + (name_hash % 2) # 1-2 points
        else:
            base_rushing = 80 + (name_hash % 60)  # 80-140 yards
            base_receiving = 20 + (name_hash % 40)  # 20-60 yards
            base_projection = 12 + (name_hash % 8)  # 12-20 points
        
        # Add some randomness
        rushing_yards = max(0, base_rushing + np.random.randint(-2 if unknown_player else -20, (3 if unknown_player else 21)))
        receiving_yards = max(0, base_receiving + np.random.randint(-1 if unknown_player else -10, (2 if unknown_player else 11)))
        rushing_tds = 0 if unknown_player else np.random.randint(0, 3)
        receiving_tds = 0 if unknown_player else np.random.randint(0, 2)
        carries = max(0 if unknown_player else 10, (rushing_yards // (20 if unknown_player else 4)) + (0 if unknown_player else np.random.randint(-3, 4)))
        receptions = max(0, (receiving_yards // (20 if unknown_player else 8)) + (0 if unknown_player else np.random.randint(-1, 2)))
        targets = max(receptions, receptions + (0 if unknown_player else np.random.randint(0, 3)))
        fumbles = 0 if unknown_player else np.random.randint(0, 2)
        
        # Calculate fantasy points (standard scoring)
        fantasy_points = (
            rushing_yards * 0.1 +
            rushing_tds * 6 +
            receptions * 1 +
            receiving_yards * 0.1 +
            receiving_tds * 6 -
            fumbles * 2
        )
        
        # Vary projection based on player performance
        projection = max(0.1, base_projection + (0 if unknown_player else np.random.randint(-3, 4)))
        
        # Determine team based on player name (simplified)
        teams = ['CIN', 'SF', 'LAC', 'NYG', 'TEN', 'CLE', 'LV', 'DET', 'NO', 'NYJ']
        team = teams[name_hash % len(teams)]
        
        # Determine opponent (simplified)
        opponents = ['BAL', 'PIT', 'CLE', 'CIN', 'BUF', 'MIA', 'NE', 'NYJ', 'KC', 'DEN']
        opponent = opponents[(name_hash + week) % len(opponents)]
        
        # Generate age and experience data
        base_age = 24 + (name_hash % 8)  # 24-32 years old
        age = base_age + (season - 2022)  # Age increases with seasons
        games_played = 48 + (name_hash % 64) + (season - 2022) * 16  # Experience increases
        games_started = games_played * 0.7  # Rough estimate of starts
        
        sample_data = pd.DataFrame({
            'player_name': [player_name],
            'week': [week],
            'season': [season],
            'position': ['RB'],
            'team': [team],
            'opponent': [opponent],
            # Actual performance stats (matching NFL data column names)
            'PassingYDS_actual': [0],
            'PassingTD_actual': [0],
            'PassingInt_actual': [0],
            'RushingYDS_actual': [rushing_yards],
            'RushingTD_actual': [rushing_tds],
            'ReceivingRec_actual': [receptions],
            'ReceivingYDS_actual': [receiving_yards],
            'ReceivingTD_actual': [receiving_tds],
            'RetTD_actual': [0],
            'FumTD_actual': [0],
            '2PT_actual': [0],
            'Fum_actual': [fumbles],
            'FanPtsAgainst-pts': [0],
            'TouchReceptions': [receptions],
            'Touches': [carries + receptions],
            'TargetsReceptions': [targets],
            'targets': [targets],
            'carries': [carries],
            'ReceptionPercentage': [receptions / max(targets, 1) * 100],
            'RzTarget': [0],
            'RzTouch': [0],
            'RzG2G': [0],
            'Rank_actual': [0],
            'TotalPoints_actual': [fantasy_points],
            # Projected stats
            'PassingYDS_projected': [0],
            'PassingTD_projected': [0],
            'PassingInt_projected': [0],
            'RushingYDS_projected': [rushing_yards * 0.9],
            'RushingTD_projected': [rushing_tds],
            'ReceivingRec_projected': [receptions],
            'ReceivingYDS_projected': [receiving_yards * 0.9],
            'ReceivingTD_projected': [receiving_tds],
            'RetTD_projected': [0],
            'FumTD_projected': [0],
            '2PT_projected': [0],
            'Fum_projected': [fumbles],
            'PlayerWeekProjectedPts': [projection],
            'Rank_projected': [0],
            'TotalPoints_projected': [projection],
            'ProjectionDiff': [fantasy_points - projection],
            # Additional required columns
            'fantasy_points': [fantasy_points],
            'projection': [projection],
            'over_performed': [1 if fantasy_points > projection else 0],
            # Age and experience data
            'player_age': [age],
            'games_played': [games_played],
            'games_started': [games_started],
            'is_rookie': [1 if age <= 23 else 0],
            'is_veteran': [1 if age >= 30 else 0],
            'is_prime_age': [1 if 25 <= age <= 28 else 0],
            'is_experienced': [1 if games_played >= 48 else 0],
            'games_per_season': [games_played / max(season - 2015, 1)]
        })
        
        # Add simplified base columns expected by feature engineering
        sample_data['rushing_yards'] = sample_data['RushingYDS_actual']
        sample_data['rushing_touchdowns'] = sample_data['RushingTD_actual']
        sample_data['receptions'] = sample_data['ReceivingRec_actual']
        sample_data['receiving_yards'] = sample_data['ReceivingYDS_actual']
        sample_data['receiving_touchdowns'] = sample_data['ReceivingTD_actual']
        sample_data['fumbles_lost'] = sample_data['Fum_actual']
        
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
            # If we have multiple rows (history + current), use inference pipeline
            if len(player_data) > 1:
                engineered_all = self.feature_engineer.engineer_features_for_inference(player_data)
                # pick the last row (current week)
                engineered_data = engineered_all.tail(1)
            else:
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
            # Usage guard inputs
            touches = 0
            try:
                base_carries = engineered_data.iloc[0].get('carries', 0)
                base_receptions = engineered_data.iloc[0].get('receptions', 0)
                touches = int((0 if pd.isna(base_carries) else base_carries) + (0 if pd.isna(base_receptions) else base_receptions))
            except Exception:
                touches = 0
            
            # Determine the correct projection for the requested (season, week)
            proj_value = None
            try:
                if 'projection' in player_data.columns:
                    mask_cur = (player_data['season'] == season) & (player_data['week'] == week)
                    if mask_cur.any():
                        proj_value = float(player_data.loc[mask_cur, 'projection'].iloc[0])
                    else:
                        proj_value = float(player_data['projection'].tail(1).iloc[0])
            except Exception:
                proj_value = None

            # Build simple human-readable reasons
            reasons = self.get_simple_explanations(engineered_data.iloc[0], touches, float(proj_value if proj_value is not None else 0.0))

            return {
                "player_name": player_name,
                "week": week,
                "season": season,
                "projection": proj_value if proj_value is not None else float(engineered_data.iloc[0].get('projection', 0.0)),
                "prediction": prediction,
                "over_perform_probability": probability[1] if len(probability) > 1 else probability[0],
                "confidence": self.get_confidence_level(probability[1] if len(probability) > 1 else probability[0]),
                "recommendation": self.get_recommendation(
                    prediction,
                    probability[1] if len(probability) > 1 else probability[0],
                    touches,
                    float(proj_value if proj_value is not None else engineered_data.iloc[0].get('projection', 0.0))
                ),
                "key_features": self.get_key_features(engineered_data.iloc[0], feature_importance),
                "reasons": reasons
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
    
    def get_recommendation(self, prediction: int, probability: float, touches: int, projection: float) -> str:
        """Get recommendation based on prediction, with simple usage/projection guardrails."""
        # Guard 1: very low projected usage
        if touches < 3 or projection < 6.0:
            return "AVOID"

        if prediction == 1:
            return "STRONG START" if probability >= 0.7 else "CONSIDER STARTING"
        else:
            return "AVOID" if probability >= 0.7 else "CONSIDER BENCHING"
    
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

    def get_simple_explanations(self, row: pd.Series, touches: int, projection: float) -> list:
        """Create simple reasons for the recommendation based on a few intuitive signals.
        Falls back gracefully if any field is missing.
        """
        reasons = []
        try:
            proj_vs_recent = float(row.get('projection_vs_recent', 0.0))
            proj_conf = float(row.get('projection_confidence', 0.0))
            fp_trend = float(row.get('fantasy_points_trend_3v3', 0.0)) if 'fantasy_points_trend_3v3' in row.index else None
            ry_trend = float(row.get('rushing_yards_trend_3v3', 0.0)) if 'rushing_yards_trend_3v3' in row.index else None
            rec_trend = float(row.get('receptions_trend_3v3', 0.0)) if 'receptions_trend_3v3' in row.index else None

            # Reason 1: Projection vs recent performance
            if proj_vs_recent is not None:
                if proj_vs_recent > 0:
                    reasons.append(f"Projection ({projection:.1f}) is above recent average by {proj_vs_recent:.1f}.")
                elif proj_vs_recent < 0:
                    reasons.append(f"Projection ({projection:.1f}) is below recent average by {abs(proj_vs_recent):.1f}.")

            # Reason 2: Usage
            if touches is not None:
                if touches >= 12:
                    reasons.append(f"Solid recent usage (~{touches} touches).")
                elif touches <= 3:
                    reasons.append("Very low recent usage.")

            # Reason 3: Trend
            trend_msgs = []
            if fp_trend is not None:
                trend_msgs.append("fantasy points" + (" trending up" if fp_trend > 0 else " trending down"))
            if ry_trend is not None:
                trend_msgs.append("rushing" + (" trending up" if ry_trend > 0 else " trending down"))
            if rec_trend is not None:
                trend_msgs.append("receiving" + (" trending up" if rec_trend > 0 else " trending down"))
            if trend_msgs:
                reasons.append(", ".join(trend_msgs).capitalize() + ".")

            # Reason 4: Projection confidence (volatility)
            if proj_conf is not None:
                if proj_conf >= 0.7:
                    reasons.append("Low recent volatility (higher confidence).")
                elif proj_conf <= 0.3:
                    reasons.append("High recent volatility (lower confidence).")
        except Exception:
            pass

        return [r for r in reasons if r]
    
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
        
        # Simple reasons/explanations
        reasons = result.get('reasons', [])
        if reasons:
            print("\n📝 Why this recommendation:")
            for r in reasons:
                print(f"  - {r}")
        
        print("\n" + "=" * 50)


def main():
    """Main function for the interactive predictor."""
    parser = argparse.ArgumentParser(description="Fantasy Football Player Predictor")
    parser.add_argument("--player", "-p", required=True, help="Player name (e.g., 'Christian McCaffrey')")
    parser.add_argument("--week", "-w", type=int, required=True, help="Week number (1-18)")
    parser.add_argument("--season", "-s", type=int, default=2023, help="Season year (default: 2023)")
    parser.add_argument("--model", "-m", default="outputs/models/baseline_rf_model.joblib", help="Path to trained model")
    
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
