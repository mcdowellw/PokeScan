"""
Cloud-native WSGI using Google Sheets as database
Eliminates large file deployment issues
"""
import os
import threading
import time
from flask import Flask, jsonify, request, render_template_string
from runtime_database_loader import database_loader

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ChillAuraTCG_Secret_Key_2024')

# Global state
scanner_ready = False
initialization_error = None

@app.route('/health')
@app.route('/healthz')
def health():
    return jsonify({'status': 'healthy', 'scanner_ready': scanner_ready}), 200

@app.route('/')
def index():
    if scanner_ready:
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>CHILLAURA TCG Scanner</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>🎴 CHILLAURA TCG Scanner</h1>
    <div class="upload-area">
        <h3>Upload Pokemon Card Image</h3>
        <input type="file" id="cardImage" accept="image/*" />
        <button class="btn" onclick="scanCard()">Scan Card</button>
    </div>
    <div id="results"></div>
    
    <script>
    async function scanCard() {
        const fileInput = document.getElementById('cardImage');
        const file = fileInput.files[0];
        if (!file) return alert('Please select an image');
        
        const formData = new FormData();
        formData.append('file', file);
        
        document.getElementById('results').innerHTML = '<p>Scanning...</p>';
        
        try {
            const response = await fetch('/scan', { method: 'POST', body: formData });
            const result = await response.json();
            
            if (result.cards && result.cards.length > 0) {
                const card = result.cards[0];
                document.getElementById('results').innerHTML = `
                    <div style="border: 1px solid #ccc; padding: 15px; margin: 10px 0;">
                        <h3>${card.name}</h3>
                        <p><strong>Set:</strong> ${card.set}</p>
                        <p><strong>Number:</strong> ${card.number}</p>
                        <p><strong>Market Price:</strong> ${card.market_price}</p>
                        <p><strong>Rarity:</strong> ${card.rarity}</p>
                    </div>
                `;
            } else {
                document.getElementById('results').innerHTML = '<p>No cards found</p>';
            }
        } catch (error) {
            document.getElementById('results').innerHTML = '<p>Error scanning card</p>';
        }
    }
    </script>
</body>
</html>
        ''')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>TCG Scanner Loading</title>
        <meta http-equiv="refresh" content="3">
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; }
            .spinner { border: 3px solid #f3f3f3; border-top: 3px solid #007bff; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto; }
            @keyframes spin { 0% { transform: rotate(0deg) } 100% { transform: rotate(360deg) } }
        </style>
    </head>
    <body>
        <h1>TCG Scanner</h1>
        <div class="spinner"></div>
        <p>Loading database...</p>
    </body>
    </html>
    '''

@app.route('/scan', methods=['POST'])
def scan_card():
    if not scanner_ready:
        return jsonify({'error': 'Scanner not ready'}), 503
    
    try:
        # Basic card scanning without OpenAI for now
        return jsonify({
            'cards': [{
                'name': 'Sample Card',
                'set': 'Sample Set',
                'number': '001',
                'market_price': '$1.00',
                'rarity': 'Common'
            }],
            'message': 'Scanner working - connect OpenAI API for full functionality'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def initialize_scanner():
    """Initialize scanner in background"""
    global scanner_ready, initialization_error
    
    try:
        time.sleep(2)  # Allow server to start
        
        # Load database from Google Sheets
        database_loader.get_database()
        
        scanner_ready = True
        print("Scanner initialized successfully")
        
    except Exception as e:
        initialization_error = str(e)
        print(f"Initialization error: {e}")

# Start background initialization
threading.Thread(target=initialize_scanner, daemon=True).start()

application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))