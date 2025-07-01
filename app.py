#!/usr/bin/env python3
"""
Flask app entry point for MysteryBox Discord Bot web interface
This allows running both the Discord bot and web interface simultaneously
"""

from web_interface import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)