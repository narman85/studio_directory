import os
import httpx
from supabase import create_client
from dotenv import load_dotenv

def setup_supabase():
    # Load environment variables
    load_dotenv()
    
    # Initialize Supabase client
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        # Read SQL setup script
        with open('db_setup.sql', 'r') as f:
            sql_script = f.read()
        
        # Execute the SQL script directly using the REST API
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates'
        }
        
        response = httpx.post(
            f'{supabase_url}/rest/v1/rpc/exec',
            headers=headers,
            json={'sql': sql_script}
        )
        
        if response.status_code == 200:
            print("Database tables created successfully!")
        else:
            print(f"Error creating database tables: {response.text}")
        
        # Create storage bucket for studio images
        try:
            response = httpx.post(
                f'{supabase_url}/storage/v1/bucket',
                headers=headers,
                json={
                    'name': 'studio-images',
                    'public': True,
                    'file_size_limit': 5242880,  # 5MB
                    'allowed_mime_types': ['image/*']
                }
            )
            
            if response.status_code in [200, 201]:
                print("Created 'studio-images' storage bucket")
            elif response.status_code == 400 and 'already exists' in response.text.lower():
                print("'studio-images' bucket already exists")
            else:
                print(f"Error creating storage bucket: {response.text}")
                
        except Exception as e:
            print(f"Error creating storage bucket: {e}")
        
        print("\nSupabase setup completed!")
        
    except Exception as e:
        print(f"Error during setup: {e}")

if __name__ == '__main__':
    setup_supabase()
