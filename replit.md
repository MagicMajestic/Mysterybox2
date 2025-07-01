# MysteryBox Discord Bot

## Overview

MysteryBox is a Discord bot built with discord.py 2.5.2 that creates timed giveaways with random prizes. The bot operates without a web interface and is designed to manage giveaways directly within Discord channels. Users can participate in giveaways by clicking buttons, and winners are automatically selected when giveaways end.

## System Architecture

### Bot Architecture
- **Framework**: Discord.py 2.5.2 using slash commands
- **Language**: Python 3.11+
- **Structure**: Modular cog-based architecture
- **Data Storage**: JSON-based file system for persistence
- **Deployment**: Replit-based hosting with environment variable configuration

### Core Components
- **Main Bot Class** (`bot.py`): Central bot instance with guild restrictions
- **Giveaway Cog** (`cogs/giveaway.py`): Primary functionality for giveaway management
- **Database Utilities** (`utils/database.py`): JSON file management for data persistence
- **Asset Management**: File-based storage for GIFs and prize lists

## Key Components

### 1. Giveaway Management System
- Creates timed giveaways with customizable duration
- Interactive button-based participation
- Automatic winner selection with random prize assignment
- Support for early termination and cancellation
- Participant tracking and management

### 2. Prize System
- Individual prize management (add/remove/list)
- Prize list templates loaded from text files
- Support for prize ranges (e.g., "1-3" for selecting multiple items)
- Emoji-enhanced prize display
- File-based prize list importing

### 3. Asset Management
- GIF storage for winner celebration animations
- Prize list file management in structured directories
- Template system for common giveaway formats
- Support for custom uploaded content

### 4. Administrative Controls
- Admin-only access to all giveaway commands
- Guild-specific bot operation (restricted to allowed servers)
- Participant viewing and giveaway monitoring
- Manual giveaway control (end early, cancel)

## Data Flow

### Giveaway Creation Flow
1. Admin creates giveaway with `/mysterybox` command
2. Bot creates interactive embed with participation button
3. Giveaway data stored in JSON file with unique ID
4. Async task scheduled for automatic completion

### Participation Flow
1. User clicks participation button
2. Bot validates user eligibility and adds to participants list
3. Updated participant count displayed in embed
4. Data persisted to JSON storage

### Completion Flow
1. Timer expires or admin manually ends giveaway
2. Random winner selected from participants
3. Random prize selected from assigned prize pool
4. Winner announcement with optional GIF celebration
5. Giveaway marked as ended in storage

## External Dependencies

### Core Dependencies
- **discord.py** (>=2.5.2): Discord API interaction
- **python-dotenv**: Environment variable management
- **aiohttp**: Async HTTP client for Discord communication
- **asyncio**: Asynchronous task management

### Development Dependencies
- **flask**: Web framework (unused but available)
- **psycopg2-binary**: PostgreSQL adapter (unused but available)
- **email-validator**: Email validation utilities
- **requests**: HTTP request handling

### System Dependencies
- **logging**: Comprehensive logging to console and files
- **json**: Data serialization and storage
- **os**: File system operations
- **random**: Prize and winner selection
- **datetime**: Time management for giveaways

## Deployment Strategy

### Environment Configuration
- **TOKEN**: Discord bot token (required)
- **APPLICATION_ID**: Discord application ID
- **DEBUG_MODE**: Development logging toggle
- **SYNC_COMMANDS**: Force command synchronization

### File Structure
```
/data/
  ├── giveaways.json (active and completed giveaways)
  ├── prizes.json (individual prize definitions)
  ├── gifs.json (celebration GIF metadata)
  ├── prize_lists.json (prize list metadata)
  ├── images/ (uploaded GIF files)
  └── prize_lists/ (text files with prize definitions)
```

### Server Restrictions
- Bot restricted to specific guild IDs for security
- Admin role verification for all commands
- Logging system for monitoring and debugging

### Error Handling
- Comprehensive exception logging
- Graceful degradation for missing assets
- Retry mechanisms for Discord API interactions
- File system error recovery

## Changelog
```
Changelog:
- July 01, 2025. Initial setup
- July 01, 2025. Successfully migrated from Replit Agent to Replit environment
  - Configured Discord bot to run properly in Replit
  - Added DISCORD_TOKEN secret for secure authentication
  - Verified bot connects and syncs 18 commands successfully
  - Bot running in production mode with server whitelist restrictions
- July 01, 2025. Fixed persistent button functionality and enhanced web interface
  - FIXED: Persistent view buttons now work correctly after bot restarts
  - Added persistent view registration in bot.py setup_hook
  - Created comprehensive dark-themed web interface with raspberry accent color
  - Added detailed giveaway view page with participants, winners, and prizes
  - Enhanced dashboard with statistics, charts, and real-time data
  - Improved prizes page with toggle views and usage statistics
  - Advanced logs page with filtering, search, and auto-refresh
  - Implemented Majestic Party San Francisco branding throughout interface
- July 01, 2025. Completed migration from Replit Agent to standard Replit environment
  - Successfully installed all required dependencies (discord.py, flask, gunicorn)
  - Configured DISCORD_TOKEN secret for secure authentication
  - Bot connects successfully and syncs 18 commands
  - Web interface runs on port 5000 with gunicorn server
  - Both Discord bot and web dashboard operational
  - Production mode active with server whitelist restrictions
- July 01, 2025. Enhanced dashboard with giveaway event logging and statistics improvements
  - Added comprehensive giveaway event logging system tracking all activities
  - Created recent events section on dashboard showing last 10 giveaway events
  - Replaced "Призов" (Prizes) statistic with "Победителей" (Winners) count
  - Enhanced activity statistics to track participant counts instead of giveaway counts
  - Improved event tracking with detailed logging of creation, participation, completion, and admin actions
- July 01, 2025. Added comprehensive prize and prize list management to web interface
  - Created full web interface for prize management (add, remove, view prizes)
  - Added prize list management system (create, edit, view, delete prize lists)
  - Implemented API endpoints for all prize operations (/api/prizes/*, /api/prize-lists/*)
  - Added modal dialogs for user-friendly prize and list management
  - Enhanced prizes page with management controls and prize list display
  - All Discord bot prize functionality now available through web interface
- July 01, 2025. Successfully completed migration from Replit Agent to standard Replit environment
  - Installed all required dependencies (discord.py 2.5.2, flask, gunicorn, aiohttp, python-dotenv)
  - Configured secure Discord bot authentication with DISCORD_TOKEN secret
  - Bot successfully connects and syncs 18 commands to Discord servers
  - Web interface runs on port 5000 using gunicorn server with proper configuration
  - Enhanced prizes page with drag-and-drop file upload functionality for prize lists
  - Fixed prize list management interface with proper view/edit capabilities
  - Both Discord bot and web dashboard fully operational in production mode
```

## User Preferences
```
Preferred communication style: Simple, everyday language.
```