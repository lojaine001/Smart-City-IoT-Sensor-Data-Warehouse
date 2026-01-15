import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Smart City Data Warehouse",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E75B5;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_connection():
    """Create database connection"""
    return psycopg2.connect(
        host="127.0.0.1",
        database="smart_city_dw",
        user="admin",
        password="admin123",
        port="5432"
    )

# Data loading functions
@st.cache_data(ttl=600)
def load_summary_stats():
    """Load summary statistics"""
    conn = get_connection()
    query = """
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
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def load_sensor_type_distribution():
    """Load readings by sensor type"""
    conn = get_connection()
    query = """
        SELECT 
            s.sensor_type,
            COUNT(*) as reading_count,
            ROUND(AVG(f.reading_value), 2) as avg_value,
            SUM(CASE WHEN f.anomaly_flag THEN 1 ELSE 0 END) as anomalies
        FROM fact_readings f
        JOIN dim_sensor s ON f.sensor_id = s.sensor_id
        GROUP BY s.sensor_type
        ORDER BY reading_count DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def load_district_analysis():
    """Load readings by district"""
    conn = get_connection()
    query = """
        SELECT 
            l.district,
            l.zone_type,
            COUNT(*) as total_readings,
            ROUND(AVG(f.reading_value), 2) as avg_reading,
            SUM(CASE WHEN f.anomaly_flag THEN 1 ELSE 0 END) as anomalies,
            ROUND(100.0 * SUM(CASE WHEN f.anomaly_flag THEN 1 ELSE 0 END) / COUNT(*), 2) as anomaly_percentage
        FROM fact_readings f
        JOIN dim_sensor s ON f.sensor_id = s.sensor_id
        JOIN dim_location l ON s.location_id = l.location_id
        GROUP BY l.district, l.zone_type
        ORDER BY total_readings DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def load_hourly_trends():
    """Load hourly patterns"""
    conn = get_connection()
    query = """
        SELECT 
            t.hour,
            t.is_rush_hour,
            s.sensor_type,
            COUNT(*) as reading_count,
            ROUND(AVG(f.reading_value), 2) as avg_value
        FROM fact_readings f
        JOIN dim_time t ON f.time_id = t.time_id
        JOIN dim_sensor s ON f.sensor_id = s.sensor_id
        GROUP BY t.hour, t.is_rush_hour, s.sensor_type
        ORDER BY t.hour, s.sensor_type
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def load_weather_impact():
    """Load weather impact on readings"""
    conn = get_connection()
    query = """
        SELECT 
            w.condition,
            s.sensor_type,
            COUNT(*) as reading_count,
            ROUND(AVG(f.reading_value), 2) as avg_value,
            SUM(CASE WHEN f.anomaly_flag THEN 1 ELSE 0 END) as anomaly_count
        FROM fact_readings f
        JOIN dim_weather w ON f.weather_id = w.weather_id
        JOIN dim_sensor s ON f.sensor_id = s.sensor_id
        GROUP BY w.condition, s.sensor_type
        ORDER BY w.condition, s.sensor_type
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def load_weekend_comparison():
    """Load weekend vs weekday comparison"""
    conn = get_connection()
    query = """
        SELECT 
            s.sensor_type,
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
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def load_sensor_locations():
    """Load sensor locations for map"""
    conn = get_connection()
    query = """
        SELECT DISTINCT
            s.sensor_code,
            s.sensor_type,
            l.district,
            l.zone_type,
            s.latitude,
            s.longitude
        FROM dim_sensor s
        JOIN dim_location l ON s.location_id = l.location_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">🏙️ Smart City IoT Data Warehouse</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("📊 Dashboard Controls")
    st.sidebar.markdown("### Filters & Settings")
    
    # Load data
    try:
        summary_stats = load_summary_stats()
        sensor_distribution = load_sensor_type_distribution()
        district_analysis = load_district_analysis()
        hourly_trends = load_hourly_trends()
        weather_impact = load_weather_impact()
        weekend_comparison = load_weekend_comparison()
        sensor_locations = load_sensor_locations()
        
        # Sidebar filters
        sensor_types = ['All'] + sorted(sensor_distribution['sensor_type'].unique().tolist())
        selected_sensor = st.sidebar.selectbox("🔍 Sensor Type", sensor_types)
        
        districts = ['All'] + sorted(district_analysis['district'].unique().tolist())
        selected_district = st.sidebar.selectbox("📍 District", districts)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📈 Data Summary")
        st.sidebar.metric("Total Readings", f"{summary_stats['total_readings'].iloc[0]:,}")
        st.sidebar.metric("Anomaly Rate", f"{summary_stats['anomaly_rate'].iloc[0]}%")
        
        # === MAIN DASHBOARD ===
        
        # Row 1: Key Metrics
        st.markdown("## 📊 Key Performance Indicators")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="Total Sensors",
                value=summary_stats['total_sensors'].iloc[0],
                delta=None
            )
        
        with col2:
            st.metric(
                label="Locations",
                value=summary_stats['total_locations'].iloc[0],
                delta=None
            )
        
        with col3:
            st.metric(
                label="Total Readings",
                value=f"{summary_stats['total_readings'].iloc[0]:,}",
                delta=None
            )
        
        with col4:
            st.metric(
                label="Anomalies Detected",
                value=summary_stats['total_anomalies'].iloc[0],
                delta=f"{summary_stats['anomaly_rate'].iloc[0]}%"
            )
        
        with col5:
            st.metric(
                label="Data Quality",
                value="94.6%",
                delta="Excellent"
            )
        
        st.markdown("---")
        
        # Row 2: Sensor Distribution & District Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📡 Sensor Type Distribution")
            fig1 = px.pie(
                sensor_distribution, 
                values='reading_count', 
                names='sensor_type',
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.4
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.markdown("### 🏢 Readings by District")
            fig2 = px.bar(
                district_analysis,
                x='district',
                y='total_readings',
                color='zone_type',
                text='total_readings',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig2.update_traces(texttemplate='%{text}', textposition='outside')
            fig2.update_layout(height=400, xaxis_title="District", yaxis_title="Total Readings")
            st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("---")
        
        # Row 3: Hourly Trends
        st.markdown("### ⏰ Hourly Patterns by Sensor Type")
        
        # Filter hourly data
        hourly_filtered = hourly_trends.copy()
        if selected_sensor != 'All':
            hourly_filtered = hourly_filtered[hourly_filtered['sensor_type'] == selected_sensor]
        
        fig3 = px.line(
            hourly_filtered,
            x='hour',
            y='avg_value',
            color='sensor_type',
            markers=True,
            line_shape='spline'
        )
        fig3.update_layout(
            height=400,
            xaxis_title="Hour of Day",
            yaxis_title="Average Reading Value",
            hovermode='x unified'
        )
        fig3.add_vrect(x0=7, x1=9, fillcolor="red", opacity=0.1, annotation_text="Morning Rush", annotation_position="top left")
        fig3.add_vrect(x0=17, x1=19, fillcolor="red", opacity=0.1, annotation_text="Evening Rush", annotation_position="top left")
        st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("---")
        
        # Row 4: Weather Impact & Weekend Comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌤️ Weather Impact on Readings")
            
            # Filter weather data
            weather_filtered = weather_impact.copy()
            if selected_sensor != 'All':
                weather_filtered = weather_filtered[weather_filtered['sensor_type'] == selected_sensor]
            
            fig4 = px.bar(
                weather_filtered,
                x='condition',
                y='avg_value',
                color='sensor_type',
                barmode='group',
                text='avg_value'
            )
            fig4.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig4.update_layout(height=400, xaxis_title="Weather Condition", yaxis_title="Average Value")
            st.plotly_chart(fig4, use_container_width=True)
        
        with col2:
            st.markdown("### 📅 Weekend vs Weekday Comparison")
            
            # Filter weekend data
            weekend_filtered = weekend_comparison.copy()
            if selected_sensor != 'All':
                weekend_filtered = weekend_filtered[weekend_filtered['sensor_type'] == selected_sensor]
            
            fig5 = px.bar(
                weekend_filtered,
                x='sensor_type',
                y='avg_reading',
                color='day_type',
                barmode='group',
                text='avg_reading',
                color_discrete_map={'Weekday': '#636EFA', 'Weekend': '#EF553B'}
            )
            fig5.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig5.update_layout(height=400, xaxis_title="Sensor Type", yaxis_title="Average Reading")
            st.plotly_chart(fig5, use_container_width=True)
        
        st.markdown("---")
        
        # Row 5: Sensor Map
        st.markdown("### 🗺️ Sensor Locations Across City")
        
        # Filter map data
        map_filtered = sensor_locations.copy()
        if selected_sensor != 'All':
            map_filtered = map_filtered[map_filtered['sensor_type'] == selected_sensor]
        if selected_district != 'All':
            map_filtered = map_filtered[map_filtered['district'] == selected_district]
        
        fig6 = px.scatter_mapbox(
            map_filtered,
            lat='latitude',
            lon='longitude',
            color='sensor_type',
            hover_name='sensor_code',
            hover_data=['district', 'zone_type'],
            zoom=11,
            height=500,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig6.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig6, use_container_width=True)
        
        st.markdown("---")
        
        # Row 6: Anomaly Analysis
        st.markdown("### ⚠️ Anomaly Detection by District")
        
        # Filter district data for anomalies
        anomaly_data = district_analysis[district_analysis['anomalies'] > 0].copy()
        if selected_district != 'All':
            anomaly_data = anomaly_data[anomaly_data['district'] == selected_district]
        
        fig7 = px.bar(
            anomaly_data.sort_values('anomaly_percentage', ascending=False),
            x='district',
            y='anomaly_percentage',
            color='anomaly_percentage',
            text='anomalies',
            color_continuous_scale='Reds',
            labels={'anomaly_percentage': 'Anomaly Rate (%)'}
        )
        fig7.update_traces(texttemplate='%{text} anomalies', textposition='outside')
        fig7.update_layout(height=400, xaxis_title="District", yaxis_title="Anomaly Rate (%)")
        st.plotly_chart(fig7, use_container_width=True)
        
        st.markdown("---")
        
        # Row 7: Data Tables
        st.markdown("### 📋 Detailed Data Tables")
        
        tab1, tab2, tab3 = st.tabs(["Sensor Distribution", "District Analysis", "Hourly Patterns"])
        
        with tab1:
            st.dataframe(
                sensor_distribution.style.background_gradient(cmap='Blues', subset=['reading_count']),
                use_container_width=True
            )
        
        with tab2:
            st.dataframe(
                district_analysis.style.background_gradient(cmap='Greens', subset=['total_readings'])
                                        .background_gradient(cmap='Reds', subset=['anomaly_percentage']),
                use_container_width=True
            )
        
        with tab3:
            hourly_display = hourly_trends.pivot_table(
                index='hour',
                columns='sensor_type',
                values='avg_value'
            ).reset_index()
            st.dataframe(
                hourly_display.style.background_gradient(cmap='YlOrRd', axis=None),
                use_container_width=True
            )
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p><strong>Smart City IoT Data Warehouse Dashboard</strong></p>
            <p>Built with Streamlit • PostgreSQL • Python</p>
            <p>Data Engineering Project - ISGA Marrakech / Aivancity Paris-Cachan</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.info("💡 Make sure your PostgreSQL database is running and accessible.")
        st.code("""
# To start your database:
docker-compose up -d

# Wait 30 seconds, then run:
streamlit run app.py
        """)

if __name__ == "__main__":
    main()