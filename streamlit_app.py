import pandas as pd
import streamlit as st
import plotly.express as px
import folium
import json

# Load the data
us_data = pd.read_csv("data.csv")
ko_data = pd.read_csv("korea.csv")

# Create a 'Date' column for better plotting
us_data['Date'] = pd.to_datetime(us_data['Year'].astype(str) + '-' + us_data['Month'].astype(str), format='%Y-%m')

# Load the data
# Assuming your CSV file is structured like: Year, City, Value
df = pd.read_csv("korea.csv")  # Replace "your_data.csv"

# Load GeoJSON data
with open('ko.json', 'r', encoding='utf-8') as f:
    korea_regions = json.load(f)


# Streamlit app
st.title("Drug Trends")

page = st.sidebar.radio("Select a Page", ["US Drug Overdose Trend", "Korean Drug Violations Trend"])

# Page 1: US Drug Overdose Trend
if page == "US Drug Overdose Trend":
    st.title("US Drug Overdose Trend")

    # Create the Plotly line chart with smoothed lines
    fig = px.line(us_data, x='Date', y='Drug Overdose', color='Year', title='Drug Overdose Trend in the US', line_shape='spline')

    # Display the chart in Streamlit
    st.plotly_chart(fig)
    st.dataframe(us_data)
    st.write("Source : Data.gov")


# Page 2: Korean Drug Violations Trend
elif page == "Korean Drug Violations Trend":
    # Streamlit app
    st.title("Korean Drug Violations Trend")

    # Year slider
    selected_year = st.slider("Select Year", int(df['년도'].min()), int(df['년도'].max()), int(df['년도'].min()))

    # Crime category radio buttons
    crime_categories =  df['범죄분류'].unique().tolist()
    selected_crime = st.radio("Select Crime Category", crime_categories, horizontal=True) 
    # Use 'horizontal=True' for a horizontal layout

    # Filter data based on selected year and crime category
    filtered_df = df[(df['년도'] == selected_year) & (df['범죄분류'] == selected_crime)]

    # Filter data based on selected year
    filtered_df = filtered_df.melt(id_vars=['년도', '범죄분류'], 
                                var_name='City', 
                                value_name='Value')

    # Create the Folium map
    m = folium.Map(location=[36.34,127.77], zoom_start=6)

    threshold_scales = {
        '마약류 관리에 관한법률(대마)': [0, 100, 200, 300, 400, 500, 800],  # Example scale for crime_category_1
        '마약류 관리에 관한법률(마약)': [0, 100, 200, 300, 400, 500],   # Example scale for crime_category_2
        '마약류 관리에 관한법률(향정)': [0, 500, 1000, 1500, 2000],     # Example scale for crime_category_3
        '전체': [0, 500, 1000, 1500, 2000, 2600]   # Example scale for "Total"
    }

    # Add choropleth layer
    choropleth = folium.Choropleth(
        geo_data=korea_regions,
        name='Violations',
        data=filtered_df,
        columns=['City','Value'],  # Make sure these match your CSV
        key_on='properties.name',  # Adjust based on your GeoJSON
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Violations',
        threshold_scale=threshold_scales.get(selected_crime) 
    )

    choropleth.add_to(m)

    folium.LayerControl().add_to(m)
    tab1, tab2, tab3 = st.tabs(["Map", "Bar Chart", "Table"])

    with tab1:
        st.components.v1.html(m._repr_html_(), height=350)
    with tab2:
        fig_bar = px.bar(filtered_df, x='City', y='Value', 
                     title=f"{selected_crime} Violations in {selected_year}")
        st.plotly_chart(fig_bar)
    with tab3:
        st.dataframe(filtered_df)

    st.write("Source : Data.go.kr")
