#!/usr/bin/env python3
"""
Web interface runner for Replit Preview
This file is specifically for running the Flask web interface on Replit
"""

from web_interface import app

if __name__ == '__main__':
    # Run the Flask app on port 5000 for Replit Preview
    app.run(host='0.0.0.0', port=5000, debug=False)