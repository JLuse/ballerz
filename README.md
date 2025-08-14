# Fantasy Football Analytics Tool

A machine learning tool that predicts whether NFL players will over- or underperform their weekly fantasy projections.

## Project Goals

1. **MVP**: Build a baseline model that predicts over/under performance vs projections
2. **Data Pipeline**: Ingest and clean historical fantasy football data
3. **Model Evaluation**: Compare predictions against actual outcomes
4. **Future**: Add AI assistant for prediction explanations and start/sit decisions

## Project Structure

```
ballerz/
├── data/                   # Raw and processed data
│   ├── raw/               # Original data files
│   └── processed/         # Cleaned and feature-engineered data
├── src/                   # Source code
│   ├── data/             # Data processing modules
│   ├── models/           # ML model code
│   ├── features/         # Feature engineering
│   └── utils/            # Utility functions
├── notebooks/            # Jupyter notebooks for exploration
├── tests/               # Unit tests
├── requirements.txt     # Python dependencies
└── config/             # Configuration files
```

## Getting Started

### Option 1: Sample Data (Quick Start)
1. Install dependencies: `pip install -r requirements.txt`
2. Train with sample data: `python train_baseline.py`
3. Make predictions: `python predict.py`

### Option 2: Real NFL Data (Recommended)
1. Install dependencies: `pip install -r requirements.txt`
2. Train with real NFL data: `python train_with_real_data.py`
3. Explore the data: `python -m src.data.nfl_data_integration`

## Development Approach

- Start simple with one position (RB)
- Use 2-3 seasons of historical data
- Focus on binary classification (over/under perform)
- Build incrementally with testable components
- Learn and iterate based on results

## Next Steps

1. ✅ Set up data collection pipeline
2. ✅ Create baseline model for RBs
3. ✅ Add feature engineering
4. ✅ Integrate real NFL data
5. 🔄 Expand to other positions (WR, QB, TE)
6. 🔄 Add opponent defensive stats
7. 🔄 Include weather and injury data
8. 🔄 Build AI assistant for explanations
