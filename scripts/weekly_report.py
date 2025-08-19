#!/usr/bin/env python3
"""
Weekly Fantasy Football Report Generator
Generates comprehensive weekly predictions for multiple players.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from predict_player import PlayerPredictor


class WeeklyReportGenerator:
    """Generate weekly fantasy football prediction reports."""
    
    def __init__(self, model_path: str = "outputs/models/baseline_rf_model.joblib"):
        """Initialize the report generator."""
        self.predictor = PlayerPredictor(model_path)
        self.report_data = []
    
    def add_player(self, player_name: str, week: int, season: int = 2023) -> Dict:
        """Add a player to the weekly report."""
        print(f"📊 Adding {player_name} to week {week} report...")
        
        result = self.predictor.predict_player(player_name, week, season)
        
        if "error" not in result:
            self.report_data.append(result)
            print(f"✅ Added {player_name}: {result['recommendation']}")
        else:
            print(f"❌ Failed to add {player_name}: {result['error']}")
        
        return result
    
    def add_sample_players(self, week: int, season: int = 2023):
        """Add sample players for demonstration."""
        sample_players = [
            "Christian McCaffrey",
            "Austin Ekeler", 
            "Saquon Barkley",
            "Derrick Henry",
            "Nick Chubb",
            "Josh Jacobs",
            "Joe Mixon",
            "D'Andre Swift",
            "Alvin Kamara",
            "Dalvin Cook"
        ]
        
        print(f"🏈 Adding {len(sample_players)} sample players to week {week} report...")
        
        for player in sample_players:
            self.add_player(player, week, season)
    
    def generate_report(self, week: int, season: int = 2023, output_file: str = None) -> str:
        """Generate a comprehensive weekly report."""
        if not self.report_data:
            print("📝 No players in report. Adding sample players...")
            self.add_sample_players(week, season)
        
        # Sort by over-perform probability
        sorted_data = sorted(self.report_data, key=lambda x: x['over_perform_probability'], reverse=True)
        
        # Generate report
        report = self._format_report(sorted_data, week, season)
        
        # Save to file if specified
        if output_file:
            self._save_report(report, output_file)
        
        return report
    
    def _format_report(self, data: List[Dict], week: int, season: int) -> str:
        """Format the report as a string."""
        report_lines = []
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append(f"🏈 FANTASY FOOTBALL WEEKLY REPORT - WEEK {week}, {season}")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total Players: {len(data)}")
        report_lines.append("")
        
        # Summary
        over_perform_count = sum(1 for player in data if player['prediction'] == 1)
        under_perform_count = len(data) - over_perform_count
        
        report_lines.append("📊 SUMMARY")
        report_lines.append("-" * 40)
        report_lines.append(f"Over-Perform Predictions: {over_perform_count}")
        report_lines.append(f"Under-Perform Predictions: {under_perform_count}")
        report_lines.append(f"Average Confidence: {np.mean([p['over_perform_probability'] for p in data]):.1%}")
        report_lines.append("")
        
        # Strong Starts (High confidence over-perform)
        strong_starts = [p for p in data if p['prediction'] == 1 and p['over_perform_probability'] >= 0.7]
        if strong_starts:
            report_lines.append("🔥 STRONG STARTS")
            report_lines.append("-" * 40)
            for player in strong_starts:
                report_lines.append(
                    f"• {player['player_name']:<20} "
                    f"Projection: {player['projection']:>5.1f} | "
                    f"Over-Perform: {player['over_perform_probability']:>5.1%} | "
                    f"Confidence: {player['confidence']}"
                )
            report_lines.append("")
        
        # Consider Starting (Medium confidence over-perform)
        consider_starts = [p for p in data if p['prediction'] == 1 and 0.5 <= p['over_perform_probability'] < 0.7]
        if consider_starts:
            report_lines.append("🤔 CONSIDER STARTING")
            report_lines.append("-" * 40)
            for player in consider_starts:
                report_lines.append(
                    f"• {player['player_name']:<20} "
                    f"Projection: {player['projection']:>5.1f} | "
                    f"Over-Perform: {player['over_perform_probability']:>5.1%} | "
                    f"Confidence: {player['confidence']}"
                )
            report_lines.append("")
        
        # Avoid (High confidence under-perform)
        avoid_players = [p for p in data if p['prediction'] == 0 and p['over_perform_probability'] >= 0.7]
        if avoid_players:
            report_lines.append("⚠️  AVOID")
            report_lines.append("-" * 40)
            for player in avoid_players:
                report_lines.append(
                    f"• {player['player_name']:<20} "
                    f"Projection: {player['projection']:>5.1f} | "
                    f"Over-Perform: {player['over_perform_probability']:>5.1%} | "
                    f"Confidence: {player['confidence']}"
                )
            report_lines.append("")
        
        # Consider Benching (Medium confidence under-perform)
        consider_bench = [p for p in data if p['prediction'] == 0 and 0.3 <= p['over_perform_probability'] < 0.5]
        if consider_bench:
            report_lines.append("🛋️  CONSIDER BENCHING")
            report_lines.append("-" * 40)
            for player in consider_bench:
                report_lines.append(
                    f"• {player['player_name']:<20} "
                    f"Projection: {player['projection']:>5.1f} | "
                    f"Over-Perform: {player['over_perform_probability']:>5.1%} | "
                    f"Confidence: {player['confidence']}"
                )
            report_lines.append("")
        
        # Full Rankings
        report_lines.append("📋 FULL RANKINGS (by Over-Perform Probability)")
        report_lines.append("-" * 40)
        report_lines.append(f"{'Rank':<4} {'Player':<20} {'Projection':<10} {'Over-Perform':<12} {'Confidence':<10} {'Recommendation'}")
        report_lines.append("-" * 80)
        
        for i, player in enumerate(data, 1):
            report_lines.append(
                f"{i:<4} {player['player_name']:<20} "
                f"{player['projection']:<10.1f} "
                f"{player['over_perform_probability']:<12.1%} "
                f"{player['confidence']:<10} "
                f"{player['recommendation']}"
            )
        
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("💡 TIPS:")
        report_lines.append("• Use this report as one tool in your decision-making process")
        report_lines.append("• Consider injuries, weather, and other factors not captured here")
        report_lines.append("• High confidence predictions (>80%) are more reliable")
        report_lines.append("• Always check the latest news before making final decisions")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def _save_report(self, report: str, output_file: str):
        """Save the report to a file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"📄 Report saved to: {output_path}")
    
    def export_csv(self, output_file: str = None):
        """Export the report data as CSV."""
        if not self.report_data:
            print("❌ No data to export")
            return
        
        df = pd.DataFrame(self.report_data)
        
        # Reorder columns for better readability
        column_order = [
            'player_name', 'week', 'season', 'projection', 'prediction',
            'over_perform_probability', 'confidence', 'recommendation'
        ]
        
        # Only include columns that exist
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        if output_file is None:
            output_file = f"week_{self.report_data[0]['week']}_predictions.csv"
        
        output_path = Path(output_file)
        df.to_csv(output_path, index=False)
        print(f"📊 CSV exported to: {output_path}")
        
        return output_path


def main():
    """Main function for the weekly report generator."""
    parser = argparse.ArgumentParser(description="Fantasy Football Weekly Report Generator")
    parser.add_argument("--week", "-w", type=int, required=True, help="Week number (1-18)")
    parser.add_argument("--season", "-s", type=int, default=2023, help="Season year (default: 2023)")
    parser.add_argument("--players", "-p", nargs="+", help="List of players to analyze")
    parser.add_argument("--output", "-o", help="Output file for the report")
    parser.add_argument("--csv", "-c", help="Export CSV file")
    parser.add_argument("--model", "-m", default="outputs/models/baseline_rf_model.joblib", help="Path to trained model")
    
    args = parser.parse_args()
    
    # Validate inputs
    if args.week < 1 or args.week > 18:
        print("❌ Week must be between 1 and 18")
        sys.exit(1)
    
    # Initialize report generator
    generator = WeeklyReportGenerator(args.model)
    
    # Add players
    if args.players:
        print(f"🏈 Analyzing {len(args.players)} players for Week {args.week}...")
        for player in args.players:
            generator.add_player(player, args.week, args.season)
    else:
        print(f"🏈 Generating sample report for Week {args.week}...")
        generator.add_sample_players(args.week, args.season)
    
    # Generate report
    report = generator.generate_report(args.week, args.season, args.output)
    
    # Print report
    print("\n" + report)
    
    # Export CSV if requested
    if args.csv:
        generator.export_csv(args.csv)


if __name__ == "__main__":
    main()
