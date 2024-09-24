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
    #creating date time object
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for i in list(df):
        date_obj = datetime.strptime(str(i), '%Y-%m-%d')
        day.append(weekday_names[date_obj.weekday()])
        month.append(date_obj.month)
        year.append(date_obj.year)
    return pd.DataFrame({
        "Day":day,
        "Month":month,
        "Year":year,
    })
def Create_df(file):
    pattern = r"^(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}\s[ap]m) - ([^:]+): (.*)"
    chat_data=file.readlines() 
    dates=[]
    times=[]
    names=[]
    messages=[]
    df=pd.DataFrame()
    for line in chat_data:
        match = re.match(pattern, line.decode("utf-8"))
        if match:
            # Extract the date, time, name, and message
            date = match.group(1)
            time = match.group(2)
            name = match.group(3)
            message = match.group(4)
            # Append the extracted data to respective lists
            dates.append(date)
            times.append(time)
            names.append(name)
            messages.append(message)
    df = pd.DataFrame({
        'Date': dates,
        'Time': times,
        'Name': names,
        'Message': messages
    })
    df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y").dt.date
    #Extracting the day, month, year from the date column
    df = pd.concat([df, extracting_columns(df["Date"])], axis=1, ignore_index=True)
    df.columns = ["Date", "Time", "Name", "Message", "Day", "Month", "Year"]
    df = df.assign(AmPm=df["Time"].astype(str).str[-2:])
    time_duration = []
    for i in list(df["Time"]):
        time_obj = datetime.strptime(i, '%H:%M %p')
        hours = time_obj.hour
        time_duration.append(str(hours) + "-" + str(hours + 1) + i[-2:])
    df["Time_duration"] = time_duration
    df["Time"] = df["Time"].str[:-2]  # Remove the AM/PM part from time
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
    return words.value_counts()[0:10]
def extract_emojis(messages):
    emoji_list = []
    for msg in messages:
        emoji_list.extend([char for char in msg if char in emoji.EMOJI_DATA])
        # Extend the list with found emojis (flatten the list)
    return pd.Series(emoji_list).value_counts()
def generate_wordcloud(messages):
    messages=messages[messages!="<Media omitted>"]
    all_messages = " ".join(messages)
    wordcloud = WordCloud(width=800, height=400, max_words=200, background_color='white').generate(all_messages)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off') 
    st.pyplot(fig)
def analyze_normal_chat(file):
    df=Create_df(file)
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
    df['Date'] = pd.to_datetime(df['Date'])
    # Extract the month from the 'Date' column
    df['MonthNum'] = df['Date'].dt.month
    monthly_activity=df.groupby(["Year","MonthNum"],sort=[True,True]).count()["Message"]
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
    st.header("Most Common Emojis")
    emoji_counts = extract_emojis(df["Message"])
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=emoji_counts.values[:10], y=emoji_counts.index[:10], ax=ax)
    ax.set_title("Most Common Emojis")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Emoji")
    st.pyplot(fig)
    #generating word cloud
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