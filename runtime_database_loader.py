"""
Runtime Database Loader
Downloads the Pokemon card database at startup instead of including in deployment
"""
import os
import requests
import pandas as pd
import json
import tempfile
from pathlib import Path

class RuntimeDatabaseLoader:
    def __init__(self):
        # Use the existing Google Sheets URL from your project
        self.sheets_url = "https://docs.google.com/spreadsheets/d/1JicEp6N0vrXVPbE6L1JGTLiNexXyPP5OraHQbDAqcXc/export?format=csv&gid=0"
        self.df = None
    
    def setup_google_credentials(self):
        """Setup Google credentials from environment variable"""
        try:
            # Check if credentials are provided as environment variable
            creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
            if creds_json:
                # Write credentials to temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    f.write(creds_json)
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name
                return True
            return False
        except Exception as e:
            print(f"Failed to setup Google credentials: {e}")
            return False
    
    def download_database(self):
        """Load database directly from Google Sheets"""
        try:
            print("Loading Pokemon card database from Google Sheets...")
            
            # Try with credentials first
            self.setup_google_credentials()
            
            # Attempt to load from Google Sheets
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(self.sheets_url, headers=headers)
            
            if response.status_code == 200:
                from io import StringIO
                self.df = pd.read_csv(StringIO(response.text))
                print(f"Database loaded successfully - {len(self.df)} cards")
                return True
            else:
                print(f"Failed to load database: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Failed to load database: {e}")
            return False
    
    def get_database(self):
        """Get the loaded database"""
        if self.df is None:
            if not self.download_database():
                raise Exception("Failed to load database from any source")
        return self.df
    
    def search_card(self, name, number=None):
        """Search for a card in the database"""
        df = self.get_database()
        
        if df is None or df.empty:
            return None
        
        # Ensure columns exist
        if 'name' not in df.columns:
            return None
            
        # Search by name
        name_matches = df[df['name'].astype(str).str.lower().str.contains(name.lower(), na=False, regex=False)]
        
        if number and 'number' in df.columns:
            # Also filter by number if provided
            number_matches = name_matches[name_matches['number'].astype(str).str.contains(str(number), na=False, regex=False)]
            return number_matches if len(number_matches) > 0 else name_matches
        
        return name_matches

# Global instance
database_loader = RuntimeDatabaseLoader()