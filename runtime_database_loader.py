"""
Runtime Database Loader
Downloads the Pokemon card database at startup instead of including in deployment
"""
import os
import requests
import pandas as pd
from pathlib import Path

class RuntimeDatabaseLoader:
    def __init__(self):
        # Use the existing Google Sheets URL from your project
        self.sheets_url = "https://docs.google.com/spreadsheets/d/1JicEp6N0vrXVPbE6L1JGTLiNexXyPP5OraHQbDAqcXc/export?format=csv&gid=0"
        self.df = None
    
    def download_database(self):
        """Load database directly from Google Sheets"""
        try:
            print("Loading Pokemon card database from Google Sheets...")
            self.df = pd.read_csv(self.sheets_url)
            print(f"Database loaded successfully - {len(self.df)} cards")
            return True
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