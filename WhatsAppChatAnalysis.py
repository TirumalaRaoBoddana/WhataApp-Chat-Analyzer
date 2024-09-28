import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
from datetime import datetime
from wordcloud import WordCloud
import normal_chat
import group_chat
from dateutil import parser
# Sidebar image and title
st.sidebar.image("https://cdn-icons-png.freepik.com/256/9873/9873735.png?ga=GA1.1.46124664.1726593421&semt=ais_hybrid", width=230)
font_awesome = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
"""
st.markdown(font_awesome, unsafe_allow_html=True)
st.sidebar.markdown("<h1><i class='fas fa-chart-line' style='color:blue'></i> WhatsApp Chat Analyzer</h1>", unsafe_allow_html=True)
option = st.sidebar.radio("Select an option: ", ["Normal chat", "Group chat"])

# Function to detect the type of chat (normal or group)
def detect_chat_type(file, index):
    patterns = [
        # Day/Month/Year, 12-hour
        r"(?P<date>\d{1,2}/\d{1,2}/\d{4}), (?P<time>\d{1,2}:\d{2})\u202f?(?P<ampm>AM|PM|am|pm) - (?P<user>.*?): (?P<message>.*)",
        # Day/Month/Year, 24-hour
        r"(?P<date>\d{1,2}/\d{1,2}/\d{4}), (?P<time>\d{2}:\d{2}) - (?P<user>.*?): (?P<message>.*)",
        
        # Day/Month/Year, 24-hour, 2-digit year
        r"(?P<date>\d{1,2}/\d{1,2}/\d{2}), (?P<time>\d{2}:\d{2}) - (?P<user>.*?): (?P<message>.*)",
        
        # Day/Month/Year, 12-hour, 2-digit year
        r"(?P<date>\d{1,2}/\d{1,2}/\d{2}), (?P<time>\d{1,2}:\d{2})\u202f?(?P<ampm>AM|PM|am|pm) - (?P<user>.*?): (?P<message>.*)",

        # Month/Day/Year, 24-hour
        r"(?P<date>\d{1,2}/\d{1,2}/\d{4}), (?P<time>\d{2}:\d{2}) - (?P<user>.*?): (?P<message>.*)",
        
        # Month/Day/Year, 12-hour
        r"(?P<date>\d{1,2}/\d{1,2}/\d{4}), (?P<time>\d{1,2}:\d{2})\u202f?(?P<ampm>AM|PM|am|pm) - (?P<user>.*?): (?P<message>.*)",

        # Month/Day/Year, 24-hour, 2-digit year
        r"(?P<date>\d{1,2}/\d{1,2}/\d{2}), (?P<time>\d{2}:\d{2}) - (?P<user>.*?): (?P<message>.*)",
        
        # Month/Day/Year, 12-hour, 2-digit year
        r"(?P<date>\d{1,2}/\d{1,2}/\d{2}), (?P<time>\d{1,2}:\d{2})\u202f?(?P<ampm>AM|PM|am|pm) - (?P<user>.*?): (?P<message>.*)",

        # Year/Month/Day, 24-hour
        r"(?P<date>\d{4}/\d{1,2}/\d{1,2}), (?P<time>\d{2}:\d{2}) - (?P<user>.*?): (?P<message>.*)",
        
        # Year/Month/Day, 12-hour
        r"(?P<date>\d{4}/\d{1,2}/\d{1,2}), (?P<time>\d{1,2}:\d{2})\u202f?(?P<ampm>AM|PM|am|pm) - (?P<user>.*?): (?P<message>.*)",
        
        # Year/Month/Day, 24-hour, 2-digit year
        r"(?P<date>\d{2}/\d{1,2}/\d{2}), (?P<time>\d{2}:\d{2}) - (?P<user>.*?): (?P<message>.*)",
        
        # Year/Month/Day, 12-hour, 2-digit year
        r"(?P<date>\d{2}/\d{1,2}/\d{2}), (?P<time>\d{1,2}:\d{2})\u202f?(?P<ampm>AM|PM|am|pm) - (?P<user>.*?): (?P<message>.*)",

        # Day-Month-Year, 24-hour
        r"(?P<date>\d{1,2}-\d{1,2}-\d{4}), (?P<time>\d{2}:\d{2}) - (?P<user>.*?): (?P<message>.*)",

        # Day-Month-Year, 12-hour
        r"(?P<date>\d{1,2}-\d{1,2}-\d{4}), (?P<time>\d{1,2}:\d{2})\u202f?(?P<ampm>AM|PM|am|pm) - (?P<user>.*?): (?P<message>.*)",

        # Day-Month-Year, 24-hour, 2-digit year
        r"(?P<date>\d{1,2}-\d{1,2}-\d{2}), (?P<time>\d{2}:\d{2}) - (?P<user>.*?): (?P<message>.*)",

        # Day-Month-Year, 12-hour, 2-digit year
        r"(?P<date>\d{1,2}-\d{1,2}-\d{2}), (?P<time>\d{1,2}:\d{2})\u202f?(?P<ampm>AM|PM|am|pm) - (?P<user>.*?): (?P<message>.*)",

        # Month-Day-Year, 24-hour
        r"(?P<date>\d{1,2}-\d{1,2}-\d{4}), (?P<time>\d{2}:\d{2}) - (?P<user>.*?): (?P<message>.*)",

        # Month-Day-Year, 12-hour
        r"(?P<date>\d{1,2}-\d{1,2}-\d{4}), (?P<time>\d{1,2}:\d{2})\u202f?(?P<ampm>AM|PM|am|pm) - (?P<user>.*?): (?P<message>.*)",

        # Month-Day-Year, 24-hour, 2-digit year
        r"(?P<date>\d{1,2}-\d{1,2}-\d{2}), (?P<time>\d{2}:\d{2}) - (?P<user>.*?): (?P<message>.*)",

        # Month-Day-Year, 12-hour, 2-digit year
        r"(?P<date>\d{1,2}-\d{1,2}-\d{2}), (?P<time>\d{1,2}:\d{2})\u202f?(?P<ampm>AM|PM|am|pm) - (?P<user>.*?): (?P<message>.*)",
    ]
    # # Create a regex pattern based on various date and time formats
    pattern = patterns[index]                 # Match the message
    persons = set()
    # Read the file again to detect chat type
    file.seek(0)
    chat = file.readlines()
    for line in chat:
        try:
            decoded_line = line.decode("utf-8")
            match = re.match(pattern, decoded_line)
            if match:
                persons.add(match.group('user'))
        except Exception as e:
            st.error(f"Error decoding line: {e}")
    return "Group Chat" if len(persons) > 2 else "Normal Chat"

date_formats = [
    "Day/Month/Year,12-hour",
    "Day/Month/Year,24-hour",
    "Day/Month/Year,24-hour,2-digit year",
    "Day/Month/Year,12-hour,2-digit year",

    "Month/Day/Year,24-hour",
    "Month/Day/Year,12-hour",
    "Month/Day/Year,24-hour,2-digit year",
    "Month/Day/Year,12-hour,2-digit year",

    "Year/Month/Day,24-hour",
    "Year/Month/Day,12-hour",
    "Year/Month/Day,24-hour,2-digit year",
    "Year/Month/Day,12-hour,2-digit year",

    "Day-Month-Year,24-hour",
    "Day-Month-Year,12-hour",
    "Day-Month-Year,24-hour,2-digit year",
    "Day-Month-Year,12-hour,2-digit year",
    "Month-Day-Year,24-hour",
    "Month-Day-Year,12-hour",
    "Month-Day-Year,24-hour,2-digit year",
    "Month-Day-Year,12-hour,2-digit year"
]
# Streamlit select box
selected_format = st.sidebar.selectbox("Select a date format", date_formats)
# File uploader for chat log
file = st.sidebar.file_uploader("Upload file", type="txt")
if file:
    chat_type = detect_chat_type(file,date_formats.index(selected_format))
    file.seek(0)  # Reset file pointer for analysis
    if option == "Normal chat":
        if chat_type == "Normal Chat":
            normal_chat.analyze_normal_chat(file,date_formats.index(selected_format))
        else:
            st.warning("Upload a correct file for Normal Chat.")
    elif option == "Group chat":
        if chat_type == "Group Chat":
            group_chat.analyze_group_chat(file,date_formats.index(selected_format))
        else:
            st.warning("Upload a correct file for Group Chat.")
else:
    # Main application description
    st.title("WhatsApp Chat Analyzer")
    st.markdown("""<p>The WhatsApp Chat Analyzer is a web application designed to help users analyze and visualize their WhatsApp chat data. 
                It processes chat logs from exported text files,
                 extracting key metrics and insights about conversations.
                The WhatsApp Chat Analyzer serves as a tool for users who want to gain insights into their messaging habits,
                 understand relationship dynamics, and explore their communication patterns in a visual format.
                 Whether for personal reflection, academic research, or social analysis, it offers a comprehensive look at chat interactions.
                </p>""", unsafe_allow_html=True)
    
    st.markdown("""<p>The WhatsApp Chat Analyzer is designed to provide insights into your messaging patterns and communication dynamics. Here are some key points to keep in mind:</p>
    <ul>
        <li>Data Privacy: Your chat data is processed locally and not stored anywhere. Ensure you are comfortable sharing the chat data you upload.</li>
        <li>File Format: Please upload a valid WhatsApp chat export file in `.txt` format for accurate analysis.</li>
        <li>Limitations: The analysis relies on the formatting of the exported chat. Ensure the chat is in the standard format for the best results.</li>
        <li>Visualization: Explore various visualizations to gain deeper insights into your conversations, including daily activity, media shared, and user engagement.</li>
    </ul>
    <p>If you encounter any issues or have questions, feel free to reach out for assistance!</p>""", unsafe_allow_html=True)
    st.info("Export chat without the media.")
