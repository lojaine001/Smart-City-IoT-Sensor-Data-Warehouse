import psycopg2
import pandas as pd
from tabulate import tabulate

def create_connection():
    """Create database connection"""
    return psycopg2.connect(
        host="127.0.0.1",
        database="smart_city_dw",
        user="admin",
        password="admin123",
        port="5432"
    )

def run_query(query, description):
    """Execute query and display results"""
    print("\n" + "=" * 80)
    print(f"QUERY: {description}")
    print("=" * 80)
    
    conn = create_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
    print(f"\nRows returned: {len(df)}")
    
    return df

def analytics_dashboard():
    """Run comprehensive analytics queries"""
    
    print("\n" + "█" * 80)
    print("SMART CITY DATA WAREHOUSE - ANALYTICS DASHBOARD")
    print("█" * 80)
    
    # Query 1: Average readings by sensor type and district
    query1 = """
        SELECT 
            s.sensor_type,
            l.district,
            l.zone_type,
            COUNT(*) as total_readings,
            ROUND(AVG(f.reading_value), 2) as avg_reading,
            ROUND(MIN(f.reading_value), 2) as min_reading,
            ROUND(MAX(f.reading_value), 2) as max_reading
        FROM fact_readings f
        JOIN dim_sensor s ON f.sensor_id = s.sensor_id
        JOIN dim_location l ON s.location_id = l.location_id
        GROUP BY s.sensor_type, l.district, l.zone_type
        ORDER BY s.sensor_type, avg_reading DESC
    """
    run_query(query1, "Average Readings by Sensor Type and District")
    
    # Query 2: Rush hour analysis
    query2 = """
        SELECT 
            t.hour,
            t.is_rush_hour,
            s.sensor_type,
            COUNT(*) as reading_count,
            ROUND(AVG(f.reading_value), 2) as avg_value
        FROM fact_readings f
        JOIN dim_time t ON f.time_id = t.time_id
        JOIN dim_sensor s ON f.sensor_id = s.sensor_id
        WHERE s.sensor_type IN ('traffic', 'noise')
        GROUP BY t.hour, t.is_rush_hour, s.sensor_type
        ORDER BY t.hour, s.sensor_type
    """
    run_query(query2, "Traffic and Noise Patterns by Hour (Rush Hour Analysis)")
    
    # Query 3: Weather impact on air quality
    query3 = """
        SELECT 
            w.condition,
            w.temperature_range,
            COUNT(*) as reading_count,
            ROUND(AVG(f.reading_value), 2) as avg_air_quality,
            SUM(CASE WHEN f.anomaly_flag THEN 1 ELSE 0 END) as anomaly_count
        FROM fact_readings f
        JOIN dim_weather w ON f.weather_id = w.weather_id
        JOIN dim_sensor s ON f.sensor_id = s.sensor_id
        WHERE s.sensor_type = 'air_quality'
        GROUP BY w.condition, w.temperature_range
        ORDER BY avg_air_quality DESC
    """
    run_query(query3, "Weather Impact on Air Quality")
    
    # Query 4: Anomaly detection by zone
    query4 = """
        SELECT 
            l.district,
            l.zone_type,
            s.sensor_type,
            COUNT(*) as total_readings,
            SUM(CASE WHEN f.anomaly_flag THEN 1 ELSE 0 END) as anomalies,
            ROUND(100.0 * SUM(CASE WHEN f.anomaly_flag THEN 1 ELSE 0 END) / COUNT(*), 2) as anomaly_percentage
        FROM fact_readings f
        JOIN dim_sensor s ON f.sensor_id = s.sensor_id
        JOIN dim_location l ON s.location_id = l.location_id
        GROUP BY l.district, l.zone_type, s.sensor_type
        HAVING SUM(CASE WHEN f.anomaly_flag THEN 1 ELSE 0 END) > 0
        ORDER BY anomaly_percentage DESC
    """
    run_query(query4, "Anomaly Detection by Zone and Sensor Type")
    
    # Query 5: Weekend vs Weekday comparison
    query5 = """
        SELECT 
            s.sensor_type,
            t.is_weekend,
            CASE 
                WHEN t.is_weekend THEN 'Weekend'
                ELSE 'Weekday'
            END as day_type,
            COUNT(*) as reading_count,
            ROUND(AVG(f.reading_value), 2) as avg_reading
        FROM fact_readings f
        JOIN dim_sensor s ON f.sensor_id = s.sensor_id
        JOIN dim_time t ON f.time_id = t.time_id
        GROUP BY s.sensor_type, t.is_weekend
        ORDER BY s.sensor_type, t.is_weekend
    """
    run_query(query5, "Weekend vs Weekday Sensor Readings")
    
    # Query 6: Hourly trends for specific district
    query6 = """
        SELECT 
            t.hour,
            l.district,
            s.sensor_type,
            COUNT(*) as readings,
            ROUND(AVG(f.reading_value), 2) as avg_value
        FROM fact_readings f
        JOIN dim_time t ON f.time_id = t.time_id
        JOIN dim_sensor s ON f.sensor_id = s.sensor_id
        JOIN dim_location l ON s.location_id = l.location_id
        WHERE l.district = 'Downtown'
        GROUP BY t.hour, l.district, s.sensor_type
        ORDER BY t.hour, s.sensor_type
    """
    run_query(query6, "Hourly Trends for Downtown District")
    
    # Summary statistics
    query_summary = """
        SELECT 
            COUNT(DISTINCT s.sensor_id) as total_sensors,
            COUNT(DISTINCT l.location_id) as total_locations,
            COUNT(*) as total_readings,
            SUM(CASE WHEN f.anomaly_flag THEN 1 ELSE 0 END) as total_anomalies,
            ROUND(100.0 * SUM(CASE WHEN f.anomaly_flag THEN 1 ELSE 0 END) / COUNT(*), 2) as anomaly_rate
        FROM fact_readings f
        JOIN dim_sensor s ON f.sensor_id = s.sensor_id
        JOIN dim_location l ON s.location_id = l.location_id
    """
    run_query(query_summary, "Data Warehouse Summary Statistics")
    
    print("\n" + "█" * 80)
    print("ANALYTICS COMPLETE")
    print("█" * 80 + "\n")

if __name__ == "__main__":
    analytics_dashboard()