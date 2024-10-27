# config.py

# Application Configuration
APP_NAME = "Temtemone Submissions Dashboard"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A dashboard for monitoring submissions and analytics for the Temtemone platform."

# Layout Settings
PAGE_TITLE = f"{APP_NAME} - {APP_DESCRIPTION}"
PAGE_ICON = "📊"  # You can change this to any emoji or icon representing your app

# Theme Settings
THEME = {
    "primaryColor": "#F39C12",  
    "backgroundColor": "#FFFFFF",
    "secondaryBackgroundColor": "#F4F4F4",
    "textColor": "#333333",
    "font": "sans serif"
}

# Data Paths
DATA_PATHS = {
    "RAW_DATA": "data/raw",
    "PROCESSED_DATA": "data/processed",
    "EXTERNAL_DATA": "data/external"
}

# Other Constants
DEFAULT_PAGE = "Home"
