"""
Feature engineering module for fantasy football analytics.
Creates predictive features from raw player performance data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path

from ..utils.config import load_config, get_feature_config, get_data_paths


class FeatureEngineer:
    """
    Creates features for fantasy football prediction models.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the feature engineer.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.feature_config = get_feature_config(self.config)
        self.paths = get_data_paths(self.config)
        
    def create_rolling_features(self, df: pd.DataFrame, player_col: str = 'player_name') -> pd.DataFrame:
        """
        Create rolling average features for each player.
        
        Args:
            df: DataFrame with player performance data
            player_col: Column name for player identifier
            
        Returns:
            DataFrame with rolling features added
        """
        print("Creating rolling average features...")
        
        # Sort by player, season, week for proper rolling calculations
        df = df.sort_values([player_col, 'season', 'week']).reset_index(drop=True)
        
        # Get rolling windows from config
        rolling_windows = self.feature_config.get('rolling_windows', [3, 5])
        
        # Features to create rolling averages for
        stat_columns = [
            'rushing_yards', 'rushing_touchdowns', 'receptions', 
            'receiving_yards', 'receiving_touchdowns', 'fantasy_points'
        ]
        
        for window in rolling_windows:
            for stat in stat_columns:
                if stat in df.columns:
                    # Rolling average
                    col_name = f'{stat}_rolling_{window}'
                    df[col_name] = df.groupby(player_col)[stat].transform(
                        lambda x: x.rolling(window=window, min_periods=1).mean()
                    )
                    
                    # Rolling standard deviation (volatility)
                    col_name_std = f'{stat}_rolling_{window}_std'
                    df[col_name_std] = df.groupby(player_col)[stat].transform(
                        lambda x: x.rolling(window=window, min_periods=2).std().fillna(0)
                    )
        
        return df
    
    def create_trend_features(self, df: pd.DataFrame, player_col: str = 'player_name') -> pd.DataFrame:
        """
        Create trend features showing recent performance direction.
        
        Args:
            df: DataFrame with player performance data
            player_col: Column name for player identifier
            
        Returns:
            DataFrame with trend features added
        """
        print("Creating trend features...")
        
        # Sort by player, season, week
        df = df.sort_values([player_col, 'season', 'week']).reset_index(drop=True)
        
        # Create trend features for key stats
        trend_stats = ['fantasy_points', 'rushing_yards', 'receptions']
        
        for stat in trend_stats:
            if stat in df.columns:
                # Recent vs previous performance (last 3 vs previous 3)
                df[f'{stat}_trend_3v3'] = df.groupby(player_col)[stat].transform(
                    lambda x: x.rolling(3, min_periods=3).mean() - 
                             x.rolling(6, min_periods=6).mean().shift(3)
                )
                
                # Week-over-week change
                df[f'{stat}_week_change'] = df.groupby(player_col)[stat].diff()
                
                # Performance consistency (lower std = more consistent)
                df[f'{stat}_consistency'] = df.groupby(player_col)[stat].transform(
                    lambda x: 1 / (1 + x.rolling(5, min_periods=3).std())
                )
        
        return df
    
    def create_projection_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features related to projections and expectations.
        
        Args:
            df: DataFrame with projection data
            
        Returns:
            DataFrame with projection features added
        """
        print("Creating projection-related features...")
        
        if 'projection' in df.columns:
            # Projection accuracy in recent weeks
            df['projection_error'] = df['fantasy_points'] - df['projection']
            
            # Rolling projection accuracy
            df['projection_accuracy_rolling_5'] = df.groupby('player_name')['projection_error'].transform(
                lambda x: x.rolling(5, min_periods=3).mean()
            )
            
            # Projection vs recent performance
            df['projection_vs_recent'] = df['projection'] - df['fantasy_points_rolling_3']
            
            # Projection confidence (based on recent volatility)
            df['projection_confidence'] = 1 / (1 + df['fantasy_points_rolling_3_std'])
        
        return df
    
    def create_context_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create contextual features like season week, home/away, etc.
        
        Args:
            df: DataFrame with player data
            
        Returns:
            DataFrame with context features added
        """
        print("Creating contextual features...")
        
        # Season week (1-18)
        df['season_week'] = df['week']
        
        # Late season indicator (weeks 14-18 are fantasy playoffs)
        df['late_season'] = (df['week'] >= 14).astype(int)
        
        # Early season indicator (weeks 1-4)
        df['early_season'] = (df['week'] <= 4).astype(int)
        
        # Bye week recovery (week after bye)
        df['post_bye'] = 0  # Placeholder - would need bye week data
        
        # Create dummy variables for teams
        if 'team' in df.columns:
            team_dummies = pd.get_dummies(df['team'], prefix='team')
            df = pd.concat([df, team_dummies], axis=1)
        
        return df
    
    def create_target_variable(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create the target variable for classification.
        
        Args:
            df: DataFrame with performance data
            
        Returns:
            DataFrame with target variable added
        """
        print("Creating target variable...")
        
        if 'over_performed' in df.columns:
            # Use existing over_performed column
            df['target'] = df['over_performed'].astype(int)
        elif 'fantasy_points' in df.columns and 'projection' in df.columns:
            # Create target based on fantasy points vs projection
            df['target'] = (df['fantasy_points'] > df['projection']).astype(int)
        else:
            raise ValueError("Need either 'over_performed' column or both 'fantasy_points' and 'projection' columns")
        
        return df
    
    def engineer_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all feature engineering steps to the dataset.
        
        Args:
            df: Raw DataFrame with player performance data
            
        Returns:
            DataFrame with all engineered features
        """
        print("Starting comprehensive feature engineering...")
        
        # Make a copy to avoid modifying original
        df_engineered = df.copy()
        
        # Apply feature engineering steps
        df_engineered = self.create_rolling_features(df_engineered)
        df_engineered = self.create_trend_features(df_engineered)
        df_engineered = self.create_projection_features(df_engineered)
        df_engineered = self.create_context_features(df_engineered)
        df_engineered = self.create_target_variable(df_engineered)
        
        # Handle missing values more carefully
        initial_rows = len(df_engineered)
        
        # Fill NaN values with 0 for numeric columns (except target)
        numeric_cols = df_engineered.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in numeric_cols if col != 'target']
        df_engineered[numeric_cols] = df_engineered[numeric_cols].fillna(0)
        
        # Drop rows where target is missing (these are essential)
        df_engineered = df_engineered.dropna(subset=['target'])
        final_rows = len(df_engineered)
        
        print(f"Feature engineering complete!")
        print(f"Initial rows: {initial_rows}, Final rows: {final_rows}")
        print(f"Features created: {len(df_engineered.columns)} total columns")
        
        return df_engineered
    
    def get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of feature columns (excluding target and metadata).
        
        Args:
            df: DataFrame with engineered features
            
        Returns:
            List of feature column names
        """
        # Columns to exclude
        exclude_cols = {
            'target', 'player_name', 'team', 'position', 'season', 'week',
            'fantasy_points', 'projection', 'over_performed', 'performance_diff',
            'player_id', 'opponent'  # Also exclude categorical columns
        }
        
        # Only include numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        print(f"Identified {len(feature_cols)} numeric feature columns")
        return feature_cols
    
    def save_engineered_data(self, df: pd.DataFrame, filename: str = "engineered_rb_data.csv") -> Path:
        """
        Save engineered data to processed data directory.
        
        Args:
            df: Engineered DataFrame
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        output_path = self.paths['processed_data'] / filename
        df.to_csv(output_path, index=False)
        print(f"Engineered data saved to: {output_path}")
        return output_path


def main():
    """Main function to run feature engineering on sample data."""
    from ..data.collect_data import FantasyDataCollector
    
    # First collect data
    collector = FantasyDataCollector()
    data = collector.collect_all_data()
    rb_data = data['rb_performance']
    
    # Then engineer features
    engineer = FeatureEngineer()
    engineered_data = engineer.engineer_all_features(rb_data)
    
    # Save engineered data
    engineer.save_engineered_data(engineered_data)
    
    # Show feature summary
    feature_cols = engineer.get_feature_columns(engineered_data)
    print(f"\nFeature columns: {feature_cols[:10]}...")  # Show first 10


if __name__ == "__main__":
    main()
