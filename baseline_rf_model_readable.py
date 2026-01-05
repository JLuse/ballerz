# Auto-generated summary of baseline_rf_model.joblib

# Model type: <class 'sklearn.ensemble._forest.RandomForestClassifier'>

# Hyperparameters:
bootstrap = True
ccp_alpha = 0.0
class_weight = None
criterion = 'gini'
max_depth = 10
max_features = 'sqrt'
max_leaf_nodes = None
max_samples = None
min_impurity_decrease = 0.0
min_samples_leaf = 2
min_samples_split = 5
min_weight_fraction_leaf = 0.0
monotonic_cst = None
n_estimators = 100
n_jobs = -1
oob_score = False
random_state = 42
verbose = 0
warm_start = False


# Example tree structure from first estimator:
tree_structure = '''
|--- rushing_yards_trend_3v3 <= -14.42
|   |--- rushing_yards_week_change <= 25.50
|   |   |--- projection_accuracy_rolling_5 <= 0.56
|   |   |   |--- receptions <= 5.50
|   |   |   |   |--- rushing_yards_rolling_5_std <= 13.90
|   |   |   |   |   |--- fantasy_points_consistency <= 0.20
|   |   |   |   |   |   |--- class: 0.0
|   |   |   |   |   |--- fantasy_points_consistency >  0.20
|   |   |   |   |   |   |--- class: 1.0
|   |   |   |   |--- rushing_yards_rolling_5_std >  13.90
|   |   |   |   |   |--- rushing_touchdowns_rolling_3 <= 0.50
|   |   |   |   |   |   |--- projection_error <= 1.14
|   |   |   |   |   |   |   |--- class: 0.0
|   |   |   |   |   |   |--- projection_error >  1.14
|   |   |   |   |   |   |   |--- class: 1.0
|   |   |   |   |   |--- rushing_touchdowns_rolling_3 >  0.50
|   |   |   |   |   |   |--- receptions_rolling_5 <= 2.30
|   |   |   |   |   |   |   |--- rushing_yards <= 41.00
|   |   |   |   |   |   |   |   |--- fantasy_points_rolling_3 <= 12.62
|   |   |   |   |   |   |   |   |   |--- projection_error <= 1.48
|   |   |   |   |   |   |   |   |   |   |--- class: 0.0
|   |   |   |   |   |   |   |   |   |--- projection_error >  1.48
|   |   |   |   |   |   |   |   |   |   |--- class: 1.0
|   |   |   |   |   |   |   |   |--- fantasy_points_rolling_3 >  12.62
|   |   |   |   |   |   |   |   |   |--- class: 0.0
|   |   |   |   |   |   |   |--- rushing_yards >  41.00
|   |   |   |   |   |   |   |   |--- class: 0.0
|   |   |   |   |   |   |--- receptions_rolling_5 >  2.30
|   |   |   |   |   |   |   |--- class: 0.0
|   |   |   |--- receptions >  5.50
|   |   |   |   |--- class: 1.0
|   |   |--- projection_accuracy_rolling_5 >  0.56
|   |   |   |--- receiving_yards_rolling_5_std <= 7.25
|   |   |   |   |--- class: 0.0
|   |   |   |--- receiving_yards_rolling_5_std >  7.25
|   |   |   |   |--- projection_confidence <= 0.27
|   |   |   |   |   |--- rushing_yards_rolling_5_std <= 24.20
|   |   |   |   |   |   |--- receptions_rolling_3 <= 2.83
|   |   |   |   |   |   |   |--- class: 0.0
|   |   |   |   |   |   |--- receptions_rolling_3 >  2.83
|   |   |   |   |   |   |   |--- class: 1.0
|   |   |   |   |   |--- rushing_yards_rolling_5_std >  24.20
|   |   |   |   |   |   |--- rushing_yards_rolling_5_std <= 30.63
|   |   |   |   |   |   |   |--- class: 1.0
|   |   |   |   |   |   |--- rushing_yards_rolling_5_std >  30.63
|   |   |   |   |   |   |   |--- rushing_yards_rolling_3_std <= 26.96
|   |   |   |   |   |   |   |   |--- class: 0.0
|   |   |   |   |   |   |   |--- rushing_yards_rolling_3_std >  26.96
|   |   |   |   |   |   |   |   |--- receiving_yards_rolling_3 <= 18.00
|   |   |   |   |   |   |   |   |   |--- class: 0.0
|   |   |   |   |   |   |   |   |--- receiving_yards_rolling_3 >  18.00
|   |   |   |   |   |   |   |   |   |--- class: 1.0
|   |   |   |   |--- projection_confidence >  0.27
|   |   |   |   |   |--- fantasy_points_rolling_3 <= 10.27
|   |   |   |   |   |   |--- class: 1.0
|   |   |   |   |   |--- fantasy_points_rolling_3 >  10.27
|   |   |   |   |   |   |--- class: 1.0
|   |--- rushing_yards_week_change >  25.50
|   |   |--- projection_error <= 0.02
|   |   |   |--- class: 0.0
|   |   |--- projection_error >  0.02
|   |   |   |--- class: 1.0
|--- rushing_yards_trend_3v3 >  -14.42
|   |--- rushing_yards_rolling_5_std <= 12.82
|   |   |--- projection_vs_recent <= -0.27
|   |   |   |--- rushing_yards_rolling_3_std <= 12.41
|   |   |   |   |--- projection_accuracy_rolling_5 <= -0.40
|   |   |   |   |   |--- rushing_touchdowns_rolling_5_std <= 0.87
|   |   |   |   |   |   |--- class: 0.0
|   |   |   |   |   |--- rushing_touchdowns_rolling_5_std >  0.87
|   |   |   |   |   |   |--- class: 1.0
|   |   |   |   |--- projection_accuracy_rolling_5 >  -0.40
|   |   |   |   |   |--- fantasy_points_rolling_5_std <= 6.31
|   |   |   |   |   |   |--- class: 1.0
|   |   |   |   |   |--- fantasy_points_rolling_5_std >  6.31
|   |   |   |   |   |   |--- class: 1.0
|   |   |   |--- rushing_yards_rolling_3_std >  12.41
|   |   |   |   |--- receiving_touchdowns_rolling_5_std <= 0.22
|   |   |   |   |   |--- class: 0.0
|   |   |   |   |--- receiving_touchdowns_rolling_5_std >  0.22
|   |   |   |   |   |--- class: 1.0
|   |   |--- projection_vs_recent >  -0.27
|   |   |   |--- receptions_week_change <= 2.50
|   |   |   |   |--- receiving_touchdowns_rolling_5_std <= 0.64
|   |   |   |   |   |--- projection_error <= -0.06
|   |   |   |   |   |   |--- class: 0.0
|   |   |   |   |   |--- projection_error >  -0.06
|   |   |   |   |   |   |--- class: 0.0
|   |   |   |   |--- receiving_touchdowns_rolling_5_std >  0.64
|   |   |   |   |   |--- class: 0.0
|   |   |   |--- receptions_week_change >  2.50
|   |   |   |   |--- receiving_touchdowns_rolling_5_std <= 0.22
|   |   |   |   |   |--- class: 1.0
|   |   |   |   |--- receiving_touchdowns_rolling_5_std >  0.22
|   |   |   |   |   |--- class: 0.0
|   |--- rushing_yards_rolling_5_std >  12.82
|   |   |--- projection_confidence <= 0.65
|   |   |   |--- projection_error <= -0.00
|   |   |   |   |--- class: 0.0
|   |   |   |--- projection_error >  -0.00
|   |   |   |   |--- rushing_yards_week_change <= 50.50
|   |   |   |   |   |--- class: 1.0
|   |   |   |   |--- rushing_yards_week_change >  50.50
|   |   |   |   |   |--- receptions_rolling_3 <= 1.50
|   |   |   |   |   |   |--- fantasy_points_rolling_3 <= 16.45
|   |   |   |   |   |   |   |--- class: 1.0
|   |   |   |   |   |   |--- fantasy_points_rolling_3 >  16.45
|   |   |   |   |   |   |   |--- class: 1.0
|   |   |   |   |   |--- receptions_rolling_3 >  1.50
|   |   |   |   |   |   |--- class: 1.0
|   |   |--- projection_confidence >  0.65
|   |   |   |--- projection_error <= -1.70
|   |   |   |   |--- class: 0.0
|   |   |   |--- projection_error >  -1.70
|   |   |   |   |--- class: 1.0

'''
