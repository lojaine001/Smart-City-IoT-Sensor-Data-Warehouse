# Smart City IoT Sensor Data Warehouse

A complete data warehouse project demonstrating ETL processes, star schema design, and analytics on IoT sensor data from a smart city.

## Architecture

**Star Schema:**
- **Fact Table:** fact_readings (sensor measurements)
- **Dimension Tables:** 
  - dim_sensor (sensor details)
  - dim_location (geographical zones)
  - dim_time (temporal data)
  - dim_weather (weather conditions)

## Setup & Execution Guide

### Prerequisites
- Docker installed
- Python 3.8+
- pip

### Step-by-Step Execution

#### Step 1: Install Dependencies (5 min)
```bash
pip install -r requirements.txt
```

#### Step 2: Start PostgreSQL (2 min)
```bash
docker-compose up -d
```

Wait 30 seconds for PostgreSQL to initialize.

#### Step 3: Create Database Schema (1 min)
```bash
python setup_database.py
```

#### Step 4: Generate Sample Data (2 min)
```bash
python generate_sensor_data.py
```

This creates 5 CSV files with:
- 8 locations
- 50 sensors
- 5 weather conditions
- 720+ time entries (30 days hourly)
- 5000 raw sensor readings

#### Step 5: Run ETL Pipeline (3 min)
```bash
python etl_pipeline.py
```

ETL Process:
1. Loads dimension tables
2. Cleans raw data (removes nulls, duplicates)
3. Detects anomalies
4. Loads fact table with foreign key relationships

#### Step 6: Run Analytics (1 min)
```bash
python analytics_queries.py
```

## Total Time: ~15 minutes

## Analytics Queries Included

1. Average readings by sensor type and district
2. Rush hour traffic and noise analysis
3. Weather impact on air quality
4. Anomaly detection by zone
5. Weekend vs weekday comparison
6. Hourly trends for specific districts
7. Summary statistics

## Cleanup

```bash
docker-compose down -v
rm *.csv
```

## Technologies Used
- **Database:** PostgreSQL
- **ETL:** Python, pandas
- **Orchestration:** Docker
- **Data Generation:** Faker

## Project Highlights
- Star schema design
- Surrogate keys
- ETL pipeline with data quality checks
- Anomaly detection
- Comprehensive analytics queries
- Indexing for performance

## Quick Start (All Commands)

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL
docker-compose up -d
sleep 30

# Run the project
python setup_database.py
python generate_sensor_data.py
python etl_pipeline.py
python analytics_queries.py
```

## Project Structure

```
smart-city-dw/
├── docker-compose.yml          # PostgreSQL container setup
├── requirements.txt            # Python dependencies
├── setup_database.py          # Creates database schema
├── generate_sensor_data.py    # Generates sample data
├── etl_pipeline.py            # ETL process
├── analytics_queries.py       # Analytics dashboard
└── README.md                  # This file
```

## Database Schema

### Dimension Tables

**dim_location**
- location_id (PK)
- district
- zone_type
- population_density

**dim_sensor**
- sensor_id (PK)
- sensor_code
- sensor_type
- location_id (FK)
- latitude
- longitude
- installation_date

**dim_time**
- time_id (PK)
- timestamp
- hour
- day
- month
- year
- day_of_week
- is_rush_hour
- is_weekend

**dim_weather**
- weather_id (PK)
- condition
- temperature_range
- humidity_range

### Fact Table

**fact_readings**
- reading_id (PK)
- sensor_id (FK)
- time_id (FK)
- weather_id (FK)
- reading_value
- anomaly_flag
- created_at


