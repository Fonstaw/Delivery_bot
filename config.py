import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')      # For future API use
SUPABASE_KEY = os.getenv('SUPABASE_KEY')       # For future API use

# NEW: Direct Database Connection
SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')  # Get from Supabase → Project Settings → Database

# App Configuration
APP_URL = os.getenv('APP_URL', 'https://your-app-name')

# Channel Configuration (Channel IDs from @getmyid_bot)
CHANNELS = {
    'female_main': os.getenv('CHANNEL_FEMALE_MAIN'),
    'male_main': os.getenv('CHANNEL_MALE_MAIN'),
    'female_tecno': os.getenv('CHANNEL_FEMALE_TECNO'),
    'male_tecno': os.getenv('CHANNEL_MALE_TECNO'),
    'agri': os.getenv('CHANNEL_AGRI')
}

# Admin Configuration (Your Telegram ID)
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]

# Price Configuration
PRICE_PER_ITEM = 6.65