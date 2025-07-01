#!/usr/bin/env python3
"""
Giveaway event logging system
Logs all giveaway-related events for detailed activity tracking
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

def ensure_log_directory():
    """Ensure the logs directory exists"""
    os.makedirs('data', exist_ok=True)

def load_giveaway_events():
    """Load giveaway events from json file"""
    ensure_log_directory()
    events_file = 'data/giveaway_events.json'
    
    if not os.path.exists(events_file):
        return []
    
    try:
        with open(events_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_giveaway_events(events):
    """Save giveaway events to json file"""
    ensure_log_directory()
    events_file = 'data/giveaway_events.json'
    
    try:
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving giveaway events: {e}")

def log_giveaway_event(event_type: str, giveaway_id: str, details: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None, user_name: Optional[str] = None):
    """
    Log a giveaway event
    
    Args:
        event_type: Type of event (created, ended, participant_joined, admin_ended, modified, etc.)
        giveaway_id: ID of the giveaway
        details: Additional event details
        user_id: Discord user ID (if applicable)
        user_name: Discord user name (if applicable)
    """
    events = load_giveaway_events()
    
    event = {
        'id': len(events) + 1,
        'timestamp': datetime.now().timestamp(),
        'event_type': event_type,
        'giveaway_id': giveaway_id,
        'user_id': user_id,
        'user_name': user_name,
        'details': details or {}
    }
    
    events.append(event)
    
    # Keep only last 1000 events to prevent file bloat
    if len(events) > 1000:
        events = events[-1000:]
    
    save_giveaway_events(events)

def get_recent_events(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent giveaway events"""
    events = load_giveaway_events()
    
    # Sort by timestamp, most recent first
    events.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    return events[:limit]

def get_events_by_giveaway(giveaway_id: str) -> List[Dict[str, Any]]:
    """Get all events for a specific giveaway"""
    events = load_giveaway_events()
    
    giveaway_events = [e for e in events if e.get('giveaway_id') == giveaway_id]
    giveaway_events.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
    
    return giveaway_events

def format_event_message(event: Dict[str, Any]) -> str:
    """Format event into human-readable message"""
    event_type = event.get('event_type', 'unknown')
    giveaway_id = event.get('giveaway_id', 'unknown')
    user_name = event.get('user_name', 'Неизвестный пользователь')
    details = event.get('details', {})
    
    messages = {
        'created': f"Создан розыгрыш {giveaway_id}",
        'ended': f"Розыгрыш {giveaway_id} завершен автоматически",
        'admin_ended': f"Розыгрыш {giveaway_id} завершен администратором",
        'cancelled': f"Розыгрыш {giveaway_id} отменен администратором",
        'participant_joined': f"{user_name} присоединился к розыгрышу {giveaway_id}",
        'winner_selected': f"Выбран победитель в розыгрыше {giveaway_id}: {user_name}",
        'prize_assigned': f"Назначен приз в розыгрыше {giveaway_id}",
        'title_changed': f"Изменено название розыгрыша {giveaway_id}",
        'description_changed': f"Изменено описание розыгрыша {giveaway_id}",
        'time_extended': f"Продлено время розыгрыша {giveaway_id}",
        'winners_changed': f"Изменено количество победителей в розыгрыше {giveaway_id}",
        'gif_attached': f"Прикреплена анимация к розыгрышу {giveaway_id}",
        'prizes_modified': f"Изменены призы в розыгрыше {giveaway_id}"
    }
    
    base_message = messages.get(event_type, f"Событие {event_type} в розыгрыше {giveaway_id}")
    
    # Add details if available
    if details:
        if 'prize_name' in details:
            base_message += f" (Приз: {details['prize_name']})"
        if 'old_value' in details and 'new_value' in details:
            base_message += f" (Было: {details['old_value']}, Стало: {details['new_value']})"
        if 'participant_count' in details:
            base_message += f" (Всего участников: {details['participant_count']})"
    
    return base_message

def get_event_icon(event_type: str) -> str:
    """Get FontAwesome icon for event type"""
    icons = {
        'created': 'fas fa-plus-circle text-success',
        'ended': 'fas fa-flag-checkered text-primary',
        'admin_ended': 'fas fa-user-shield text-warning',
        'cancelled': 'fas fa-times-circle text-danger',
        'participant_joined': 'fas fa-user-plus text-info',
        'winner_selected': 'fas fa-trophy text-warning',
        'prize_assigned': 'fas fa-gift text-success',
        'title_changed': 'fas fa-edit text-secondary',
        'description_changed': 'fas fa-edit text-secondary',
        'time_extended': 'fas fa-clock text-info',
        'winners_changed': 'fas fa-users text-info',
        'gif_attached': 'fas fa-image text-success',
        'prizes_modified': 'fas fa-gift text-info'
    }
    
    return icons.get(event_type, 'fas fa-info-circle text-muted')