-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist
DROP TABLE IF EXISTS studio_stats CASCADE;
DROP TABLE IF EXISTS studio_images CASCADE;
DROP TABLE IF EXISTS studios CASCADE;

-- Create studios table
CREATE TABLE studios (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    phone_number VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create studio_images table to store image references
CREATE TABLE studio_images (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    studio_id UUID REFERENCES studios(id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create studio_stats table for analytics
CREATE TABLE studio_stats (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    studio_id UUID REFERENCES studios(id) ON DELETE CASCADE,
    views INTEGER DEFAULT 0,
    phone_reveals INTEGER DEFAULT 0,
    last_viewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updating updated_at
CREATE TRIGGER update_studios_updated_at
    BEFORE UPDATE ON studios
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

CREATE TRIGGER update_studio_stats_updated_at
    BEFORE UPDATE ON studio_stats
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_studios_name ON studios(name);
CREATE INDEX IF NOT EXISTS idx_studio_images_studio_id ON studio_images(studio_id);
CREATE INDEX IF NOT EXISTS idx_studio_stats_studio_id ON studio_stats(studio_id);

-- Enable Row Level Security (RLS)
ALTER TABLE studios ENABLE ROW LEVEL SECURITY;
ALTER TABLE studio_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE studio_stats ENABLE ROW LEVEL SECURITY;

-- Create policies for public access
CREATE POLICY studios_policy ON studios FOR ALL USING (true);
CREATE POLICY studio_images_policy ON studio_images FOR ALL USING (true);
CREATE POLICY studio_stats_policy ON studio_stats FOR ALL USING (true);
