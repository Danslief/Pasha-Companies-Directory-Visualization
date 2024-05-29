import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np
import tkinter as tk
from tkinter import ttk

# Read data from the file
data = pd.read_csv('pasha_companies_directory.csv')  # Replace 'pasha_companies_directory.csv' with the actual file name

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

# Remove numbers, spaces, and special characters from city names
data['city'] = data['city'].apply(lambda x: re.sub(r'[\d\s\W]+', '', x))

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

# Function to display company information in a table when a bar is clicked
def on_bar_click(event):
    if event.inaxes == bar_chart:
        city_clicked = city_counts.index[int(round(event.xdata))]  # Round to the nearest integer
        companies_in_city = data[data['city'] == city_clicked]

        # Create a new Tkinter window
        root = tk.Tk()
        root.title(f"Companies in {city_clicked}")

        # Create a table to display company information
        tree = ttk.Treeview(root, columns=('Name', 'Location', 'Phone', 'Email'), show='headings')
        tree.heading('#1', text='Name')
        tree.heading('#2', text='Location')
        tree.heading('#3', text='Phone')
        tree.heading('#4', text='Email')


        # Insert company information into the table
        for index, row in companies_in_city.iterrows():
            tree.insert('', 'end', values=(row['name'], row['location'], row['phone'], row['email']))

        tree.pack(expand=tk.YES, fill=tk.BOTH)

        root.mainloop()

# Connect the event handler function to the bar chart
plt.gcf().canvas.mpl_connect('button_press_event', on_bar_click)

plt.show()
