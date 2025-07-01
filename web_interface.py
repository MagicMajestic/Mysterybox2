#!/usr/bin/env python3
"""
Web interface for MysteryBox Discord Bot
Provides web dashboard to monitor giveaways and bot statistics
"""

import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for, abort
from utils.database import (
    load_giveaways, 
    load_prizes, 
    load_gifs, 
    load_prize_lists,
    save_giveaways,
    save_prizes
)
from collections import defaultdict, Counter

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

def calculate_statistics():
    """Calculate comprehensive statistics for the dashboard"""
    try:
        giveaways = load_giveaways()
        prizes = load_prizes()
        
        total_giveaways = len(giveaways)
        active_giveaways = len([g for g in giveaways.values() if not g.get('ended', False)])
        completed_giveaways = total_giveaways - active_giveaways
        
        # Calculate total participants
        all_participants = []
        for giveaway in giveaways.values():
            all_participants.extend(giveaway.get('participants', []))
        
        total_participants = len(all_participants)
        unique_participants = len(set(all_participants))
        
        # Activity data for last 7 days
        now = datetime.now()
        activity_data = []
        activity_labels = []
        
        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp()
            
            day_giveaways = 0
            for giveaway in giveaways.values():
                giveaway_time = giveaway.get('end_time', 0)
                if day_start <= giveaway_time <= day_end:
                    day_giveaways += 1
            
            activity_data.append(day_giveaways)
            activity_labels.append(day.strftime('%d.%m'))
        
        return {
            'total_giveaways': total_giveaways,
            'active_giveaways': active_giveaways,
            'completed_giveaways': completed_giveaways,
            'total_participants': total_participants,
            'unique_participants': unique_participants,
            'total_prizes': len(prizes),
            'activity_data': activity_data,
            'activity_labels': activity_labels
        }
    except Exception as e:
        print(f"Error calculating statistics: {e}")
        return {
            'total_giveaways': 0,
            'active_giveaways': 0,
            'completed_giveaways': 0,
            'total_participants': 0,
            'unique_participants': 0,
            'total_prizes': 0,
            'activity_data': [0] * 7,
            'activity_labels': [''] * 7
        }

@app.route('/')
def dashboard():
    """Main dashboard page"""
    giveaways = load_giveaways()
    bot_online, bot_status = get_bot_status()
    stats = calculate_statistics()
    
    # Convert giveaways dict to list of tuples for easier template iteration
    giveaways_list = [(gid, giveaway) for gid, giveaway in giveaways.items()]
    
    # Sort by end_time, most recent first
    giveaways_list.sort(key=lambda x: x[1].get('end_time', 0), reverse=True)
    
    return render_template('dashboard.html', 
                         stats=stats,
                         giveaways=giveaways_list,
                         bot_status=bot_online,
                         current_time=datetime.now().strftime('%d.%m.%Y %H:%M:%S'))

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
        abort(404)
    
    return render_template('giveaway_detail.html', 
                         giveaway=giveaway,
                         giveaway_id=giveaway_id)

@app.route('/giveaways')
def giveaways_list():
    """Page showing all giveaways"""
    giveaways = load_giveaways()
    
    # Convert to list and sort by end_time
    giveaways_list = [(gid, giveaway) for gid, giveaway in giveaways.items()]
    giveaways_list.sort(key=lambda x: x[1].get('end_time', 0), reverse=True)
    
    return render_template('giveaways_list.html', giveaways=giveaways_list)

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