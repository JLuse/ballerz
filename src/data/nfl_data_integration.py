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
import subprocess
import sys
import argparse

from ..utils.config import load_config, get_data_paths, ensure_directories
from .player_metadata import PlayerMetadataIntegrator


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
            position: Player position (RB, WR, QB, TE only - excludes DB, LB)
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
    
    def collect_offensive_positions_data(self, positions: List[str] = None, 
                                       seasons: List[int] = None, 
                                       weeks: List[int] = None) -> pd.DataFrame:
        """
        Collect data for offensive positions only, excluding defensive positions (DB, LB).
        
        Args:
            positions: List of offensive positions (RB, WR, QB, TE)
            seasons: List of seasons to collect
            weeks: List of weeks to collect (1-18)
            
        Returns:
            DataFrame with all offensive position data
        """
        # Define offensive positions (exclude DB, LB)
        if positions is None:
            positions = ["RB", "WR", "QB", "TE"]
        
        # Filter out defensive positions
        offensive_positions = [pos for pos in positions if pos not in ["DB", "LB", "DEF", "DST"]]
        
        if seasons is None:
            seasons = [2022, 2023]
        
        if weeks is None:
            weeks = list(range(1, 19))  # Weeks 1-18
        
        all_data = []
        
        for position in offensive_positions:
            print(f"Collecting data for {position}...")
            try:
                position_data = self.collect_weekly_data(position, seasons, weeks)
                all_data.append(position_data)
                print(f"✅ Collected {len(position_data)} records for {position}")
            except Exception as e:
                print(f"⚠️  Warning: Could not collect data for {position}: {e}")
                continue
        
        if not all_data:
            raise ValueError("No offensive position data could be loaded")
        
        # Combine all offensive position data
        combined_data = pd.concat(all_data, ignore_index=True)
        
        # Clean up column names
        combined_data = self.clean_column_names(combined_data)
        
        print(f"✅ Total offensive position records: {len(combined_data)}")
        print(f"Positions included: {combined_data['position'].unique()}")
        
        return combined_data
    
    def collect_offensive_positions_data_with_age(self, positions: List[str] = None, 
                                                seasons: List[int] = None, 
                                                weeks: List[int] = None) -> pd.DataFrame:
        """
        Collect data for offensive positions with age and experience data.
        
        Args:
            positions: List of offensive positions (RB, WR, QB, TE)
            seasons: List of seasons to collect
            weeks: List of weeks to collect (1-18)
            
        Returns:
            DataFrame with all offensive position data including age
        """
        # First collect the regular data
        data = self.collect_offensive_positions_data(positions, seasons, weeks)
        
        # Add age and experience data
        print("\n🔗 Integrating player age and experience data...")
        metadata_integrator = PlayerMetadataIntegrator()
        data_with_age = metadata_integrator.add_player_metadata(data)
        
        # Create additional age-related features
        data_with_age = metadata_integrator.create_age_features(data_with_age)
        
        # Get age summary
        age_summary = metadata_integrator.get_player_age_summary(data_with_age)
        print(f"📊 Age data summary: {age_summary}")
        
        return data_with_age
    
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


def download_nfl_data():
    """Download NFL data repository if it doesn't exist."""
    nfl_data_path = Path("NFL-Data")
    
    if nfl_data_path.exists():
        print("✅ NFL-Data repository already exists")
        return True
    
    print("📥 Downloading NFL-Data repository...")
    try:
        subprocess.run([
            "git", "clone", "https://github.com/hvpkod/NFL-Data.git"
        ], check=True)
        print("✅ NFL-Data repository downloaded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error downloading NFL-Data: {e}")
        return False
    except FileNotFoundError:
        print("❌ Git not found. Please install Git and try again.")
        return False


def explore_data():
    """Explore the NFL data structure."""
    try:
        integrator = NFLDataIntegrator()
        
        print("🔍 Exploring NFL Data Structure...")
        print("=" * 50)
        
        # Check available data
        available = integrator.get_available_data()
        print(f"Available seasons: {list(available.keys())}")
        
        # Show data structure
        data_path = Path("NFL-Data/NFL-data-Players")
        if data_path.exists():
            print(f"\nData files in {data_path}:")
            for file in sorted(data_path.glob("*.csv")):
                print(f"  - {file.name}")
        
        # Test data loading
        print("\n🧪 Testing data loading...")
        data = integrator.collect_weekly_data("RB", seasons=[2021], weeks=[1, 2, 3])
        print(f"✅ Successfully loaded {len(data)} records")
        print(f"Columns: {list(data.columns)}")
        print(f"Sample data:\n{data.head()}")
        
    except Exception as e:
        print(f"❌ Error exploring data: {e}")


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(description="NFL Data Integration Tool")
    parser.add_argument("--download", action="store_true", 
                       help="Download NFL-Data repository")
    parser.add_argument("--explore", action="store_true", 
                       help="Explore data structure")
    parser.add_argument("--test", action="store_true", 
                       help="Test data integration")
    
    args = parser.parse_args()
    
    if args.download:
        download_nfl_data()
    elif args.explore:
        explore_data()
    elif args.test:
        print("🧪 Testing NFL Data Integration...")
        try:
            integrator = NFLDataIntegrator()
            
            # Check available data
            available = integrator.get_available_data()
            print(f"Available data: {available}")
            
            # Load and merge data
            data = integrator.collect_weekly_data("RB", seasons=[2021], weeks=[1, 2, 3])
            print(f"✅ Successfully loaded {len(data)} records")
            
            # Show sample
            print("\nSample data:")
            print(data[['player_name', 'team', 'week', 'fantasy_points', 'projection', 'over_performed']].head())
            
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        # Default behavior - test integration
        print("🧪 Testing NFL Data Integration...")
        try:
            integrator = NFLDataIntegrator()
            data = integrator.collect_weekly_data("RB", seasons=[2021], weeks=[1, 2, 3])
            print(f"✅ Successfully loaded {len(data)} records")
            print(f"Data shape: {data.shape}")
            if 'over_performed' in data.columns:
                print(f"Target distribution: {data['over_performed'].value_counts(normalize=True)}")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("\n💡 Try running with --download to get the NFL data first")


if __name__ == "__main__":
    main()
