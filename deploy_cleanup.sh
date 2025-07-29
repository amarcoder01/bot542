#!/bin/bash
# Cleanup script for deployment to reduce image size

echo "🧹 Cleaning up for deployment..."

# Remove large unnecessary directories
rm -rf .git
rm -rf .cache
rm -rf .pythonlibs
rm -rf deploy/qlib_data
rm -rf deploy/logs
rm -rf deploy/results
rm -rf deploy/__pycache__
rm -rf __pycache__
rm -rf attached_assets
rm -rf deploy_backup
rm -rf logs/*.log

# Remove unnecessary Python files from deploy folder
rm -f deploy/advanced_qlib_strategies.py
rm -f deploy/enhanced_technical_indicators.py
rm -f deploy/ml_models.py
rm -f deploy/backtesting_engine.py
rm -f deploy/qlib_service.py

# Keep only essential files
echo "✅ Cleanup complete!"
du -sh .