"""
Gunicorn configuration for AWS Amplify deployment
AWS Amplify用のGunicorn設定
"""
import os

# Server socket - Amplify uses PORT environment variable
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Worker processes - optimized for Amplify
workers = 2
worker_class = "sync"
timeout = 300  # Longer timeout for data loading
keepalive = 5

# Logging - simplified for Amplify
loglevel = "info"
accesslog = "-"  # stdout
errorlog = "-"   # stderr

# Process naming
proc_name = "sshve2_dashboard"
