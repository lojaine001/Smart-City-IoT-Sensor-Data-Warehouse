import psycopg2
from psycopg2 import sql

def create_connection():
    """Create database connection"""
    return psycopg2.connect(
        host="127.0.0.1",
        database="smart_city_dw",
        user="admin",
        password="admin123",
        port="5432"
    )

def setup_schema():
    """Create all dimension and fact tables"""
    conn = create_connection()
    cur = conn.cursor()
    
    # Drop existing tables
    print("Dropping existing tables if any...")
    tables = ['fact_readings', 'dim_sensor', 'dim_location', 'dim_time', 'dim_weather']
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
    
    # Create dimension tables
    print("Creating dimension tables...")
    
    # dim_time
    cur.execute("""
        CREATE TABLE dim_time (
            time_id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP UNIQUE NOT NULL,
            hour INTEGER,
            day INTEGER,
            month INTEGER,
            year INTEGER,
            day_of_week VARCHAR(10),
            is_rush_hour BOOLEAN,
            is_weekend BOOLEAN
        )
    """)
    
    # dim_location
    cur.execute("""
        CREATE TABLE dim_location (
            location_id SERIAL PRIMARY KEY,
            district VARCHAR(50) UNIQUE NOT NULL,
            zone_type VARCHAR(20),
            population_density VARCHAR(20)
        )
    """)
    
    # dim_sensor
    cur.execute("""
        CREATE TABLE dim_sensor (
            sensor_id SERIAL PRIMARY KEY,
            sensor_code VARCHAR(50) UNIQUE NOT NULL,
            sensor_type VARCHAR(30),
            location_id INTEGER REFERENCES dim_location(location_id),
            latitude DECIMAL(9,6),
            longitude DECIMAL(9,6),
            installation_date DATE
        )
    """)
    
    # dim_weather
    cur.execute("""
        CREATE TABLE dim_weather (
            weather_id SERIAL PRIMARY KEY,
            condition VARCHAR(20),
            temperature_range VARCHAR(20),
            humidity_range VARCHAR(20)
        )
    """)
    
    # fact_readings
    cur.execute("""
        CREATE TABLE fact_readings (
            reading_id SERIAL PRIMARY KEY,
            sensor_id INTEGER REFERENCES dim_sensor(sensor_id),
            time_id INTEGER REFERENCES dim_time(time_id),
            weather_id INTEGER REFERENCES dim_weather(weather_id),
            reading_value DECIMAL(10,2),
            anomaly_flag BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    print("Creating indexes...")
    cur.execute("CREATE INDEX idx_fact_sensor ON fact_readings(sensor_id)")
    cur.execute("CREATE INDEX idx_fact_time ON fact_readings(time_id)")
    cur.execute("CREATE INDEX idx_fact_weather ON fact_readings(weather_id)")
    cur.execute("CREATE INDEX idx_time_timestamp ON dim_time(timestamp)")
    
    conn.commit()
    cur.close()
    conn.close()
    print("✓ Database schema created successfully!")

if __name__ == "__main__":
    setup_schema()