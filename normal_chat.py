import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
from datetime import datetime
from wordcloud import WordCloud
import emoji  

def extracting_columns(df):
    day=[]
    month=[]
    year=[]
    # creating date time object
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for i in list(df):
        date_obj = datetime.strptime(str(i), '%Y-%m-%d')
        day.append(weekday_names[date_obj.weekday()])
        month.append(date_obj.month)
        year.append(date_obj.year)
    return pd.DataFrame({
        "Day": day,
        "Month": month,
        "Year": year,
    })
def Create_df(file,index):
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
    chat_data = file.readlines() 
    dates, times, names, messages = [], [], [], []

    # Loop through each line in the chat data
    for line in chat_data:
        line = line.decode("utf-8").strip()  # Decode and strip any unwanted whitespace
        match = re.match(patterns[index], line)  # Match against the regex pattern
        if match:
            # Extract the date, time, name, and message
            date = match.group('date')
            time = match.group('time')
            name = match.group('user')
            message = match.group('message')
            # Append extracted data to respective lists
            dates.append(date)
            times.append(time)
            names.append(name)
            messages.append(message)
    
    # Create DataFrame from the lists
    df = pd.DataFrame({
        'Date': dates,
        'Time': times,
        'Name': names,
        'Message': messages
    })
    
    # Display the DataFrame for debugging
    # Convert Date and Time columns to appropriate formats
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df['Time'] = pd.to_datetime(df['Time']).dt.time
    # Extract day, month, year from the date column
    df = pd.concat([df, extracting_columns(df["Date"])], axis=1, ignore_index=True)
    df.columns = ["Date", "Time", "Name", "Message", "Day", "Month", "Year"]
    # Create Time Duration based on the time
    df["Time_duration"] = pd.to_datetime(df['Time'].astype(str)).dt.hour
    df['Time_duration'] = df['Time_duration'].apply(lambda x: f"{x}-{(x + 1) % 24}")  # Format as 'hour-hour+1'
    return df
def get_total_words(messages):
    count=0
    for msg in list(messages):
        count+=len(msg.split(" "))
    return count

def get_total_media(messages):
    return len(list(messages[messages=="<Media omitted>"]))
def get_total_links(messages):
    url_pattern = r'(https?://\S+)'
    # Find all occurrences of URLs in the chat
    links=[]
    for message in messages:
        links.extend(re.findall(url_pattern, message))
    return len(links)

def get_most_frequest_words(messages):
    messages=messages[messages!="<Media omitted>"]
    total_words=[]
    for i in list(messages):
        total_words+=i.split(" ")
    words=pd.Series(total_words)
    words=words[words!="(file"]
    words=words[words!="attached)"]
    return words.value_counts()[0:10]
def extract_emojis(messages):
    emoji_list = []
    for msg in messages:
        emoji_list.extend([char for char in msg if char in emoji.EMOJI_DATA])
    return pd.Series(emoji_list).value_counts()
def generate_wordcloud(messages):
    messages=messages[messages!="<Media omitted>"]
    all_messages = " ".join(messages)
    wordcloud = WordCloud(width=800, height=400, max_words=200, background_color='white').generate(all_messages)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off') 
    st.pyplot(fig)
def most_active_days(df):
    data=df.groupby("Date").count()["Message"].sort_values(ascending=False)[0:10]
    return data
def get_avg_msg_length(df):
    average_msg_len=dict()
    for i in df["Name"].unique():
        messages=df["Message"][df["Name"]==i]
        total_length=0
        for j in list(messages):
            total_length+=len(j)
        average_msg_len[i]=total_length/len(list(messages))
    return average_msg_len
def get_media_counts(df):
    media_counts=dict()
    for i in list(df["Name"]):
        media_counts[i]=df[(df["Message"]=="<Media omitted>") & (df["Name"]==i)].shape[0]
    return media_counts
def get_monthly_activity(df):
    df['Date'] = pd.to_datetime(df['Date'])
    # Extract the month and year from the 'Date' column
    df['MonthNum'] = df['Date'].dt.month
    monthly_activity = df.groupby(["Year", "MonthNum"]).count()["Message"]
    monthly_activity = monthly_activity.sort_index()
    x = [f"{i[1]:02d}-{i[0]}" for i in monthly_activity.index]  
    return monthly_activity,x
def analyze_normal_chat(file,index):
    df = Create_df(file,index)
    if(df.shape[0]==0):
        st.error("Select Appropreate date format of your whatsapp chat")
    else:
        df["Month"]=df["Month"].map({1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"})
        #top statistics
        st.header("Top Statistics")
        st.markdown("""
                    <div style="display:flex;flex-direction:column;justify-content:space-evenly;">
                        <div style="display:flex;flex-direction:row;align-items:center;justify-content:space-evenly">
                            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:25px;">
                                <div>
                                <i class='fas fa-comments'></i>
                                    Total Messages
                                </div>
                                <div style="font-size:25px;font-family:arial;color:black;">
                                    {}
                                </div>
                            </div>
                            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:25px;">
                                <div>
                                <i class="fas fa-file-word"></i>
                                    Total Words
                                </div>
                                <div style="font-size:25px;font-family:arial;color:black;">
                                    {}
                                </div>
                            </div>
                        </div>
                        <div style="display:flex;flex-direction:row;align-items:center;justify-content:space-evenly">
                            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:25px;">
                                <div>
                                <i class="fas fa-image"></i>
                                    Media Shared
                                </div>
                                <div style="font-size:25px;font-family:arial;color:black;">
                                    {}
                                </div>
                            </div>
                            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:25px;">
                                <div>
                                <i class="fas fa-link"></i>
                                    Links Shared
                                </div>
                                <div style="font-size:25px;font-family:arial;color:black;">
                                    {}
                                </div>
                            </div>
                        </div>
                        """.format(df.shape[0],get_total_words(df["Message"]),get_total_media(df["Message"]),get_total_links(df["Message"]))
                    ,unsafe_allow_html=True)
        #messages for each user
        st.header("Most Busy User")
        plt.style.use("fivethirtyeight")
        fig, ax = plt.subplots(1, 2, figsize=(10, 5))
        # Barplot for message count per user
        sns.countplot(x='Name', data=df, ax=ax[0])
        ax[0].set_title("Messages per User")
        ax[0].tick_params(axis='x', rotation=45)
        # Pie chart for message distribution
        ax[1].pie(df["Name"].value_counts(), autopct="%1.1f%%", labels=df["Name"].value_counts().index)
        ax[1].set_title("Message Distribution")
        st.pyplot(fig)
        # Daily activity timeline
        st.header("Daily Activity Timeline")
        fig1, ax = plt.subplots(figsize=(8, 4))
        daily_activity = df.groupby("Date").count()  # Get daily message counts
        sns.lineplot(data=daily_activity, x="Date", y="Message", ax=ax, color="#2E86C1", linewidth=2.5)
        # Customize the appearance
        ax.set_title("Daily Activity", fontsize=14, fontweight='bold', color='#2E86C1')
        ax.set_xlabel("Date", fontsize=12, color='#1F618D')
        ax.set_ylabel("Messages", fontsize=12, color='#1F618D')
        plt.xticks(rotation=45, fontsize=10, color='#154360')
        plt.yticks(fontsize=10, color='#154360')
        st.pyplot(fig1)
        #monthly activity
        monthly_activity,x=get_monthly_activity(df)
        fig2, ax = plt.subplots(figsize=(8, 4))
        # Create a line plot with formatted Month-Year on the x-axis and message count on the y-axis
        sns.lineplot(x=x, y=monthly_activity.values, ax=ax, color="#1ABC9C", linewidth=2.5)
        # Customize the appearance of the plot
        ax.set_title("Monthly Activity", fontsize=14, fontweight='bold', color='#1ABC9C')
        ax.set_xlabel("Month-Year", fontsize=12, color='#16A085')
        ax.set_ylabel("Messages", fontsize=12, color='#16A085')
        st.pyplot(fig2)
        #activity maps
        st.header("Activity Maps")
        #most busy day
        fig3,ax=plt.subplots(1,2,figsize=(7,2))
        week=df.groupby("Day").count()["Message"]
        ax[0].bar([i[0:3] for i in list(week.index)],week.values, color='#1f77b4', width=0.5)
        ax[0].set_title("Most Busy Day")
        #most busy month
        month=df.groupby("Month").count()["Message"]
        ax[1].bar([i[0:3] for i in list(month.index)],month.values, color='#1f77b4', width=0.5)
        ax[1].set_title("Most Busy Month")
        st.pyplot(fig3)
        #most common words 
        st.header("Most Common Words")
        most_common_words = get_most_frequest_words(df["Message"])
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=most_common_words.values, y=most_common_words.index, ax=ax)
        ax.set_title("Most Common Words")
        ax.set_xlabel("Frequency")
        ax.set_ylabel("Word")
        st.pyplot(fig)
        #emoji analysis
        col1,col2=st.columns([2.5,1.5])
        emoji_counts = extract_emojis(df["Message"])
        with col1:
            st.header("Most Common Emojis")
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.barplot(x=emoji_counts.values[:10], y=emoji_counts.index[:10], ax=ax)
            ax.set_title("Most Common Emojis")
            ax.set_xlabel("Frequency")
            ax.set_ylabel("Emoji")
            st.pyplot(fig)
        with col2:
            st.header("Emoji Counts")
            # Create a DataFrame for better formatting
            emoji_df = pd.DataFrame({'Emoji': emoji_counts.index[0:10], 'Count': emoji_counts.values[0:10]})
            # Style the DataFrame
            st.table(emoji_df)
        st.header("Word Cloud of Messages")
        generate_wordcloud(df["Message"])
        #User Message Distribution over Time (Hourly)
        st.header("Weekly Activity Map")
        data=pd.crosstab(df["Time_duration"],df["Day"],values=df['Message'],aggfunc="count")
        data.fillna(0,inplace=True)
        fig,ax=plt.subplots()
        sns.heatmap(data)
        st.pyplot(fig)
        #first message initiator
        st.subheader("First Message of the Day")
        first_message = df.groupby("Date").first()["Name"].value_counts().reset_index()
        first_message.columns = ['User', 'Count']
        fig, ax = plt.subplots()
        sns.barplot(data=first_message, x='User', y='Count', palette='viridis',ax=ax,width=0.3)
        ax.set_title("First Message initiation in a day")
        ax.set_xlabel("User")
        ax.set_ylabel("no.of times initiated conversation")
        st.pyplot(fig)
        #top 10 most Active days
        st.header("Top 10 Most Active Days")
        col1,col2=st.columns([2.5,1.5])
        data=most_active_days(df)
        with col1:
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.barplot(x=data.index, y=data.values, ax=ax)
            ax.set_title("Top 10 Most Active Days")
            ax.set_xlabel("Date")
            ax.set_ylabel("Frequency of Messages")
            plt.xticks(rotation=90)
            st.pyplot(fig)
        with col2:
            st.write(data)
        #average message length of each user
        data = get_avg_msg_length(df)
        plt.figure(figsize=(10, 8))
        # Create the bar plot
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = sns.color_palette("viridis", len(data))  # Use a color palette

        # Create a bar plot with customized aesthetics
        sns.barplot(x=list(data.keys()), y=list(data.values()), ax=ax, width=0.4, palette=colors)

        # Customize title and labels
        ax.set_title("Average Message Length of Users", fontsize=20, fontweight='bold', color='darkblue')
        ax.set_xlabel("User", fontsize=16, fontweight='bold', color='darkblue')
        ax.set_ylabel("Avg Message Length", fontsize=16, fontweight='bold', color='darkblue')

        # Rotate x-ticks for better visibility
        plt.xticks(rotation=45, ha='right', fontsize=12)

        # Add gridlines for better readability
        ax.yaxis.grid(True, linestyle='--', linewidth=0.7, alpha=0.7)
        ax.xaxis.grid(False)  # Disable x-gridlines

        # Optional: Add value labels on top of the bars
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', fontsize=12, color='black')
        # Show the plot in Streamlit
        st.header("Average Message Length of Each User")
        st.pyplot(fig)
        #which user sends the most media
        st.header("Which User sends the most Media??")
        data=get_media_counts(df)
        plt.figure(figsize=(10, 8))
        # Create the bar plot
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = sns.color_palette("viridis", len(data))  # Use a color palette

        # Create a bar plot with customized aesthetics
        sns.barplot(x=list(data.keys()), y=list(data.values()), ax=ax, width=0.4, palette=colors)

        # Customize title and labels
        ax.set_title("No.of Media Shared Per Each User", fontsize=20, fontweight='bold', color='darkblue')
        ax.set_xlabel("User", fontsize=16, fontweight='bold', color='darkblue')
        ax.set_ylabel("No.of Media Shared", fontsize=16, fontweight='bold', color='darkblue')

        # Rotate x-ticks for better visibility
        plt.xticks(rotation=45, ha='right', fontsize=12)

        # Add gridlines for better readability
        ax.yaxis.grid(True, linestyle='--', linewidth=0.7, alpha=0.7)
        ax.xaxis.grid(False)  # Disable x-gridlines

        # Optional: Add value labels on top of the bars
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', fontsize=12, color='black')
        st.pyplot(fig)