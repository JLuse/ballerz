# 📊 NFL Data Setup Guide

To use the real NFL data features in this project, you need to download and set up the data separately.

## 🏈 Quick Data Setup

### Option 1: Automated Data Download (Recommended)

```bash
# After cloning and setting up the virtual environment
cd ballerz
source .venv/bin/activate

# Download and set up NFL data automatically
python -m src.data.nfl_data_integration --download
```

### Option 2: Manual Data Setup

1. **Clone the NFL Data Repository:**
   ```bash
   cd ballerz
   git clone https://github.com/hvpkod/NFL-Data.git
   ```

2. **Verify the Data Structure:**
   ```bash
   ls NFL-Data/NFL-data-Players/
   # Should show files like:
   # - 2015_PlayerWeekStats.csv
   # - 2016_PlayerWeekStats.csv
   # - 2017_PlayerWeekStats.csv
   # - 2018_PlayerWeekStats.csv
   # - 2019_PlayerWeekStats.csv
   # - 2020_PlayerWeekStats.csv
   # - 2021_PlayerWeekStats.csv
   ```

3. **Test the Data Integration:**
   ```bash
   python -m src.data.nfl_data_integration
   ```

## 📁 Data Structure

The NFL data repository contains:
- **Player Week Stats**: Individual player performance data by week
- **Seasons**: 2015-2021 (7 seasons of data)
- **Positions**: RB, WR, QB, TE, and more
- **Stats**: Rushing, receiving, passing, fantasy points, projections

## 🔧 Data Processing

When you run `python train_with_real_data.py`, the system will:

1. **Load Data**: Read CSV files from `NFL-Data/NFL-data-Players/`
2. **Merge Data**: Combine weekly stats with projections
3. **Filter Positions**: Focus on Running Backs (RB) by default
4. **Engineer Features**: Create 57 predictive features
5. **Train Model**: Build ML model on real historical data

## 📊 Available Data

### **Seasons Available:**
- 2015-2021 (7 full seasons)
- ~1,000+ player-weeks per season
- ~7,000+ total data points

### **Player Positions:**
- **RB (Running Backs)** - Included
- **WR (Wide Receivers)** - Included
- **QB (Quarterbacks)** - Included
- **TE (Tight Ends)** - Included
- **DB (Defensive Backs)** - Excluded
- **LB (Linebackers)** - Excluded
- **DEF/DST (Team Defense)** - Excluded (needs separate data source)

### **Stats Included:**
- **Rushing**: Yards, TDs, Attempts
- **Receiving**: Yards, TDs, Receptions
- **Fantasy Points**: Actual and projected
- **Game Context**: Opponent, home/away, etc.

## 🎯 Using the Data

### **Train with Real Data:**
```bash
python train_with_real_data.py
```

### **Expected Results:**
- **Dataset Size**: ~30,000+ offensive player-weeks (RB, WR, QB, TE)
- **Target Distribution**: Varies by position (typically 15-20% over-perform)
- **Features**: 57 engineered features
- **Model Performance**: Realistic accuracy across multiple positions
- **Positions**: RB, WR, QB, TE (excludes DB, LB)

### **Compare with Sample Data:**
```bash
# Sample data (synthetic)
python train_baseline.py

# Real NFL data
python train_with_real_data.py
```

## 🔍 Data Exploration

### **Explore the Data:**
```bash
python -m src.data.nfl_data_integration --explore
```

### **Check Data Quality:**
```bash
python -c "
from src.data.nfl_data_integration import NFLDataIntegrator
integrator = NFLDataIntegrator()
data = integrator.load_and_merge_data()
print(f'Total records: {len(data)}')
print(f'Columns: {list(data.columns)}')
print(f'Sample data:\n{data.head()}')
"
```

## 🚨 Troubleshooting

### **Data Not Found:**
```bash
# Check if NFL-Data directory exists
ls -la NFL-Data/

# If missing, clone it
git clone https://github.com/hvpkod/NFL-Data.git
```

### **Permission Issues:**
```bash
# Make sure you have read permissions
chmod -R 644 NFL-Data/
```

### **Memory Issues:**
```bash
# If you get memory errors, try processing fewer seasons
# Edit config/config.yaml to limit seasons
```

## 📈 Data Insights

### **What the Real Data Shows:**
- **16% over-perform rate** (vs ~50% in sample data)
- **Realistic projections** from actual fantasy sites
- **Historical patterns** from 7 seasons of NFL data
- **Feature importance** based on real performance

### **Sample vs Real Data Comparison:**

| Metric | Sample Data | Real NFL Data |
|--------|-------------|---------------|
| Dataset Size | 1,800 records | ~30,000+ records |
| Over-perform Rate | ~50% | 15-20% |
| Data Quality | Synthetic | Historical |
| Feature Realism | Simplified | Complex |
| Model Accuracy | 100% (overfit) | Realistic |
| Positions | RB only | RB, WR, QB, TE |
| Defensive Positions | N/A | Excluded (DB, LB) |

## 🎉 Next Steps

After setting up the data:

1. **Train the model**: `python train_with_real_data.py`
2. **Make predictions**: `python predict.py`
3. **Explore results**: Check `REAL_DATA_ANALYSIS.md`
4. **Experiment**: Try different features or algorithms

## 🛡️ Team Defense Data

**Note**: Team defense (DEF/DST) positions are not included in this dataset. For team defense analysis, you'll need to find a separate data source that provides:
- Team defensive stats
- Points allowed
- Sacks, interceptions, fumbles
- Special teams touchdowns
- Fantasy points for team defense

The current analysis focuses on individual offensive players only.

---

**Need help?** Check the error messages or run `python -m src.data.nfl_data_integration --help` for more options.
