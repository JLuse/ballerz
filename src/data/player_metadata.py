"""
Player Metadata Integration Module
Integrates player age and experience data with NFL performance data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings

from ..utils.config import load_config, get_data_paths


class PlayerMetadataIntegrator:
    """
    Integrates player age and experience data with NFL performance data.
    """
    
    def __init__(self, metadata_path: str = "NFL-Data/NFL-data-Players/other-player-stats/NFL Player Stats(2016 - 2022).csv"):
        """
        Initialize the player metadata integrator.
        
        Args:
            metadata_path: Path to the player metadata CSV file
        """
        self.metadata_path = Path(metadata_path)
        self.config = load_config()
        self.paths = get_data_paths(self.config)
        
        if not self.metadata_path.exists():
            raise FileNotFoundError(f"Player metadata file not found: {metadata_path}")
        
        # Load and preprocess metadata
        self.metadata_df = self._load_metadata()
    
    def _load_metadata(self) -> pd.DataFrame:
        """
        Load and preprocess the player metadata.
        
        Returns:
            DataFrame with cleaned player metadata
        """
        print("📊 Loading player metadata...")
        
        # Load the CSV file
        df = pd.read_csv(self.metadata_path)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Filter for offensive positions only (RB, WR, QB, TE)
        offensive_positions = ['RB', 'WR', 'QB', 'TE']
        df = df[df['Pos'].isin(offensive_positions)].copy()
        
        # Clean player names (remove extra spaces and special characters)
        df['Player'] = df['Player'].str.strip()
        
        # Convert age to numeric, handling any missing values
        df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
        
        # Convert games played and started to numeric
        df['G'] = pd.to_numeric(df['G'], errors='coerce')
        df['GS'] = pd.to_numeric(df['GS'], errors='coerce')
        
        # Create experience features
        df['games_played'] = df['G'].fillna(0)
        df['games_started'] = df['GS'].fillna(0)
        
        # Standardize team names to match our NFL data
        df['team_clean'] = self._standardize_team_names(df['Tm'])
        
        print(f"✅ Loaded {len(df)} player records with age data")
        print(f"Positions: {df['Pos'].unique()}")
        print(f"Seasons: {sorted(df['Season'].unique())}")
        
        return df
    
    def _standardize_team_names(self, team_series: pd.Series) -> pd.Series:
        """
        Standardize team names to match our NFL data format.
        
        Args:
            team_series: Series of team names
            
        Returns:
            Series with standardized team names
        """
        # Team name mapping from the metadata format to our NFL data format
        team_mapping = {
            'ATL': 'ATL', 'BAL': 'BAL', 'BUF': 'BUF', 'CAR': 'CAR', 'CHI': 'CHI',
            'CIN': 'CIN', 'CLE': 'CLE', 'DAL': 'DAL', 'DEN': 'DEN', 'DET': 'DET',
            'GB': 'GB', 'HOU': 'HOU', 'IND': 'IND', 'JAX': 'JAX', 'KC': 'KC',
            'LAC': 'LAC', 'LAR': 'LAR', 'LV': 'LV', 'MIA': 'MIA', 'MIN': 'MIN',
            'NE': 'NE', 'NO': 'NO', 'NYG': 'NYG', 'NYJ': 'NYJ', 'OAK': 'LV',  # OAK -> LV
            'PHI': 'PHI', 'PIT': 'PIT', 'SEA': 'SEA', 'SF': 'SF', 'TB': 'TB',
            'TEN': 'TEN', 'WAS': 'WAS'
        }
        
        return team_series.map(team_mapping).fillna(team_series)
    
    def _fuzzy_match_player_names(self, player_name: str, candidate_names: List[str]) -> Optional[str]:
        """
        Fuzzy match player names to handle slight differences in naming.
        
        Args:
            player_name: Name to match
            candidate_names: List of candidate names
            
        Returns:
            Best matching name or None
        """
        player_name_clean = player_name.lower().strip()
        
        # Direct match
        for candidate in candidate_names:
            if candidate.lower().strip() == player_name_clean:
                return candidate
        
        # Handle common variations
        variations = [
            player_name_clean,
            player_name_clean.replace("'", ""),
            player_name_clean.replace(".", ""),
            player_name_clean.replace("jr", "").replace("sr", "").strip(),
            player_name_clean.replace("iii", "").replace("ii", "").strip()
        ]
        
        for variation in variations:
            for candidate in candidate_names:
                if candidate.lower().strip() == variation:
                    return candidate
        
        return None
    
    def add_player_metadata(self, nfl_data: pd.DataFrame) -> pd.DataFrame:
        """
        Add player age and experience data to NFL performance data.
        
        Args:
            nfl_data: DataFrame with NFL performance data
            
        Returns:
            DataFrame with added age and experience columns
        """
        print("🔗 Adding player age and experience data...")
        
        # Create a copy to avoid modifying original
        result_df = nfl_data.copy()
        
        # Initialize new columns
        result_df['player_age'] = np.nan
        result_df['games_played'] = np.nan
        result_df['games_started'] = np.nan
        
        # Get unique players from NFL data
        nfl_players = result_df['player_name'].unique()
        metadata_players = self.metadata_df['Player'].unique()
        
        print(f"📊 Matching {len(nfl_players)} NFL players with {len(metadata_players)} metadata players...")
        
        # Track matches for reporting
        matches = 0
        no_matches = []
        
        for nfl_player in nfl_players:
            # Try to find matching player in metadata
            matched_player = self._fuzzy_match_player_names(nfl_player, metadata_players)
            
            if matched_player:
                # Get metadata for this player (all seasons)
                player_metadata = self.metadata_df[
                    (self.metadata_df['Player'] == matched_player)
                ]
                
                if not player_metadata.empty:
                    # For each season, get the age and experience data
                    for season in result_df['season'].unique():
                        season_metadata = player_metadata[player_metadata['Season'] == season]
                        
                        if not season_metadata.empty:
                            # Use the first record for that season (should be the same)
                            age = season_metadata.iloc[0]['Age']
                            games_played = season_metadata.iloc[0]['games_played']
                            games_started = season_metadata.iloc[0]['games_started']
                            
                            # Update all rows for this player and season
                            mask = (result_df['player_name'] == nfl_player) & (result_df['season'] == season)
                            result_df.loc[mask, 'player_age'] = age
                            result_df.loc[mask, 'games_played'] = games_played
                            result_df.loc[mask, 'games_started'] = games_started
                        else:
                            # If no data for this season, try to estimate age from previous seasons
                            # Find the most recent season with data for this player
                            available_seasons = player_metadata['Season'].unique()
                            if len(available_seasons) > 0:
                                latest_season = max(available_seasons)
                                if latest_season < season:
                                    # Estimate age by adding years difference
                                    latest_metadata = player_metadata[player_metadata['Season'] == latest_season].iloc[0]
                                    age_diff = season - latest_season
                                    estimated_age = latest_metadata['Age'] + age_diff
                                    estimated_games = latest_metadata['games_played'] + (age_diff * 16)  # Rough estimate
                                    estimated_starts = latest_metadata['games_started'] + (age_diff * 16)  # Rough estimate
                                    
                                    # Update all rows for this player and season
                                    mask = (result_df['player_name'] == nfl_player) & (result_df['season'] == season)
                                    result_df.loc[mask, 'player_age'] = estimated_age
                                    result_df.loc[mask, 'games_played'] = estimated_games
                                    result_df.loc[mask, 'games_started'] = estimated_starts
                    
                    matches += 1
                else:
                    no_matches.append(nfl_player)
            else:
                no_matches.append(nfl_player)
        
        # Report results
        print(f"✅ Successfully matched {matches} players with age data")
        if no_matches:
            print(f"⚠️  Could not find age data for {len(no_matches)} players")
            if len(no_matches) <= 10:
                print(f"   Missing: {', '.join(no_matches)}")
        
        # Calculate match percentage
        match_percentage = (matches / len(nfl_players)) * 100
        print(f"📈 Age data coverage: {match_percentage:.1f}% of players")
        
        return result_df
    
    def get_player_age_summary(self, nfl_data: pd.DataFrame) -> Dict:
        """
        Get summary statistics about player ages in the dataset.
        
        Args:
            nfl_data: DataFrame with NFL performance data (after adding metadata)
            
        Returns:
            Dictionary with age statistics
        """
        if 'player_age' not in nfl_data.columns:
            raise ValueError("Player age data not found. Run add_player_metadata() first.")
        
        age_data = nfl_data['player_age'].dropna()
        
        if age_data.empty:
            return {"error": "No age data available"}
        
        summary = {
            "total_players_with_age": len(age_data.unique()),
            "age_mean": age_data.mean(),
            "age_median": age_data.median(),
            "age_min": age_data.min(),
            "age_max": age_data.max(),
            "age_std": age_data.std(),
            "age_distribution": age_data.value_counts().sort_index().to_dict()
        }
        
        return summary
    
    def create_age_features(self, nfl_data: pd.DataFrame) -> pd.DataFrame:
        """
        Create additional age-related features for machine learning.
        
        Args:
            nfl_data: DataFrame with NFL performance data (after adding metadata)
            
        Returns:
            DataFrame with additional age features
        """
        if 'player_age' not in nfl_data.columns:
            raise ValueError("Player age data not found. Run add_player_metadata() first.")
        
        result_df = nfl_data.copy()
        
        # Age categories
        result_df['age_category'] = pd.cut(
            result_df['player_age'], 
            bins=[0, 23, 26, 29, 32, 100], 
            labels=['Rookie', 'Young', 'Prime', 'Veteran', 'Senior'],
            include_lowest=True
        )
        
        # Experience categories
        result_df['experience_category'] = pd.cut(
            result_df['games_played'],
            bins=[0, 16, 48, 96, 200, 1000],
            labels=['Rookie', 'Early', 'Mid', 'Experienced', 'Veteran'],
            include_lowest=True
        )
        
        # Age-related features
        result_df['is_rookie'] = (result_df['player_age'] <= 23).astype(int)
        result_df['is_veteran'] = (result_df['player_age'] >= 30).astype(int)
        result_df['is_prime_age'] = ((result_df['player_age'] >= 25) & (result_df['player_age'] <= 28)).astype(int)
        
        # Experience features
        result_df['is_experienced'] = (result_df['games_played'] >= 48).astype(int)
        result_df['games_per_season'] = result_df['games_played'] / (result_df['season'] - 2015 + 1)  # Approximate
        
        print(f"✅ Created {len([col for col in result_df.columns if 'age' in col or 'experience' in col or 'rookie' in col or 'veteran' in col])} age-related features")
        
        return result_df


def main():
    """Test the player metadata integration."""
    try:
        # Initialize integrator
        integrator = PlayerMetadataIntegrator()
        
        # Test with sample data
        print("\n🧪 Testing player metadata integration...")
        
        # Create sample NFL data
        sample_nfl_data = pd.DataFrame({
            'player_name': ['Christian McCaffrey', 'Derrick Henry', 'Austin Ekeler', 'Unknown Player'],
            'season': [2022, 2022, 2022, 2022],
            'week': [1, 1, 1, 1],
            'team': ['SF', 'TEN', 'LAC', 'UNK'],
            'fantasy_points': [20.0, 18.0, 15.0, 10.0]
        })
        
        # Add metadata
        result = integrator.add_player_metadata(sample_nfl_data)
        
        print("\n📊 Results:")
        print(result[['player_name', 'season', 'player_age', 'games_played', 'games_started']])
        
        # Get summary
        summary = integrator.get_player_age_summary(result)
        print(f"\n📈 Age Summary: {summary}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
