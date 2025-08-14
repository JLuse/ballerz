"""
NFL Data Integration Module
Integrates real NFL player data from the hvpkod/NFL-Data repository.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime

from ..utils.config import load_config, get_data_paths, ensure_directories


class NFLDataIntegrator:
    """
    Integrates real NFL data from the hvpkod/NFL-Data repository.
    """
    
    def __init__(self, nfl_data_path: str = "NFL-Data/NFL-data-Players", config_path: str = "config/config.yaml"):
        """
        Initialize the NFL data integrator.
        
        Args:
            nfl_data_path: Path to the NFL data repository
            config_path: Path to configuration file
        """
        self.nfl_data_path = Path(nfl_data_path)
        self.config = load_config(config_path)
        self.paths = get_data_paths(self.config)
        ensure_directories(self.config)
        
        if not self.nfl_data_path.exists():
            raise FileNotFoundError(f"NFL data path not found: {nfl_data_path}")
    
    def load_weekly_data(self, position: str = "RB", season: int = 2023, week: int = 1) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load weekly actual performance and projection data.
        
        Args:
            position: Player position (RB, WR, QB, TE, etc.)
            season: NFL season year
            week: Week number
            
        Returns:
            Tuple of (actual_data, projected_data)
        """
        season_path = self.nfl_data_path / str(season) / str(week)
        
        # Load actual performance data
        actual_file = season_path / f"{position}.csv"
        if not actual_file.exists():
            raise FileNotFoundError(f"Actual data file not found: {actual_file}")
        
        actual_data = pd.read_csv(actual_file)
        
        # Load projection data
        projected_file = season_path / "projected" / f"{position}_projected.csv"
        if not projected_file.exists():
            raise FileNotFoundError(f"Projection data file not found: {projected_file}")
        
        projected_data = pd.read_csv(projected_file)
        
        return actual_data, projected_data
    
    def load_season_data(self, position: str = "RB", season: int = 2023) -> pd.DataFrame:
        """
        Load season-level data.
        
        Args:
            position: Player position
            season: NFL season year
            
        Returns:
            DataFrame with season data
        """
        season_path = self.nfl_data_path / str(season)
        season_file = season_path / f"{position}_season.csv"
        
        if not season_file.exists():
            raise FileNotFoundError(f"Season data file not found: {season_file}")
        
        return pd.read_csv(season_file)
    
    def merge_weekly_data(self, actual_data: pd.DataFrame, projected_data: pd.DataFrame, 
                         season: int, week: int) -> pd.DataFrame:
        """
        Merge actual and projected weekly data.
        
        Args:
            actual_data: Actual performance data
            projected_data: Projection data
            season: Season year
            week: Week number
            
        Returns:
            Merged DataFrame
        """
        # Select key columns for merging
        merge_cols = ['PlayerName', 'PlayerId', 'Pos', 'Team', 'PlayerOpponent']
        
        # Merge on player identifiers
        merged = pd.merge(actual_data, projected_data, 
                         on=merge_cols, 
                         suffixes=('_actual', '_projected'))
        
        # Add metadata
        merged['season'] = season
        merged['week'] = week
        
        return merged
    
    def calculate_fantasy_points(self, df: pd.DataFrame, scoring_type: str = "standard") -> pd.DataFrame:
        """
        Use existing fantasy points from the data.
        
        Args:
            df: DataFrame with player stats
            scoring_type: Scoring system (standard, ppr, half_ppr)
            
        Returns:
            DataFrame with fantasy points added
        """
        df = df.copy()
        

        
        # Use existing fantasy points from the data
        df['fantasy_points'] = df['TotalPoints_actual']
        df['projection'] = df['PlayerWeekProjectedPts']
        
        # Calculate over/under performance
        df['over_performed'] = df['fantasy_points'] > df['projection']
        df['performance_diff'] = df['fantasy_points'] - df['projection']
        
        return df
    
    def collect_weekly_data(self, position: str = "RB", seasons: List[int] = None, 
                           weeks: List[int] = None) -> pd.DataFrame:
        """
        Collect weekly data across multiple seasons and weeks.
        
        Args:
            position: Player position
            seasons: List of seasons to collect
            weeks: List of weeks to collect (1-18)
            
        Returns:
            DataFrame with all weekly data
        """
        if seasons is None:
            seasons = [2022, 2023]
        
        if weeks is None:
            weeks = list(range(1, 19))  # Weeks 1-18
        
        all_data = []
        
        for season in seasons:
            for week in weeks:
                try:
                    # Load weekly data
                    actual_data, projected_data = self.load_weekly_data(position, season, week)
                    
                    # Merge data
                    merged_data = self.merge_weekly_data(actual_data, projected_data, season, week)
                    
                    # Calculate fantasy points
                    merged_data = self.calculate_fantasy_points(merged_data)
                    
                    all_data.append(merged_data)
                    
                except FileNotFoundError as e:
                    print(f"Warning: Could not load data for {season} Week {week}: {e}")
                    continue
        
        if not all_data:
            raise ValueError("No data could be loaded")
        
        # Combine all data
        combined_data = pd.concat(all_data, ignore_index=True)
        
        # Clean up column names
        combined_data = self.clean_column_names(combined_data)
        
        return combined_data
    
    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean up column names for consistency.
        
        Args:
            df: DataFrame to clean
            
        Returns:
            DataFrame with cleaned column names
        """
        df = df.copy()
        
        # Rename columns to match our expected format
        column_mapping = {
            'PlayerName': 'player_name',
            'PlayerId': 'player_id',
            'Pos': 'position',
            'Team': 'team',
            'PlayerOpponent': 'opponent',
            'RushingYDS': 'rushing_yards',
            'RushingTD': 'rushing_touchdowns',
            'ReceivingRec': 'receptions',
            'ReceivingYDS': 'receiving_yards',
            'ReceivingTD': 'receiving_touchdowns',
            'Fum': 'fumbles_lost',
            'TouchCarries': 'carries',
            'Targets': 'targets',
            'TotalPoints': 'total_points'
        }
        
        # Apply mapping for columns that exist
        existing_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_cols)
        
        return df
    
    def save_integrated_data(self, df: pd.DataFrame, position: str = "RB", 
                           filename: str = None) -> Path:
        """
        Save integrated data to processed data directory.
        
        Args:
            df: DataFrame to save
            position: Player position
            filename: Optional filename
            
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"nfl_{position.lower()}_data.csv"
        
        output_path = self.paths['processed_data'] / filename
        df.to_csv(output_path, index=False)
        
        print(f"Integrated NFL data saved to: {output_path}")
        print(f"Data shape: {df.shape}")
        print(f"Seasons: {df['season'].unique()}")
        print(f"Weeks: {df['week'].nunique()}")
        print(f"Players: {df['player_name'].nunique()}")
        
        return output_path
    
    def get_available_data(self) -> Dict[str, List[int]]:
        """
        Get information about available data.
        
        Returns:
            Dictionary with available seasons and positions
        """
        available_data = {}
        
        for season_dir in self.nfl_data_path.iterdir():
            if season_dir.is_dir() and season_dir.name.isdigit():
                season = int(season_dir.name)
                available_data[season] = []
                
                # Check what positions are available
                for file in season_dir.glob("*_season.csv"):
                    position = file.stem.replace("_season", "")
                    available_data[season].append(position)
        
        return available_data


def main():
    """Main function to test NFL data integration."""
    print("Testing NFL Data Integration...")
    
    try:
        integrator = NFLDataIntegrator()
        
        # Check available data
        available = integrator.get_available_data()
        print(f"Available data: {available}")
        
        # Collect RB data for 2023
        print("\nCollecting RB data for 2023...")
        rb_data = integrator.collect_weekly_data("RB", seasons=[2023], weeks=[1, 2, 3])
        
        # Save data
        integrator.save_integrated_data(rb_data, "RB", "nfl_rb_2023_weeks1-3.csv")
        
        print("\nSample data:")
        print(rb_data[['player_name', 'team', 'week', 'fantasy_points', 'projection', 'over_performed']].head())
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
