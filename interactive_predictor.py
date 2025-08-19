#!/usr/bin/env python3
"""
Interactive Fantasy Football Predictor
A user-friendly tool that guides users through player predictions.
"""

import sys
from pathlib import Path
from typing import List, Dict

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from predict_player import PlayerPredictor


class InteractivePredictor:
    """Interactive tool for fantasy football predictions."""
    
    def __init__(self):
        """Initialize the interactive predictor."""
        self.predictor = PlayerPredictor()
    
    def run(self):
        """Run the interactive prediction tool."""
        print("🏈 Welcome to the Fantasy Football Interactive Predictor!")
        print("=" * 60)
        print("This tool will help you predict player performance.")
        print("Let's get started!\n")
        
        while True:
            try:
                # Get user choice
                choice = self._get_main_menu_choice()
                
                if choice == "1":
                    self._single_player_prediction()
                elif choice == "2":
                    self._weekly_report()
                elif choice == "3":
                    self._player_comparison()
                elif choice == "4":
                    self._show_help()
                elif choice == "5":
                    print("\n👋 Thanks for using the Fantasy Football Predictor!")
                    print("Good luck with your fantasy team! 🏈")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
                
                print("\n" + "-" * 60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Thanks for using the Fantasy Football Predictor!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print("Please try again.")
    
    def _get_main_menu_choice(self) -> str:
        """Display main menu and get user choice."""
        print("📋 MAIN MENU")
        print("1. Single Player Prediction")
        print("2. Weekly Report")
        print("3. Player Comparison")
        print("4. Help")
        print("5. Exit")
        
        return input("\nEnter your choice (1-5): ").strip()
    
    def _single_player_prediction(self):
        """Handle single player prediction."""
        print("\n🎯 SINGLE PLAYER PREDICTION")
        print("-" * 40)
        
        # Get player name
        player_name = input("Enter player name: ").strip()
        if not player_name:
            print("❌ Player name cannot be empty.")
            return
        
        # Get week
        week = self._get_week_input()
        if week is None:
            return
        
        # Get season
        season = self._get_season_input()
        if season is None:
            return
        
        # Make prediction
        print(f"\n🏈 Analyzing {player_name} for Week {week}, {season}...")
        result = self.predictor.predict_player(player_name, week, season)
        
        # Display results
        self.predictor.display_prediction(result)
        
        # Ask if user wants to save
        save_choice = input("\n💾 Save this prediction to file? (y/n): ").strip().lower()
        if save_choice in ['y', 'yes']:
            self._save_prediction(result)
    
    def _weekly_report(self):
        """Handle weekly report generation."""
        print("\n📊 WEEKLY REPORT GENERATOR")
        print("-" * 40)
        
        # Get week
        week = self._get_week_input()
        if week is None:
            return
        
        # Get season
        season = self._get_season_input()
        if season is None:
            return
        
        # Get players
        print("\nEnter player names (one per line, press Enter twice when done):")
        players = []
        while True:
            player = input("Player: ").strip()
            if not player:
                break
            players.append(player)
        
        if not players:
            print("❌ No players entered. Using sample players.")
            players = None
        
        # Generate report
        from weekly_report import WeeklyReportGenerator
        generator = WeeklyReportGenerator()
        
        if players:
            print(f"\n🏈 Generating report for {len(players)} players...")
            for player in players:
                generator.add_player(player, week, season)
        else:
            print(f"\n🏈 Generating sample report...")
            generator.add_sample_players(week, season)
        
        # Generate and display report
        report = generator.generate_report(week, season)
        print("\n" + report)
        
        # Ask if user wants to save
        save_choice = input("\n💾 Save report to file? (y/n): ").strip().lower()
        if save_choice in ['y', 'yes']:
            filename = input("Enter filename (default: weekly_report.txt): ").strip()
            if not filename:
                filename = "weekly_report.txt"
            generator._save_report(report, filename)
    
    def _player_comparison(self):
        """Handle player comparison."""
        print("\n⚖️  PLAYER COMPARISON")
        print("-" * 40)
        
        # Get players to compare
        print("Enter two players to compare:")
        player1 = input("Player 1: ").strip()
        player2 = input("Player 2: ").strip()
        
        if not player1 or not player2:
            print("❌ Both player names are required.")
            return
        
        # Get week and season
        week = self._get_week_input()
        if week is None:
            return
        
        season = self._get_season_input()
        if season is None:
            return
        
        # Get predictions
        print(f"\n🏈 Comparing {player1} vs {player2} for Week {week}...")
        
        result1 = self.predictor.predict_player(player1, week, season)
        result2 = self.predictor.predict_player(player2, week, season)
        
        # Display comparison
        self._display_comparison(result1, result2)
    
    def _display_comparison(self, result1: Dict, result2: Dict):
        """Display player comparison."""
        if "error" in result1 or "error" in result2:
            print("❌ Could not complete comparison due to errors.")
            return
        
        print("\n" + "=" * 80)
        print("⚖️  PLAYER COMPARISON RESULTS")
        print("=" * 80)
        
        print(f"{'Metric':<20} {'Player 1':<30} {'Player 2':<30}")
        print("-" * 80)
        
        print(f"{'Player Name':<20} {result1['player_name']:<30} {result2['player_name']:<30}")
        print(f"{'Projection':<20} {result1['projection']:<30.1f} {result2['projection']:<30.1f}")
        print(f"{'Prediction':<20} {'OVER-PERFORM' if result1['prediction'] == 1 else 'UNDER-PERFORM':<30} {'OVER-PERFORM' if result2['prediction'] == 1 else 'UNDER-PERFORM':<30}")
        print(f"{'Confidence':<20} {result1['confidence']:<30} {result2['confidence']:<30}")
        print(f"{'Over-Perform %':<20} {result1['over_perform_probability']:<30.1%} {result2['over_perform_probability']:<30.1%}")
        print(f"{'Recommendation':<20} {result1['recommendation']:<30} {result2['recommendation']:<30}")
        
        print("\n" + "=" * 80)
        
        # Determine winner
        if result1['over_perform_probability'] > result2['over_perform_probability']:
            winner = result1['player_name']
            margin = result1['over_perform_probability'] - result2['over_perform_probability']
            print(f"🏆 RECOMMENDATION: {winner} (by {margin:.1%})")
        elif result2['over_perform_probability'] > result1['over_perform_probability']:
            winner = result2['player_name']
            margin = result2['over_perform_probability'] - result1['over_perform_probability']
            print(f"🏆 RECOMMENDATION: {winner} (by {margin:.1%})")
        else:
            print("🤝 RECOMMENDATION: Tie - both players have similar probabilities")
        
        print("=" * 80)
    
    def _get_week_input(self) -> int:
        """Get week input from user."""
        while True:
            try:
                week = input("Enter week number (1-18): ").strip()
                week_num = int(week)
                if 1 <= week_num <= 18:
                    return week_num
                else:
                    print("❌ Week must be between 1 and 18.")
            except ValueError:
                print("❌ Please enter a valid number.")
            except KeyboardInterrupt:
                return None
    
    def _get_season_input(self) -> int:
        """Get season input from user."""
        while True:
            try:
                season = input("Enter season year (default: 2023): ").strip()
                if not season:
                    return 2023
                season_num = int(season)
                if 2015 <= season_num <= 2024:
                    return season_num
                else:
                    print("❌ Season must be between 2015 and 2024.")
            except ValueError:
                print("❌ Please enter a valid year.")
            except KeyboardInterrupt:
                return None
    
    def _save_prediction(self, result: Dict):
        """Save prediction to file."""
        if "error" in result:
            print("❌ Cannot save prediction due to error.")
            return
        
        filename = input("Enter filename (default: prediction.txt): ").strip()
        if not filename:
            filename = "prediction.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write("FANTASY FOOTBALL PREDICTION\n")
                f.write("=" * 40 + "\n")
                f.write(f"Player: {result['player_name']}\n")
                f.write(f"Week: {result['week']} ({result['season']})\n")
                f.write(f"Projection: {result['projection']:.1f} fantasy points\n")
                f.write(f"Prediction: {'OVER-PERFORM' if result['prediction'] == 1 else 'UNDER-PERFORM'}\n")
                f.write(f"Confidence: {result['confidence']} ({result['over_perform_probability']:.1%})\n")
                f.write(f"Recommendation: {result['recommendation']}\n")
            
            print(f"✅ Prediction saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
    
    def _show_help(self):
        """Show help information."""
        print("\n📖 HELP & TIPS")
        print("-" * 40)
        print("🏈 Single Player Prediction:")
        print("  • Enter a player's full name (e.g., 'Christian McCaffrey')")
        print("  • Choose the week and season for analysis")
        print("  • Get detailed prediction with confidence level")
        print()
        print("📊 Weekly Report:")
        print("  • Analyze multiple players at once")
        print("  • Get ranked list by over-perform probability")
        print("  • Save results to file for later reference")
        print()
        print("⚖️  Player Comparison:")
        print("  • Compare two players side-by-side")
        print("  • See which player is more likely to over-perform")
        print("  • Get clear recommendation")
        print()
        print("💡 Tips for Best Results:")
        print("  • Use full player names for better matching")
        print("  • High confidence predictions (>80%) are more reliable")
        print("  • Consider this as one tool in your decision process")
        print("  • Always check for injuries and latest news")
        print()
        print("🔧 Technical Notes:")
        print("  • Model trained on historical fantasy data")
        print("  • Features include rolling averages, trends, and projections")
        print("  • Predictions based on over/under performance vs projections")


def main():
    """Main function for the interactive predictor."""
    predictor = InteractivePredictor()
    predictor.run()


if __name__ == "__main__":
    main()
