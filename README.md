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

### 🏈 Quick Start

```bash
git clone https://github.com/JLuse/ballerz.git
cd ballerz
chmod +x quick_start.sh
./quick_start.sh
```

### 🔧 Manual Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/JLuse/ballerz.git
   cd ballerz
   ```

2. **Set up virtual environment:**
   ```bash
   python setup.py
   ```

3. **Activate virtual environment:**
   ```bash
   # Unix/Linux/macOS
   source .venv/bin/activate

4. **Set up NFL data (optional):**
   ```bash
   # Download and set up real NFL data
   python -m src.data.nfl_data_integration --download
   ```

5. **Run the tool:**
   ```bash
   # Train with sample data
   python train_baseline.py
   
   # Train with real NFL data
   python train_with_real_data.py
   
   # Make predictions
   python predict.py
   ```

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
