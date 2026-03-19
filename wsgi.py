"""
WSGI entry point for production deployment
本番環境用のWSGIエントリーポイント
"""
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from sshve2_dashboard_web_app import app, load_data

# Load data on startup
print("Loading data...")
success, message = load_data()
if success:
    print(f"✅ {message}")
else:
    print(f"❌ {message}")

# This is the WSGI application object
application = app

if __name__ == "__main__":
    app.run()
