from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase configuration from environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def setup_database():
    try:
        # Insert a test studio
        studio_data = {
            'name': 'Test Studio',
            'description': 'A test studio with great lighting and equipment',
            'price': 100.00,
            'phone_number': '123-456-7890',
            'address': '123 Test St, San Francisco, CA 94105'
        }
        result = supabase.table('studios').insert(studio_data).execute()
        print("Test studio data inserted!")
        
        # Get the studio ID from the result
        studio_id = result.data[0]['id']

        # Insert test studio image
        image_data = {
            'studio_id': studio_id,
            'image_path': '/static/images/default-studio.jpg',
            'is_primary': True
        }
        supabase.table('studio_images').insert(image_data).execute()
        print("Test studio image data inserted!")

        # Insert test studio stats
        stats_data = {
            'studio_id': studio_id,
            'views': 0,
            'phone_reveals': 0,
            'last_viewed_at': None
        }
        supabase.table('studio_stats').insert(stats_data).execute()
        print("Test studio stats data inserted!")

        print("Database setup completed successfully!")
        return True

    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        return False

if __name__ == '__main__':
    setup_database()
