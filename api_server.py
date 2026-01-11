"""
Flask API Server - מספק את המשחקים ב-API
"""

from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # אפשר CORS לכל הדומיינים

@app.route('/')
def home():
    return jsonify({
        'name': 'IFA Football Scraper API',
        'version': '1.0',
        'endpoints': {
            '/api/matches': 'Get all matches',
            '/api/live': 'Get only live matches',
            '/health': 'Health check'
        }
    })

@app.route('/api/matches')
def get_matches():
    """החזר את כל המשחקים"""
    try:
        if os.path.exists('matches.json'):
            with open('matches.json', 'r', encoding='utf-8') as f:
                matches = json.load(f)
            return jsonify(matches)
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/live')
def get_live():
    """החזר רק משחקים חיים מדף הלייב"""
    try:
        if os.path.exists('live_matches.json'):
            with open('live_matches.json', 'r', encoding='utf-8') as f:
                live = json.load(f)
            return jsonify(live)
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """בדיקת תקינות"""
    try:
        # בדוק מתי הקובץ עודכן לאחרונה
        if os.path.exists('matches.json'):
            mtime = os.path.getmtime('matches.json')
            last_update = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            with open('matches.json', 'r', encoding='utf-8') as f:
                matches = json.load(f)
            
            return jsonify({
                'status': 'ok',
                'last_update': last_update,
                'total_matches': len(matches),
                'live_matches': len([m for m in matches if m.get('status') == 'live'])
            })
        else:
            return jsonify({
                'status': 'no_data',
                'message': 'matches.json not found'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
