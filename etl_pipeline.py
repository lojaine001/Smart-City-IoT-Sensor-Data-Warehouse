import pandas as pd
import psycopg2
from datetime import datetime
import numpy as np

def create_connection():
    """Create database connection"""
    return psycopg2.connect(
        host="127.0.0.1",
        database="smart_city_dw",
        user="admin",
        password="admin123",
        port="5432"
    )

def load_dimensions():
    """Load dimension tables"""
    conn = create_connection()
    cur = conn.cursor()
    
    print("\n=== LOADING DIMENSIONS ===")
    
    # Load locations
    print("Loading locations...")
    locations_df = pd.read_csv('locations.csv')
    for _, row in locations_df.iterrows():
        cur.execute("""
            INSERT INTO dim_location (district, zone_type, population_density)
            VALUES (%s, %s, %s)
            ON CONFLICT (district) DO NOTHING
        """, (row['district'], row['zone_type'], row['population_density']))
    print(f"✓ Loaded {len(locations_df)} locations")
    
    # Load weather conditions
    print("Loading weather conditions...")
    weather_df = pd.read_csv('weather.csv')
    for _, row in weather_df.iterrows():
        cur.execute("""
            INSERT INTO dim_weather (condition, temperature_range, humidity_range)
            VALUES (%s, %s, %s)
        """, (row['condition'], row['temperature_range'], row['humidity_range']))
    print(f"✓ Loaded {len(weather_df)} weather conditions")
    
    # Load sensors
    print("Loading sensors...")
    sensors_df = pd.read_csv('sensors.csv')
    for _, row in sensors_df.iterrows():
        # Get location_id
        cur.execute("SELECT location_id FROM dim_location WHERE district = %s", (row['district'],))
        location_id = cur.fetchone()[0]
        
        cur.execute("""
            INSERT INTO dim_sensor (sensor_code, sensor_type, location_id, latitude, longitude, installation_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (sensor_code) DO NOTHING
        """, (row['sensor_code'], row['sensor_type'], location_id, 
              row['latitude'], row['longitude'], row['installation_date']))
    print(f"✓ Loaded {len(sensors_df)} sensors")
    
    # Load time dimension
    print("Loading time dimension...")
    time_df = pd.read_csv('time_dimension.csv')
    time_df['timestamp'] = pd.to_datetime(time_df['timestamp'])
    
    for _, row in time_df.iterrows():
        cur.execute("""
            INSERT INTO dim_time (timestamp, hour, day, month, year, day_of_week, is_rush_hour, is_weekend)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (timestamp) DO NOTHING
        """, (row['timestamp'], row['hour'], row['day'], row['month'], 
              row['year'], row['day_of_week'], row['is_rush_hour'], row['is_weekend']))
    print(f"✓ Loaded {len(time_df)} time entries")
    
    conn.commit()
    cur.close()
    conn.close()

def clean_and_transform_readings():
    """ETL: Extract, Clean, and Transform sensor readings"""
    print("\n=== ETL PROCESS ===")
    
    # Extract
    print("Extracting raw readings...")
    readings_df = pd.read_csv('raw_readings.csv')
    print(f"Extracted {len(readings_df)} raw readings")
    
    # Transform
    print("Cleaning data...")
    
    # Remove duplicates
    initial_count = len(readings_df)
    readings_df = readings_df.drop_duplicates()
    print(f"  - Removed {initial_count - len(readings_df)} duplicates")
    
    # Handle missing values
    missing_count = readings_df['reading_value'].isna().sum()
    readings_df = readings_df.dropna(subset=['reading_value'])
    print(f"  - Removed {missing_count} missing values")
    
    # Detect anomalies (values beyond 3 standard deviations)
    mean_val = readings_df['reading_value'].mean()
    std_val = readings_df['reading_value'].std()
    readings_df['anomaly_flag'] = (
        (readings_df['reading_value'] > mean_val + 3*std_val) |
        (readings_df['reading_value'] < mean_val - 3*std_val)
    )
    anomaly_count = readings_df['anomaly_flag'].sum()
    print(f"  - Detected {anomaly_count} anomalies")
    
    # Convert timestamp
    readings_df['timestamp'] = pd.to_datetime(readings_df['timestamp'])
    
    print(f"✓ Cleaned data ready: {len(readings_df)} readings")
    
    return readings_df

def load_fact_table(readings_df):
    """Load fact table with foreign key lookups"""
    conn = create_connection()
    cur = conn.cursor()
    
    print("\n=== LOADING FACT TABLE ===")
    
    loaded_count = 0
    skipped_count = 0
    
    for _, row in readings_df.iterrows():
        try:
            # Get sensor_id
            cur.execute("SELECT sensor_id FROM dim_sensor WHERE sensor_code = %s", 
                       (row['sensor_code'],))
            sensor_result = cur.fetchone()
            if not sensor_result:
                skipped_count += 1
                continue
            sensor_id = sensor_result[0]
            
            # Get time_id
            cur.execute("SELECT time_id FROM dim_time WHERE timestamp = %s", 
                       (row['timestamp'],))
            time_result = cur.fetchone()
            if not time_result:
                skipped_count += 1
                continue
            time_id = time_result[0]
            
            # Get weather_id
            cur.execute("SELECT weather_id FROM dim_weather WHERE condition = %s", 
                       (row['weather_condition'],))
            weather_result = cur.fetchone()
            if not weather_result:
                skipped_count += 1
                continue
            weather_id = weather_result[0]
            
            # Insert fact
            cur.execute("""
                INSERT INTO fact_readings (sensor_id, time_id, weather_id, reading_value, anomaly_flag)
                VALUES (%s, %s, %s, %s, %s)
            """, (sensor_id, time_id, weather_id, row['reading_value'], row['anomaly_flag']))
            
            loaded_count += 1
            
            if loaded_count % 1000 == 0:
                print(f"  Loaded {loaded_count} readings...")
                conn.commit()
                
        except Exception as e:
            print(f"Error loading reading: {e}")
            skipped_count += 1
            continue
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"✓ Loaded {loaded_count} readings into fact table")
    print(f"  Skipped {skipped_count} readings (missing references)")

def run_etl():
    """Run complete ETL pipeline"""
    print("=" * 50)
    print("SMART CITY DATA WAREHOUSE - ETL PIPELINE")
    print("=" * 50)
    
    start_time = datetime.now()
    
    # Step 1: Load dimensions
    load_dimensions()
    
    # Step 2: Clean and transform readings
    cleaned_readings = clean_and_transform_readings()
    
    # Step 3: Load fact table
    load_fact_table(cleaned_readings)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 50)
    print(f"✓ ETL COMPLETED in {duration:.2f} seconds")
    print("=" * 50)

if __name__ == "__main__":
    run_etl()