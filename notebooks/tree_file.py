import joblib
from sklearn.tree import export_text
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

# Load the model
model = joblib.load("/Users/jordanluse/Desktop/projects/ballerz/outputs/models/baseline_rf_model.joblib")

with open("baseline_rf_model_readable.py", "w") as f:
    f.write("# Auto-generated summary of baseline_rf_model.joblib\n\n")
    f.write(f"# Model type: {type(model)}\n\n")
    try:
        f.write("# Hyperparameters:\n")
        for k, v in model.get_params().items():
            f.write(f"{k} = {repr(v)}\n")
    except Exception:
        f.write("# Could not extract hyperparameters\n")

    # If it's a RandomForest, dump one tree as python-like text
    if isinstance(model, (RandomForestClassifier, RandomForestRegressor)):
        if hasattr(model, "estimators_") and model.estimators_:
            tree_text = export_text(model.estimators_[0],
                                    feature_names=getattr(model, "feature_names_in_", None))
            f.write("\n\n# Example tree structure from first estimator:\n")
            f.write("tree_structure = '''\n")
            f.write(tree_text)
            f.write("\n'''\n")

print("✅ Saved a readable Python file → baseline_rf_model_readable.py")