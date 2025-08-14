# 🚀 Quick Setup After Cloning

When you clone this repository on a new machine, here's how to get everything running:

## Option 1: One-Command Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/JLuse/ballerz.git
cd ballerz

# Run the automated setup (creates virtual environment and installs dependencies)
chmod +x quick_start.sh
./quick_start.sh
```

That's it! The script will:
- ✅ Check Python version
- ✅ Create a virtual environment (`.venv`)
- ✅ Install all dependencies from `requirements.txt`
- ✅ Activate the virtual environment automatically

## Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/JLuse/ballerz.git
cd ballerz

# Run setup script
python setup.py

# Activate virtual environment
source .venv/bin/activate
```

## 🎯 What You Can Do Now

After setup, you can run:

```bash
# Train with sample data (quick test)
python train_baseline.py

# Train with real NFL data (full pipeline)
python train_with_real_data.py

# Make predictions
python predict.py

# Run tests
python -m pytest tests/
```

## 🔧 Virtual Environment Management

- **Activate**: `source .venv/bin/activate`
- **Deactivate**: `deactivate`
- **Reinstall dependencies**: `pip install -r requirements.txt`

## 📝 Notes

- The virtual environment is stored in `.venv/` (excluded from Git)
- All dependencies are listed in `requirements.txt`
- Large data files are not included in the repository
- For real NFL data, you'll need to download it separately or use the sample data

---

**Need help?** Check the `README.md` or `GETTING_STARTED.md` for more detailed information.
