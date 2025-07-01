#!/usr/bin/env python3
"""
SparkHost runner for MysteryBox Discord Bot web interface
Configured to run on port 25696 for SparkHost deployment
"""

from web_interface import app
import os

if __name__ == '__main__':
    # Run on SparkHost port 25696
    port = int(os.environ.get('PORT', 25696))
    app.run(host='0.0.0.0', port=port, debug=False)