import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import re
from tkinter import ttk

# Read data from the file
data = pd.read_csv('pasha_companies_directory.csv')  # Replace with the actual file name

# Function to extract city names from the location column
def extract_city(location):
    if isinstance(location, str):  # Check if location is a string
        parts = location.split(',')
        if len(parts) >= 2:
            city = parts[-3].strip()  # Adjusted index to extract city name
            return city
    return None  # Return None for non-string or invalid locations

# Apply the function to extract city names and create a new column
data['city'] = data['location'].apply(extract_city)

# Drop rows with missing city values
data.dropna(subset=['city'], inplace=True)
data['city'] = data['city'].apply(lambda x: re.sub(r'[\d\s\W]+', '', x))
# Preprocess city names to remove single quotation marks
data['city'] = data['city'].str.replace("'", "")

# Read world cities data
world_cities = pd.read_csv('worldcities.csv')

# Merge data with world cities based on city names
merged_data = pd.merge(data, world_cities, left_on='city', right_on='city_ascii', how='left')

# Extract latitude and longitude columns
latitude = merged_data['lat']
longitude = merged_data['lng']

# Create a dashboard using Tkinter
root = tk.Tk()
root.title("Company Directory Dashboard")

# Frame to display the visualizations
visualization_frame = tk.Frame(root)
visualization_frame.pack()

# Function to display bar chart of companies by city
def display_city_bar_chart():
    # Count the number of companies in each city
    city_counts = data['city'].value_counts()

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    bar_chart = city_counts.plot(kind='bar')
    plt.title('Number of Companies in Different Cities')
    plt.xlabel('City')
    plt.ylabel('Number of Companies')
    plt.yticks(range(0, max(city_counts)+1, 50))  # Set y-axis ticks with increments of 50
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
    plt.tight_layout()

    # Embed the bar chart into the visualization frame
    canvas = FigureCanvasTkAgg(bar_chart.figure, master=visualization_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Function to display a table of companies in a selected city
def display_city_company_table(city):
    # Filter data for the selected city
    city_data = data[data['city'] == city]

    # Create a new window for displaying company information
    company_window = tk.Toplevel(root)
    company_window.title(f"Companies in {city}")

    # Create a treeview widget for displaying company information
    tree = ttk.Treeview(company_window)
    tree["columns"] = tuple(city_data.columns)

    # Set column headings
    for col in city_data.columns:
        tree.heading(col, text=col)

    # Insert company data into the treeview
    for index, row in city_data.iterrows():
        tree.insert("", "end", values=tuple(row))

    tree.pack()

# Display bar chart
display_city_bar_chart()

# Dropdown menu to select a city
selected_city = tk.StringVar()
city_dropdown = ttk.Combobox(root, textvariable=selected_city, values=data['city'].unique())
city_dropdown.pack()

# Button to display company table for selected city
company_table_button = tk.Button(root, text="Display Company Table", command=lambda: display_city_company_table(selected_city.get()))
company_table_button.pack()

root.mainloop()