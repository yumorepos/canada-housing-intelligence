
import folium
import pandas as pd

# Sample data (replace with your actual housing data)
data = {'city': ['Montreal', 'Toronto', 'Vancouver'],
        'province': ['Quebec', 'Ontario', 'British Columbia'],
        'price': [450000, 900000, 1200000],
        'affordability_index': [0.8, 0.5, 0.3],
        'trend': [0.05, 0.02, -0.01], # Example: 5% increase, 2% increase, 1% decrease
        'latitude': [45.5017, 43.6532, 49.2827],
        'longitude': [-73.5673, -79.3832, -123.1207]}
df = pd.DataFrame(data)

# Create the map
m = folium.Map(location=[56.1304, -106.3468], zoom_start=4)  # Canada centered

# Function to determine color based on affordability index
def color_producer(affordability_index):
    if affordability_index >= 0.7:
        return 'green'
    elif affordability_index >= 0.4:
        return 'orange'
    else:
        return 'red'

# Add markers for each city
for index, row in df.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color=color_producer(row['affordability_index']),
        fill=True,
        fill_color=color_producer(row['affordability_index']),
        popup=f"<b>{row['city']}, {row['province']}</b><br>"
              f"Price: ${row['price']:,}<br>"
              f"Affordability Index: {row['affordability_index']:.2f}<br>"
              f"Trend: {row['trend']:.2%}"
    ).add_to(m)

# Save the map to an HTML file
m.save("canada-housing-intelligence/map.html")
