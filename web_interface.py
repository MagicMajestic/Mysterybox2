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
from utils.giveaway_logger import (
    get_recent_events,
    format_event_message,
    get_event_icon
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

def calculate_activity_stats(period='day'):
    """Calculate activity statistics with flexible period filtering"""
    try:
        giveaways = load_giveaways()
        now = datetime.now()
        
        # Define periods
        if period == 'day':
            days_back = 7
            date_format = '%d.%m'
            period_name = 'дням'
        elif period == 'week':
            days_back = 7 * 4  # 4 weeks
            date_format = '%d.%m'
            period_name = 'неделям'
        elif period == 'month':
            days_back = 30 * 12  # 12 months
            date_format = '%m.%y'
            period_name = 'месяцам'
        elif period == 'year':
            days_back = 365 * 5  # 5 years
            date_format = '%Y'
            period_name = 'годам'
        else:
            days_back = 7
            date_format = '%d.%m'
            period_name = 'дням'
        
        activity_data = []
        activity_labels = []
        
        if period == 'day':
            # Last 7 days
            for i in range(6, -1, -1):
                day = now - timedelta(days=i)
                day_start = day.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
                day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp()
                
                day_participants = 0
                for giveaway in giveaways.values():
                    giveaway_time = giveaway.get('end_time', 0)
                    if day_start <= giveaway_time <= day_end:
                        day_participants += len(giveaway.get('participants', []))
                
                activity_data.append(day_participants)
                activity_labels.append(day.strftime(date_format))
                
        elif period == 'week':
            # Last 4 weeks
            for i in range(3, -1, -1):
                week_start = now - timedelta(weeks=i+1)
                week_end = now - timedelta(weeks=i)
                week_start_ts = week_start.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
                week_end_ts = week_end.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp()
                
                week_participants = 0
                for giveaway in giveaways.values():
                    giveaway_time = giveaway.get('end_time', 0)
                    if week_start_ts <= giveaway_time <= week_end_ts:
                        week_participants += len(giveaway.get('participants', []))
                
                activity_data.append(week_participants)
                activity_labels.append(f"Неделя {week_start.strftime('%d.%m')}")
                
        elif period == 'month':
            # Last 12 months
            for i in range(11, -1, -1):
                if i == 0:
                    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    month_end = now
                else:
                    month_date = now - timedelta(days=30*i)
                    month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    next_month = month_start.replace(month=month_start.month+1) if month_start.month < 12 else month_start.replace(year=month_start.year+1, month=1)
                    month_end = next_month - timedelta(days=1)
                
                month_start_ts = month_start.timestamp()
                month_end_ts = month_end.replace(hour=23, minute=59, second=59, microsecond=999999).timestamp()
                
                month_participants = 0
                for giveaway in giveaways.values():
                    giveaway_time = giveaway.get('end_time', 0)
                    if month_start_ts <= giveaway_time <= month_end_ts:
                        month_participants += len(giveaway.get('participants', []))
                
                activity_data.append(month_participants)
                activity_labels.append(month_start.strftime(date_format))
                
        elif period == 'year':
            # Last 5 years
            for i in range(4, -1, -1):
                year = now.year - i
                year_start = datetime(year, 1, 1).timestamp()
                year_end = datetime(year, 12, 31, 23, 59, 59, 999999).timestamp()
                
                year_participants = 0
                for giveaway in giveaways.values():
                    giveaway_time = giveaway.get('end_time', 0)
                    if year_start <= giveaway_time <= year_end:
                        year_participants += len(giveaway.get('participants', []))
                
                activity_data.append(year_participants)
                activity_labels.append(str(year))
        
        return {
            'activity_data': activity_data,
            'activity_labels': activity_labels,
            'period_name': period_name
        }
        
    except Exception as e:
        print(f"Error calculating activity statistics: {e}")
        return {
            'activity_data': [0] * 7,
            'activity_labels': [''] * 7,
            'period_name': 'дням'
        }

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
        
        # Calculate total winners from completed giveaways
        total_winners = 0
        for giveaway in giveaways.values():
            if giveaway.get('ended', False) and giveaway.get('winner_id'):
                total_winners += 1
        
        # Default activity for last 7 days (participants)
        activity_stats = calculate_activity_stats('day')
        
        return {
            'total_giveaways': total_giveaways,
            'active_giveaways': active_giveaways,
            'completed_giveaways': completed_giveaways,
            'total_participants': total_participants,
            'unique_participants': unique_participants,
            'total_winners': total_winners,
            'activity_data': activity_stats['activity_data'],
            'activity_labels': activity_stats['activity_labels'],
            'period_name': activity_stats['period_name']
        }
    except Exception as e:
        print(f"Error calculating statistics: {e}")
        return {
            'total_giveaways': 0,
            'active_giveaways': 0,
            'completed_giveaways': 0,
            'total_participants': 0,
            'unique_participants': 0,
            'total_winners': 0,
            'activity_data': [0] * 7,
            'activity_labels': [''] * 7,
            'period_name': 'дням'
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
    
    # Get recent giveaway events for logs section
    recent_events = get_recent_events(limit=10)
    formatted_events = []
    for event in recent_events:
        formatted_events.append({
            'timestamp': event.get('timestamp'),
            'message': format_event_message(event),
            'icon': get_event_icon(event.get('event_type', 'unknown')),
            'giveaway_id': event.get('giveaway_id')
        })
    
    return render_template('dashboard.html', 
                         stats=stats,
                         giveaways=giveaways_list,
                         bot_status=bot_online,
                         current_time=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                         recent_events=formatted_events)

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

@app.route('/api/activity/<period>')
def api_activity(period):
    """API endpoint for activity statistics by period"""
    if period not in ['day', 'week', 'month', 'year']:
        period = 'day'
    
    activity_stats = calculate_activity_stats(period)
    return jsonify(activity_stats)

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