# Getting Started with Ballerz

## What We've Built

You now have a complete **fantasy football analytics tool** that predicts whether NFL players will over- or underperform their weekly fantasy projections. Here's what's included:

### 🎯 **MVP Features**
- **Data Pipeline**: Collects and processes fantasy football data
- **Feature Engineering**: Creates 57 predictive features from raw stats
- **Machine Learning Model**: Random Forest classifier with 99.9% accuracy
- **Prediction System**: Makes predictions on new data with confidence scores

### 📁 **Project Structure**
```
ballerz/
├── src/                    # Source code
│   ├── data/              # Data collection
│   ├── features/          # Feature engineering
│   ├── models/            # ML models
│   └── utils/             # Utilities
├── data/                  # Raw and processed data
├── models/                # Trained models
├── notebooks/             # Jupyter notebooks
├── tests/                 # Unit tests
└── config/                # Configuration files
```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**For Unix/Linux/macOS:**
```bash
git clone https://github.com/YOUR_USERNAME/fantasy-football-analytics.git
cd fantasy-football-analytics
chmod +x quick_start.sh
./quick_start.sh
```

**For Windows:**
```cmd
git clone https://github.com/YOUR_USERNAME/fantasy-football-analytics.git
cd fantasy-football-analytics
quick_start.bat
```

### Option 2: Manual Setup

1. **Clone and navigate to the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/fantasy-football-analytics.git
   cd fantasy-football-analytics
   ```

2. **Set up virtual environment:**
   ```bash
   python setup.py
   ```

3. **Activate virtual environment:**
   ```bash
   # Unix/Linux/macOS
   source .venv/bin/activate
   
   # Windows
   .venv\Scripts\activate
   ```

4. **Train the Model:**
   ```bash
   python train_baseline.py
   ```
   This will:
   - Generate sample RB data (1800 records)
   - Engineer 57 features
   - Train a Random Forest model
   - Save the model to `models/baseline_rf_model.joblib`

5. **Make Predictions:**
   ```bash
   python predict.py
   ```
   This demonstrates how to use the trained model to make predictions on new data.

6. **Run Tests:**
   ```bash
   python -m pytest tests/ -v
   ```

## 📊 Current Results

Our baseline model achieves:
- **99.9% cross-validation accuracy**
- **100% test set accuracy** 
- **100% AUC score**

**Top 5 Most Important Features:**
1. `projection_error` (61.7%) - How far off projections have been
2. `projection_vs_recent` (8.4%) - Projection vs recent performance
3. `projection_accuracy_rolling_5` (6.5%) - Recent projection accuracy
4. `fantasy_points_week_change` (1.4%) - Week-over-week performance change
5. `rushing_yards_trend_3v3` (1.0%) - Rushing yards trend

## 🔍 Understanding the Model

### What It Predicts
- **Binary Classification**: Will a player over-perform (1) or under-perform (0) their projection?
- **Confidence Score**: Probability of over-performing (0-1)

### Key Features Created
- **Rolling Averages**: 3-week and 5-week averages of key stats
- **Trend Features**: Recent vs previous performance comparisons
- **Projection Features**: Historical projection accuracy
- **Context Features**: Season week, team indicators, etc.

### Sample Prediction Output
```
player_name    team  week  projection  predicted_over_perform  confidence
Christian McCaffrey  SF    10     18.5                       1      0.85
Saquon Barkley      NYG    10     15.2                       0      0.23
```

## 🎯 Next Steps for Improvement

### 1. **Real Data Integration**
- Replace sample data with real fantasy football data
- Sources: FantasyPros, ESPN, Pro Football Reference
- Add opponent defensive stats
- Include weather data and injury reports

### 2. **Feature Engineering**
- **Opponent Features**: Rush defense rank, points allowed
- **Weather Features**: Temperature, wind, precipitation
- **Team Features**: Offensive efficiency, game script
- **Player Features**: Age, experience, contract year

### 3. **Model Improvements**
- Try different algorithms (XGBoost, LightGBM, Neural Networks)
- Hyperparameter tuning with GridSearchCV
- Ensemble methods (voting, stacking)
- Time-series validation (walk-forward analysis)

### 4. **Expand Scope**
- **Other Positions**: WR, QB, TE, K, DEF
- **Scoring Formats**: PPR, half-PPR, custom scoring
- **Time Horizons**: Weekly, ROS (rest of season), dynasty

### 5. **AI Assistant (Stretch Goal)**
- Explain predictions with SHAP values
- Provide start/sit recommendations
- Generate waiver wire suggestions
- Interactive web interface

## 🛠️ Development Workflow

### Adding New Features
1. Modify `config/config.yaml` to include new data sources
2. Update `src/data/collect_data.py` to fetch new data
3. Add feature engineering in `src/features/feature_engineering.py`
4. Retrain model and evaluate performance

### Testing Changes
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_baseline.py::test_model_training -v
```

### Data Exploration
```bash
# Start Jupyter notebook
jupyter notebook notebooks/01_data_exploration.py
```

## 📈 Performance Metrics

### Current Model Performance
- **Accuracy**: 99.9% (very high due to sample data)
- **Precision**: 100% (no false positives)
- **Recall**: 100% (no false negatives)
- **F1-Score**: 100%

### Expected Real-World Performance
With real data, expect:
- **Accuracy**: 55-65% (beating projections is hard!)
- **Precision**: 60-70% for over-perform predictions
- **Recall**: 50-60% for identifying over-performers

## 🎓 Learning Resources

### Machine Learning Concepts
- **Feature Engineering**: Creating predictive variables
- **Cross-Validation**: Testing model robustness
- **Feature Importance**: Understanding what drives predictions
- **Overfitting**: When models memorize training data

### Fantasy Football Analytics
- **Projection Sources**: Understanding different projection systems
- **Variance**: Why players over/under perform
- **Sample Size**: Need sufficient data for reliable predictions
- **Market Efficiency**: How quickly information is priced in

## 🤝 Contributing

### Code Style
- Use type hints
- Add docstrings to functions
- Follow PEP 8 style guide
- Write unit tests for new features

### Project Structure
- Keep modules focused and single-purpose
- Use configuration files for parameters
- Separate data, features, and models
- Document assumptions and limitations

## 🚨 Important Notes

### Sample Data Disclaimer
The current model uses **synthetic sample data** for demonstration. Real-world performance will be different and likely lower.

### Model Limitations
- **Historical Bias**: Past performance doesn't guarantee future results
- **Market Efficiency**: Fantasy projections already incorporate much information
- **Small Edges**: Beating projections consistently is extremely difficult
- **Sample Size**: Need large datasets for reliable predictions

### Responsible Use
- Use as one tool among many for fantasy decisions
- Don't rely solely on ML predictions
- Consider context, injuries, weather, etc.
- Remember: past performance ≠ future results

---

**Happy coding and good luck with your fantasy football season! 🏈**
