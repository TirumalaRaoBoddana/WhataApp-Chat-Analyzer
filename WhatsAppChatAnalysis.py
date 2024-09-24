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

st.sidebar.image("https://cdn-icons-png.freepik.com/256/9873/9873735.png?ga=GA1.1.46124664.1726593421&semt=ais_hybrid", width=230)
font_awesome = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
"""
st.markdown(font_awesome, unsafe_allow_html=True)
st.sidebar.markdown("<h1><i class='fas fa-chart-line' style='color:blue'></i> WhatsApp Chat Analyzer</h1>", unsafe_allow_html=True)
option = st.sidebar.radio("Select an option: ", ["Normal chat", "Group chat"])

def detect_chat_type(file):
    pattern = r"^(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}\s[ap]m) - ([^:]+): (.*)"
    persons = set()
    
    # Read the file again for detecting chat type
    file.seek(0)
    chat = file.readlines()
    
    for line in chat:
        try:
            decoded_line = line.decode("utf-8")
            match = re.match(pattern, decoded_line)
            if match:
                persons.add(match.group(3))
        except Exception as e:
            st.error(f"Error decoding line: {e}")
    
    if len(persons) > 2:
        return "Group Chat"
    else:
        return "Normal Chat"

file = st.sidebar.file_uploader("Upload file", type="txt")
if file:
    chat_type = detect_chat_type(file)
    file.seek(0)  # Reset file pointer for analysis
    if option == "Normal chat":
        if chat_type == "Normal Chat":
            normal_chat.analyze_normal_chat(file)
        else:
            st.warning("Upload correct file for Normal Chat.")
    elif option == "Group chat":
        if chat_type == "Group Chat":
            group_chat.analyze_group_chat(file)
        else:
            st.warning("Upload correct file for Group Chat.")
else:
    st.title("WhatsApp chat analyzer")
    st.markdown("""<p>The WhatsApp Chat Analyzer is a web application designed to help users analyze and visualize their WhatsApp chat data. 
                It processes chat logs from exported text files,
                 extracting key metrics and insights about conversations.
                The WhatsApp Chat Analyzer serves as a tool for users who want to gain insights into their messaging habits,
                 understand relationship dynamics, and explore their communication patterns in a visual format.
                 Whether for personal reflection, academic research, or social analysis, it offers a comprehensive look at chat interactions.
                </p>""",unsafe_allow_html=True)
    st.markdown("""
    ### Note on WhatsApp Chat Analyzer

    The **WhatsApp Chat Analyzer** is designed to provide insights into your messaging patterns and communication dynamics. Here are some key points to keep in mind:

    - **Data Privacy**: Your chat data is processed locally and not stored anywhere. Ensure you are comfortable sharing the chat data you upload.
    - **File Format**: Please upload a valid WhatsApp chat export file in `.txt` format for accurate analysis.
    - **Limitations**: The analysis relies on the formatting of the exported chat. Ensure the chat is in the standard format for the best results.
    - **Visualization**: Explore various visualizations to gain deeper insights into your conversations, including daily activity, media shared, and user engagement.
    
    If you encounter any issues or have questions, feel free to reach out for assistance!
""")
    st.info("Export chat without the media")
    