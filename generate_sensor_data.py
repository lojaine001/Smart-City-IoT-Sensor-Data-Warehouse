import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker
import numpy as np

fake = Faker()

def generate_locations():
    """Generate location dimension data"""
    districts = [
        ('Downtown', 'Commercial', 'High'),
        ('Industrial Zone', 'Industrial', 'Medium'),
        ('North Residential', 'Residential', 'High'),
        ('South Residential', 'Residential', 'Medium'),
        ('West Park', 'Recreational', 'Low'),
        ('East Suburb', 'Residential', 'Low'),
        ('Tech District', 'Commercial', 'Medium'),
        ('Harbor Area', 'Industrial', 'Low')
    ]
    
    return pd.DataFrame(districts, columns=['district', 'zone_type', 'population_density'])

def generate_sensors(num_sensors=50):
    """Generate sensor dimension data"""
    sensor_types = ['temperature', 'air_quality', 'traffic', 'noise']
    
    sensors = []
    for i in range(num_sensors):
        sensor = {
            'sensor_code': f'SENSOR_{i+1:04d}',
            'sensor_type': random.choice(sensor_types),
            'district': random.choice(['Downtown', 'Industrial Zone', 'North Residential', 
                                      'South Residential', 'West Park', 'East Suburb',
                                      'Tech District', 'Harbor Area']),
            'latitude': round(random.uniform(33.5, 34.0), 6),
            'longitude': round(random.uniform(-7.7, -7.5), 6),
            'installation_date': fake.date_between(start_date='-2y', end_date='today')
        }
        sensors.append(sensor)
    
    return pd.DataFrame(sensors)

def generate_weather_conditions():
    """Generate weather dimension data"""
    conditions = [
        ('Sunny', 'Warm (20-30°C)', 'Low (30-50%)'),
        ('Cloudy', 'Mild (15-25°C)', 'Medium (50-70%)'),
        ('Rainy', 'Cool (10-20°C)', 'High (70-90%)'),
        ('Hot', 'Hot (30-40°C)', 'Low (20-40%)'),
        ('Cold', 'Cold (0-15°C)', 'Medium (40-60%)')
    ]
    
    return pd.DataFrame(conditions, columns=['condition', 'temperature_range', 'humidity_range'])

def generate_time_dimension(start_date, end_date):
    """Generate time dimension for date range"""
    # Round to nearest hour
    start_date = start_date.replace(minute=0, second=0, microsecond=0)
    end_date = end_date.replace(minute=0, second=0, microsecond=0)
    dates = pd.date_range(start=start_date, end=end_date, freq='H')
    
    time_data = []
    for dt in dates:
        time_entry = {
            'timestamp': dt,
            'hour': dt.hour,
            'day': dt.day,
            'month': dt.month,
            'year': dt.year,
            'day_of_week': dt.strftime('%A'),
            'is_rush_hour': dt.hour in [7, 8, 9, 17, 18, 19],
            'is_weekend': dt.weekday() >= 5
        }
        time_data.append(time_entry)
    
    return pd.DataFrame(time_data)

def generate_sensor_readings(num_readings=5000):
    """Generate raw sensor readings (simulating messy source data)"""
    sensor_types_ranges = {
        'temperature': (0, 45),
        'air_quality': (0, 500),  # AQI scale
        'traffic': (0, 100),  # vehicles per minute
        'noise': (30, 120)  # decibels
    }
    
    readings = []
    start_date = datetime.now() - timedelta(days=30)
    # Round to nearest hour to match time dimension
    start_date = start_date.replace(minute=0, second=0, microsecond=0)
    
    for _ in range(num_readings):
        sensor_code = f'SENSOR_{random.randint(1, 50):04d}'
        sensor_type = random.choice(list(sensor_types_ranges.keys()))
        min_val, max_val = sensor_types_ranges[sensor_type]
        
        # Generate reading with some noise and occasional nulls
        if random.random() < 0.05:  # 5% missing data
            value = None
        else:
            value = round(random.uniform(min_val, max_val), 2)
            
            # Add some outliers (anomalies)
            if random.random() < 0.03:  # 3% anomalies
                value = value * random.uniform(1.5, 3.0)
        
        # Generate timestamp aligned to exact hours
        hours_offset = random.randint(0, 720)
        reading = {
            'sensor_code': sensor_code,
            'timestamp': start_date + timedelta(hours=hours_offset),
            'reading_value': value,
            'weather_condition': random.choice(['Sunny', 'Cloudy', 'Rainy', 'Hot', 'Cold'])
        }
        readings.append(reading)
    
    return pd.DataFrame(readings)

if __name__ == "__main__":
    print("Generating data files...")
    
    # Generate all dimension data
    locations_df = generate_locations()
    sensors_df = generate_sensors(50)
    weather_df = generate_weather_conditions()
    time_df = generate_time_dimension(
        datetime.now() - timedelta(days=30),
        datetime.now()
    )
    readings_df = generate_sensor_readings(5000)
    
    # Save to CSV
    locations_df.to_csv('locations.csv', index=False)
    sensors_df.to_csv('sensors.csv', index=False)
    weather_df.to_csv('weather.csv', index=False)
    time_df.to_csv('time_dimension.csv', index=False)
    readings_df.to_csv('raw_readings.csv', index=False)
    
    print("✓ Data files generated successfully!")
    print(f"  - {len(locations_df)} locations")
    print(f"  - {len(sensors_df)} sensors")
    print(f"  - {len(weather_df)} weather conditions")
    print(f"  - {len(time_df)} time entries")
    print(f"  - {len(readings_df)} raw readings")