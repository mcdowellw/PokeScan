"""
Railway Pokemon TCG Scanner - Complete Implementation
Uses authentic Google Sheets database and OpenAI for card recognition
"""
import os
import pandas as pd
import base64
import json
import tempfile
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ChillAuraTCG_Secret_Key_2024')

# Global variables
df = None
scanner_ready = False

def load_database():
    """Load Pokemon card database from Google Sheets"""
    global df, scanner_ready
    
    try:
        print("Loading Pokemon card database from Google Sheets...")
        
        # Try Google Sheets API with credentials
        creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
        if creds_json:
            try:
                import gspread
                from google.oauth2.service_account import Credentials
                
                print("Google credentials found, attempting connection...")
                creds_dict = json.loads(creds_json)
                
                # Define required scopes for Google Sheets
                scopes = [
                    'https://www.googleapis.com/auth/spreadsheets.readonly',
                    'https://www.googleapis.com/auth/drive.readonly'
                ]
                
                credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                gc = gspread.authorize(credentials)
                
                # Open the CHILLAURA TCG Library spreadsheet
                sheet = gc.open_by_key("1JicEp6N0vrXVPbE6L1JGTLiNexXyPP5OraHQbDAqcXc")
                worksheet = sheet.get_worksheet(0)  # First sheet
                records = worksheet.get_all_records()
                
                if records:
                    df = pd.DataFrame(records)
                    print(f"✓ Database loaded from Google Sheets: {len(df)} cards")
                    scanner_ready = True
                    return True
                else:
                    print("Google Sheets returned empty data")
                    
            except Exception as e:
                print(f"Google Sheets authentication failed: {e}")
                print("Verify that GOOGLE_CREDENTIALS_JSON environment variable is set correctly")
        else:
            print("GOOGLE_CREDENTIALS_JSON environment variable not found")
        
        # If Google Sheets fails, notify user that credentials are needed
        print("Failed to load database: Google Sheets authentication required")
        print("Please ensure GOOGLE_CREDENTIALS_JSON is properly configured in Railway")
        return False
        
    except Exception as e:
        print(f"Database loading failed: {e}")
        return False

def analyze_card_with_openai(image_data):
    """Analyze Pokemon card using OpenAI Vision API"""
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return None
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-4-vision-preview',
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': 'Analyze this Pokemon card image and extract: card name, set name, card number, rarity. Return as JSON format: {"name": "", "set": "", "number": "", "rarity": ""}'
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:image/jpeg;base64,{image_data}'
                            }
                        }
                    ]
                }
            ],
            'max_tokens': 300
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            try:
                return json.loads(content)
            except:
                return {'name': 'Card detected', 'set': 'Unknown', 'number': '???', 'rarity': 'Unknown'}
        
        return None
        
    except Exception as e:
        print(f"OpenAI analysis error: {e}")
        return None

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'scanner_ready': scanner_ready}), 200

@app.route('/status')
def status():
    return jsonify({
        'scanner_ready': scanner_ready,
        'database_size': len(df) if df is not None else 0,
        'openai_available': bool(os.environ.get('OPENAI_API_KEY')),
        'google_sheets_configured': bool(os.environ.get('GOOGLE_CREDENTIALS_JSON')),
        'status': 'ready' if scanner_ready else 'loading'
    })

@app.route('/')
def index():
    if not scanner_ready:
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pokemon TCG Scanner</title>
            <meta http-equiv="refresh" content="5">
            <style>
                body { 
                    font-family: Arial; 
                    text-align: center; 
                    padding: 50px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    min-height: 100vh;
                    margin: 0;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background: rgba(255,255,255,0.1);
                    padding: 3rem;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                }
                .loading { 
                    font-size: 1.2rem; 
                    margin-top: 20px; 
                }
                .status {
                    background: rgba(255,255,255,0.2);
                    padding: 1rem;
                    border-radius: 10px;
                    margin-top: 2rem;
                    text-align: left;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Pokemon TCG Scanner</h1>
                <div class="loading">Loading database from Google Sheets...</div>
                <div class="status">
                    <strong>Status:</strong><br>
                    • Google Sheets: {{ "Configured" if google_sheets else "Needs Configuration" }}<br>
                    • OpenAI API: {{ "Ready" if openai else "Needs Configuration" }}<br>
                    • Database: {{ database_size }} cards loaded
                </div>
                <p><small>If loading persists, check Railway environment variables</small></p>
            </div>
        </body>
        </html>
        ''', 
        google_sheets=bool(os.environ.get('GOOGLE_CREDENTIALS_JSON')),
        openai=bool(os.environ.get('OPENAI_API_KEY')),
        database_size=len(df) if df is not None else 0
        )
    
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CHILLAURA Pokemon TCG Scanner</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .header {
                background: rgba(255,255,255,0.95);
                padding: 2rem;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                margin-bottom: 2rem;
            }
            h1 {
                color: #2c3e50;
                font-size: 3rem;
                margin-bottom: 0.5rem;
            }
            .subtitle {
                color: #7f8c8d;
                font-size: 1.2rem;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                padding: 0 1rem;
            }
            .stats {
                background: rgba(255,255,255,0.9);
                border-radius: 15px;
                padding: 1.5rem;
                margin-bottom: 2rem;
                text-align: center;
                color: #2c3e50;
            }
            .scanner-section {
                background: white;
                border-radius: 20px;
                padding: 3rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                margin-bottom: 2rem;
            }
            .upload-area {
                border: 3px dashed #3498db;
                border-radius: 15px;
                padding: 4rem 2rem;
                text-align: center;
                background: linear-gradient(135deg, #f8f9fa 0%, #e3f2fd 100%);
                transition: all 0.3s ease;
                cursor: pointer;
            }
            .upload-area:hover {
                border-color: #2980b9;
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(52, 152, 219, 0.2);
            }
            .upload-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
            }
            .btn {
                background: linear-gradient(135deg, #3498db, #2980b9);
                color: white;
                padding: 15px 40px;
                border: none;
                border-radius: 30px;
                font-size: 1.2rem;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 20px;
                box-shadow: 0 6px 20px rgba(52, 152, 219, 0.3);
            }
            .btn:hover:not(:disabled) {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(52, 152, 219, 0.4);
            }
            .btn:disabled {
                background: #bdc3c7;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            .card-result {
                background: white;
                border-radius: 15px;
                padding: 2rem;
                margin: 1.5rem 0;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                border-left: 6px solid #3498db;
                transition: transform 0.3s ease;
            }
            .card-result:hover {
                transform: translateY(-3px);
            }
            .card-name {
                font-size: 2rem;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 1rem;
            }
            .card-info {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
            }
            .info-item {
                background: #f8f9fa;
                padding: 1rem;
                border-radius: 10px;
                border: 1px solid #e9ecef;
            }
            .info-label {
                font-weight: bold;
                color: #495057;
                font-size: 0.9rem;
                margin-bottom: 0.5rem;
                text-transform: uppercase;
            }
            .info-value {
                color: #2c3e50;
                font-size: 1.1rem;
                font-weight: 500;
            }
            .loading {
                text-align: center;
                padding: 3rem;
                color: #7f8c8d;
                font-size: 1.2rem;
            }
            .error {
                background: #e74c3c;
                color: white;
                padding: 1.5rem;
                border-radius: 10px;
                margin: 1.5rem 0;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Pokemon TCG Scanner</h1>
            <p class="subtitle">AI-Powered Card Recognition with Live Database</p>
        </div>
        
        <div class="container">
            <div class="stats">
                <strong>Database:</strong> {{ database_size }} Pokemon cards loaded from Google Sheets<br>
                <strong>AI Recognition:</strong> {{ 'Enabled' if openai_available else 'Configure OpenAI API' }}
            </div>
            
            <div class="scanner-section">
                <div class="upload-area" onclick="document.getElementById('cardImage').click()">
                    <div class="upload-icon">📷</div>
                    <h3>Upload Pokemon Card Image</h3>
                    <p>AI will analyze your card and find matches in the live database</p>
                    <input type="file" id="cardImage" accept="image/*" style="display: none;" />
                </div>
                
                <div style="text-align: center;">
                    <button class="btn" onclick="scanCard()" id="scanBtn" disabled>
                        Analyze Card
                    </button>
                </div>
                
                <div id="results"></div>
            </div>
        </div>
        
        <script>
        document.getElementById('cardImage').addEventListener('change', function(e) {
            document.getElementById('scanBtn').disabled = !e.target.files[0];
        });
        
        async function scanCard() {
            const file = document.getElementById('cardImage').files[0];
            if (!file) return;
            
            const btn = document.getElementById('scanBtn');
            btn.disabled = true;
            btn.textContent = 'Analyzing...';
            
            document.getElementById('results').innerHTML = '<div class="loading">AI analyzing card image...</div>';
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/scan', { method: 'POST', body: formData });
                const result = await response.json();
                
                let html = '';
                if (result.cards?.length > 0) {
                    result.cards.forEach(card => {
                        html += `
                            <div class="card-result">
                                <div class="card-name">${card.name}</div>
                                <div class="card-info">
                                    <div class="info-item">
                                        <div class="info-label">Set</div>
                                        <div class="info-value">${card.set}</div>
                                    </div>
                                    <div class="info-item">
                                        <div class="info-label">Number</div>
                                        <div class="info-value">${card.number}</div>
                                    </div>
                                    <div class="info-item">
                                        <div class="info-label">Rarity</div>
                                        <div class="info-value">${card.rarity}</div>
                                    </div>
                                    <div class="info-item">
                                        <div class="info-label">Market Price</div>
                                        <div class="info-value">${card.market_price || 'N/A'}</div>
                                    </div>
                                </div>
                                ${card.tcgplayer_url ? `<div style="margin-top: 1rem; text-align: center;"><a href="${card.tcgplayer_url}" target="_blank" style="color: #3498db; text-decoration: none; font-weight: bold;">View on TCGPlayer →</a></div>` : ''}
                            </div>
                        `;
                    });
                } else if (result.error) {
                    html = `<div class="error">${result.error}</div>`;
                } else {
                    html = '<div class="error">No matching cards found. Try a different image or angle.</div>';
                }
                
                document.getElementById('results').innerHTML = html;
            } catch (error) {
                document.getElementById('results').innerHTML = '<div class="error">Error analyzing card. Please try again.</div>';
            }
            
            btn.disabled = false;
            btn.textContent = 'Analyze Card';
        }
        </script>
    </body>
    </html>
    ''', 
    database_size=len(df) if df is not None else 0, 
    openai_available=bool(os.environ.get('OPENAI_API_KEY'))
    )

@app.route('/scan', methods=['POST'])
def scan_card():
    if not scanner_ready:
        return jsonify({'error': 'Database not loaded. Please check Google Sheets configuration.'}), 503
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Read and encode image
        image_data = base64.b64encode(file.read()).decode('utf-8')
        
        # Analyze with OpenAI if available
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            card_info = analyze_card_with_openai(image_data)
            if card_info:
                # Search database for matches
                matches = search_database(card_info)
                if matches:
                    return jsonify({'cards': matches})
        
        return jsonify({'error': 'Card analysis requires OpenAI API configuration'})
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

def search_database(card_info):
    """Search database for card matches"""
    try:
        if df is None or len(df) == 0:
            return []
        
        matches = []
        card_name = card_info.get('name', '').lower()
        
        # Search by name similarity
        for _, row in df.iterrows():
            db_name = str(row.get('Name', '')).lower()
            if card_name and (card_name in db_name or db_name in card_name):
                matches.append({
                    'name': str(row.get('Name', 'Unknown')),
                    'set': str(row.get('Set', 'Unknown Set')),
                    'number': str(row.get('Card Number', '???')),
                    'rarity': str(row.get('Rarity', 'Unknown')),
                    'market_price': str(row.get('Market Price', 'N/A')),
                    'tcgplayer_url': str(row.get('TCGPlayer Link', '')) if 'TCGPlayer Link' in row else ''
                })
                if len(matches) >= 3:
                    break
        
        return matches
        
    except Exception as e:
        print(f"Database search error: {e}")
        return []

if __name__ == '__main__':
    print("Starting Pokemon TCG Scanner...")
    success = load_database()
    if not success:
        print("Warning: Database not loaded. Check environment configuration.")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)