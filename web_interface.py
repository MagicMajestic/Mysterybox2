#!/usr/bin/env python3
"""
Web interface for MysteryBox Discord Bot
Provides web dashboard to monitor giveaways and bot statistics
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for
from utils.database import (
    load_giveaways, 
    load_prizes, 
    load_gifs, 
    load_prize_lists,
    save_giveaways,
    save_prizes
)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "mysterybox-secret-key-for-development")

@app.template_filter('timestamp_to_date')
def timestamp_to_date(timestamp):
    """Convert timestamp to readable date format"""
    try:
        dt = datetime.fromtimestamp(float(timestamp))
        return dt.strftime('%d.%m.%Y %H:%M:%S')
    except (ValueError, TypeError):
        return 'Неверный формат времени'

def get_bot_status():
    """Check if the bot is running by checking log file"""
    try:
        with open('logs/bot.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-10:]  # Last 10 lines
            
            for line in reversed(recent_lines):
                if 'Bot is ready!' in line:
                    return True, 'Бот онлайн и готов к работе'
                elif 'Connection closed' in line or 'Failed to start' in line:
                    return False, 'Бот отключен или ошибка подключения'
        
        return False, 'Статус неизвестен'
    except Exception as e:
        return False, f'Не удалось проверить статус: {str(e)}'

@app.route('/')
def dashboard():
    """Main dashboard page"""
    giveaways = load_giveaways()
    prizes = load_prizes()
    gifs = load_gifs()
    prize_lists = load_prize_lists()
    
    # Calculate statistics
    active_giveaways = [g for g in giveaways.values() if not g.get('ended', False)]
    completed_giveaways = [g for g in giveaways.values() if g.get('ended', False)]
    
    bot_online, bot_status = get_bot_status()
    
    stats = {
        'total_giveaways': len(giveaways),
        'active_giveaways': len(active_giveaways),
        'completed_giveaways': len(completed_giveaways),
        'total_prizes': len(prizes),
        'total_gifs': len(gifs),
        'prize_lists': len(prize_lists),
        'bot_online': bot_online,
        'bot_status': bot_status
    }
    
    return render_template('dashboard.html', 
                         stats=stats,
                         active_giveaways=active_giveaways,
                         completed_giveaways=completed_giveaways[:10])  # Show last 10

@app.route('/api/giveaways')
def api_giveaways():
    """API endpoint for giveaways data"""
    giveaways = load_giveaways()
    return jsonify(giveaways)

@app.route('/api/prizes')
def api_prizes():
    """API endpoint for prizes data"""
    prizes = load_prizes()
    return jsonify(prizes)

@app.route('/api/stats')
def api_stats():
    """API endpoint for bot statistics"""
    giveaways = load_giveaways()
    prizes = load_prizes()
    gifs = load_gifs()
    
    active_giveaways = [g for g in giveaways.values() if not g.get('ended', False)]
    completed_giveaways = [g for g in giveaways.values() if g.get('ended', False)]
    
    bot_online, bot_status = get_bot_status()
    
    return jsonify({
        'total_giveaways': len(giveaways),
        'active_giveaways': len(active_giveaways),
        'completed_giveaways': len(completed_giveaways),
        'total_prizes': len(prizes),
        'total_gifs': len(gifs),
        'bot_online': bot_online,
        'bot_status': bot_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/giveaway/<giveaway_id>')
def giveaway_detail(giveaway_id):
    """Show detailed information about a specific giveaway"""
    giveaways = load_giveaways()
    giveaway = giveaways.get(giveaway_id)
    
    if not giveaway:
        return "Розыгрыш не найден", 404
    
    return render_template('giveaway_detail.html', 
                         giveaway=giveaway,
                         giveaway_id=giveaway_id)

@app.route('/prizes')
def prizes_page():
    """Page showing all prizes"""
    prizes = load_prizes()
    return render_template('prizes.html', prizes=prizes)

@app.route('/logs')
def logs_page():
    """Page showing bot logs"""
    try:
        with open('logs/bot.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_logs = lines[-100:]  # Last 100 lines
        
        return render_template('logs.html', logs=recent_logs)
    except Exception as e:
        return f"Не удалось загрузить логи: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)