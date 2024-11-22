from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app, supabase
from functools import wraps
import os
from werkzeug.security import check_password_hash
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    try:
        # Get all studios with their primary images
        response = supabase.table('studios') \
            .select('*, studio_images!inner(image_path)') \
            .eq('studio_images.is_primary', True) \
            .execute()
        studios = response.data
        return render_template('index.html', studios=studios)
    except Exception as e:
        flash(f'Error loading studios: {str(e)}', 'error')
        return render_template('index.html', studios=[])

@app.route('/studio/<studio_id>')
def studio_detail(studio_id):
    try:
        # Get studio details
        response = supabase.table('studios') \
            .select('*, studio_images(image_path, is_primary)') \
            .eq('id', studio_id) \
            .single() \
            .execute()
        
        if not response.data:
            flash('Studio not found', 'error')
            return redirect(url_for('index'))
        
        studio = response.data
        
        # Update view count
        try:
            # Check if stats exist
            stats_response = supabase.table('studio_stats') \
                .select('*') \
                .eq('studio_id', studio_id) \
                .execute()
            
            current_time = datetime.utcnow().isoformat()
            
            if stats_response.data and len(stats_response.data) > 0:
                # Update existing stats
                supabase.table('studio_stats') \
                    .update({
                        'views': stats_response.data[0]['views'] + 1,
                        'last_viewed_at': current_time
                    }) \
                    .eq('studio_id', studio_id) \
                    .execute()
            else:
                # Create new stats
                supabase.table('studio_stats') \
                    .insert({
                        'studio_id': studio_id,
                        'views': 1,
                        'phone_reveals': 0,
                        'last_viewed_at': current_time
                    }) \
                    .execute()
            
            print(f"Updated view count for studio {studio_id}")
        except Exception as e:
            print(f"Error updating view stats: {str(e)}")
        
        return render_template('studio_detail.html', studio=studio)
    except Exception as e:
        flash(f'Error loading studio: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == os.getenv('ADMIN_USERNAME') and \
           check_password_hash(os.getenv('ADMIN_PASSWORD_HASH'), password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    try:
        # First get all studios with their stats
        response = supabase.table('studios') \
            .select('*, studio_stats(*)') \
            .execute()
        
        studios = response.data
        print(f"Found {len(studios)} studios")
        
        # Then get primary images for each studio
        for studio in studios:
            # Get primary image
            image_response = supabase.table('studio_images') \
                .select('image_path') \
                .eq('studio_id', studio['id']) \
                .eq('is_primary', True) \
                .limit(1) \
                .execute()
            
            # Add image data to studio
            studio['studio_images'] = image_response.data if image_response.data else []
            
            # Initialize stats if they don't exist
            if not studio.get('studio_stats') or len(studio['studio_stats']) == 0:
                studio['studio_stats'] = [{
                    'views': 0,
                    'phone_reveals': 0,
                    'last_viewed_at': None
                }]
            print(f"Studio {studio['name']} stats: {studio['studio_stats']}")
        
        return render_template('admin_dashboard.html', studios=studios)
    except Exception as e:
        print(f"Admin dashboard error: {str(e)}")
        flash(f'Error loading studios: {str(e)}', 'error')
        return render_template('admin_dashboard.html', studios=[])

@app.route('/admin/studio/add', methods=['GET', 'POST'])
@admin_required
def add_studio():
    if request.method == 'POST':
        try:
            # Create studio
            studio_data = {
                'name': request.form['name'],
                'description': request.form['description'],
                'address': request.form['address'],
                'phone_number': request.form['phone'],
                'price': float(request.form['price'])
            }
            
            studio_response = supabase.table('studios').insert(studio_data).execute()
            studio_id = studio_response.data[0]['id']
            
            # Handle image uploads
            main_image = request.files['main_image']
            if main_image:
                main_image_path = f'storage/studios/{studio_id}/main.jpg'
                os.makedirs(os.path.dirname(f'static/{main_image_path}'), exist_ok=True)
                main_image.save(f'static/{main_image_path}')
                
                # Save main image reference
                supabase.table('studio_images').insert({
                    'studio_id': studio_id,
                    'image_path': main_image_path,
                    'is_primary': True
                }).execute()
            
            # Handle additional images
            additional_images = request.files.getlist('additional_images')
            for i, image in enumerate(additional_images):
                if image:
                    image_path = f'storage/studios/{studio_id}/image_{i+1}.jpg'
                    os.makedirs(os.path.dirname(f'static/{image_path}'), exist_ok=True)
                    image.save(f'static/{image_path}')
                    
                    # Save additional image reference
                    supabase.table('studio_images').insert({
                        'studio_id': studio_id,
                        'image_path': image_path,
                        'is_primary': False
                    }).execute()
            
            flash('Studio added successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error adding studio: {str(e)}', 'error')
    
    return render_template('add_studio.html')

@app.route('/admin/studio/<studio_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_studio(studio_id):
    if request.method == 'POST':
        try:
            # Update studio
            studio_data = {
                'name': request.form['name'],
                'description': request.form['description'],
                'address': request.form['address'],
                'phone_number': request.form['phone'],
                'price': float(request.form['price'])
            }
            
            supabase.table('studios').update(studio_data).eq('id', studio_id).execute()
            
            # Handle main image update
            main_image = request.files['main_image']
            if main_image:
                main_image_path = f'storage/studios/{studio_id}/main.jpg'
                os.makedirs(os.path.dirname(f'static/{main_image_path}'), exist_ok=True)
                main_image.save(f'static/{main_image_path}')
                
                # Update or create main image reference
                existing_main = supabase.table('studio_images') \
                    .select('id') \
                    .eq('studio_id', studio_id) \
                    .eq('is_primary', True) \
                    .execute()
                
                if existing_main.data:
                    supabase.table('studio_images') \
                        .update({'image_path': main_image_path}) \
                        .eq('id', existing_main.data[0]['id']) \
                        .execute()
                else:
                    supabase.table('studio_images').insert({
                        'studio_id': studio_id,
                        'image_path': main_image_path,
                        'is_primary': True
                    }).execute()
            
            # Handle additional images
            additional_images = request.files.getlist('additional_images')
            if additional_images:
                # Remove old additional images
                supabase.table('studio_images') \
                    .delete() \
                    .eq('studio_id', studio_id) \
                    .eq('is_primary', False) \
                    .execute()
                
                # Add new additional images
                for i, image in enumerate(additional_images):
                    if image:
                        image_path = f'storage/studios/{studio_id}/image_{i+1}.jpg'
                        os.makedirs(os.path.dirname(f'static/{image_path}'), exist_ok=True)
                        image.save(f'static/{image_path}')
                        
                        supabase.table('studio_images').insert({
                            'studio_id': studio_id,
                            'image_path': image_path,
                            'is_primary': False
                        }).execute()
            
            flash('Studio updated successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error updating studio: {str(e)}', 'error')
    
    try:
        # Get studio details for editing
        response = supabase.table('studios') \
            .select('*, studio_images(image_path, is_primary)') \
            .eq('id', studio_id) \
            .single() \
            .execute()
        
        if not response.data:
            flash('Studio not found', 'error')
            return redirect(url_for('admin_dashboard'))
        
        return render_template('edit_studio.html', studio=response.data)
    except Exception as e:
        flash(f'Error loading studio: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/studio/<studio_id>/delete', methods=['POST'])
@admin_required
def delete_studio(studio_id):
    try:
        # Delete studio (will cascade to images and stats)
        supabase.table('studios').delete().eq('id', studio_id).execute()
        
        # Delete image files
        studio_dir = f'static/storage/studios/{studio_id}'
        if os.path.exists(studio_dir):
            for file in os.listdir(studio_dir):
                os.remove(os.path.join(studio_dir, file))
            os.rmdir(studio_dir)
        
        flash('Studio deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting studio: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/api/studio/<studio_id>/reveal-phone', methods=['POST'])
def reveal_phone(studio_id):
    try:
        # Get studio
        studio_response = supabase.table('studios') \
            .select('phone_number') \
            .eq('id', studio_id) \
            .single() \
            .execute()
        
        if not studio_response.data:
            return jsonify({'error': 'Studio not found'}), 404
        
        # Update phone reveal stats
        try:
            # Check if stats exist
            stats_response = supabase.table('studio_stats') \
                .select('*') \
                .eq('studio_id', studio_id) \
                .execute()
            
            current_time = datetime.utcnow().isoformat()
            
            if stats_response.data and len(stats_response.data) > 0:
                # Update existing stats
                supabase.table('studio_stats') \
                    .update({
                        'phone_reveals': stats_response.data[0]['phone_reveals'] + 1,
                        'last_viewed_at': current_time
                    }) \
                    .eq('studio_id', studio_id) \
                    .execute()
                print(f"Updated phone reveals for studio {studio_id}")
            else:
                # Create new stats
                supabase.table('studio_stats') \
                    .insert({
                        'studio_id': studio_id,
                        'views': 0,
                        'phone_reveals': 1,
                        'last_viewed_at': current_time
                    }) \
                    .execute()
                print(f"Created new stats for studio {studio_id}")
            
            return jsonify({
                'phone': studio_response.data['phone_number']
            })
        except Exception as e:
            print(f"Error updating phone reveal stats: {str(e)}")
            return jsonify({'error': 'Error updating stats'}), 500
    except Exception as e:
        print(f"Error in reveal_phone: {str(e)}")
        return jsonify({'error': 'Server error'}), 500
