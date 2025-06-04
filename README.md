# Pokemon TCG Scanner

A comprehensive Pokemon Trading Card Game scanner that recognizes cards and provides market prices and inventory data.

## Features

- **Card Recognition**: Upload Pokemon card images for automatic identification
- **Market Pricing**: Real-time TCGPlayer market price data
- **Inventory Management**: Google Sheets integration for inventory tracking
- **Search Function**: Find cards by name and number
- **Library View**: Browse complete card database

## Deployment

This application is deployed on Railway and loads the Pokemon card database from Google Sheets at runtime.

### Environment Variables Required

- `GOOGLE_CREDENTIALS_JSON`: Google service account credentials for Sheets access
- `OPENAI_API_KEY`: OpenAI API key for card image analysis (optional)

### Database Source

The application connects to Google Sheets ID: `1JicEp6N0vrXVPbE6L1JGTLiNexXyPP5OraHQbDAqcXc`

## Usage

1. Upload a Pokemon card image
2. Click "Scan Card" to identify the card
3. View market price and inventory information
4. Use the search function to find specific cards
5. Browse the complete library of cards

## Technical Details

- **Framework**: Flask (Python)
- **Database**: Google Sheets (runtime loaded)
- **Hosting**: Railway
- **Image Analysis**: OpenAI GPT-4 Vision
- **Market Data**: Pokemon TCG IO API