import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
from datetime import datetime
from wordcloud import WordCloud
import emoji
from dateutil import parser
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
def get_total_messages(df,selected_user):
    if(selected_user=="All"):
        return df.shape[0]
    else:
        messages=df[df["Name"]==selected_user]
        return messages.shape[0]
def get_total_words(df,selected_user):
    count=0
    if(selected_user=="All"):
        messages=df["Message"]
    else:
        messages=df["Message"][df["Name"]==selected_user]
    messages=messages[messages!="<Media omitted>"]
    for msg in messages:
        count+=len(msg.split(" "))
    return count
def get_total_media(df,selected_user):
    if(selected_user=="All"):
        messages=df["Message"][df["Message"]=="<Media omitted>"]
    else:
        messages=df["Message"][(df["Name"]==selected_user)&(df["Message"]=="<Media omitted>")]
    return len(messages)
def get_total_links(df,selected_user):
    links=[]
    url_pattern = r'(https?://\S+)'
    if(selected_user=="All"):
        messages=df["Message"]
        for msg in messages:
            links.extend(re.findall(url_pattern, msg))
    else:
        messages=df["Message"][df["Name"]==selected_user]
        for msg in messages:
            links.extend(re.findall(url_pattern,msg))
    return len(links)
def get_busy_user(df):
    data = df.groupby("Name").count()["Message"].sort_values(ascending=False)
    return data
def get_most_frequest_words(df,selected_user):
    messages=df["Message"]
    if(selected_user=="All"):
        messages=messages[(messages!="<Media omitted>")]
        total_words=[]
        for i in list(messages):
            total_words+=i.split(" ")
        words=pd.Series(total_words)
        words=words[(words!="message")&(words!="was")& (words!="deleted") &(words!="null") & (words!="(file") & (words!="attached)")]
        return words.value_counts()[0:15]
    else:
        user_messages=df[df["Name"]==selected_user]
        messages=user_messages["Message"][user_messages["Message"]!="<Medial omitted>"]
        messages=messages[(messages!="<Media omitted>")]
        total_words=[]
        for i in list(messages):
            total_words+=i.split(" ")
        words=pd.Series(total_words)
        words=words[(words!="message")&(words!="was")& (words!="deleted") &(words!="null")& (words!="(file" ) & (words!="attached)")]
        return words.value_counts()[0:15]
def plot_user_message_distribution(df, num=10):
    data = get_busy_user(df, num)
    fig, ax = plt.subplots(figsize=(max(10, len(data) * 1.2), 6))  # Dynamically adjust the width
    sns.barplot(x=data.values, y=data.index, ax=ax, palette="viridis")  # Horizontal barplot
    ax.set_title(f"Messages per User (Top {num})", fontsize=20)
    ax.set_xlabel("Number of Messages", fontsize=14)
    ax.set_ylabel("User", fontsize=14)
    # Adding data labels on the bars
    for p in ax.patches:
        ax.annotate(f'{int(p.get_width())}', (p.get_width(), p.get_y() + p.get_height() / 2.),
                    ha='center', va='center', fontsize=12, color='black', weight='bold')
    st.pyplot(fig)
def get_daily_activity(df,selected_user):
    if(selected_user=="All"):
        return df.groupby("Date").count()["Message"]
    else:
        messages=df[df["Name"]==selected_user]
        return messages.groupby("Date").count()["Message"]
def get_monthly_activity(df,selected_user):
    df['Date'] = pd.to_datetime(df['Date'])
    # Extract the month and year from the 'Date' column
    df['MonthNum'] = df['Date'].dt.month
    if(selected_user=="All"):
        monthly_activity = df.groupby(["Year", "MonthNum"]).count()["Message"]
        monthly_activity = monthly_activity.sort_index()
        x = [f"{i[1]:02d}-{i[0]}" for i in monthly_activity.index]  
    else:
        monthly_activity=df[df["Name"]==selected_user]
        monthly_activity = monthly_activity.groupby(["Year", "MonthNum"]).count()["Message"]
        monthly_activity = monthly_activity.sort_index()
        x = [f"{i[1]:02d}-{i[0]}" for i in monthly_activity.index]
    return monthly_activity,x
def most_busy_day(df,selected_user):
    if(selected_user=="All"):
        return df.Day.value_counts()
    else:
        selected_data=df[df["Name"]==selected_user]
        return selected_data.Day.value_counts()
def most_busy_month(df,selected_user):
    if(selected_user=="All"):
        return df.Month.value_counts()
    else:
        selected_data=df[df["Name"]==selected_user]
        return selected_data.Month.value_counts()
def extract_emojis(df,selected_user):
    if(selected_user=="All"):
        emoji_list = []
        for msg in df["Message"]:
            emoji_list.extend([char for char in msg if char in emoji.EMOJI_DATA])
            # Extend the list with found emojis (flatten the list)
        return pd.Series(emoji_list).value_counts()
    else:
        emoji_list = []
        for msg in df["Message"][df["Name"]==selected_user]:
            emoji_list.extend([char for char in msg if char in emoji.EMOJI_DATA])
            # Extend the list with found emojis (flatten the list)
        return pd.Series(emoji_list).value_counts()
def generate_wordcloud(df,selected_user):
    if(selected_user=="All"):
        messages=df["Message"][(df["Message"]!="<Media omitted>") & (df["Message"]!="null")&(df["Message"]!='This message was deleted')]
        words = " ".join(messages)
    else:
        messages=df[df["Name"]==selected_user]
        messages=messages["Message"][(df["Message"]!="<Media omitted>") & (df["Message"]!="null") & (df["Message"]!='This message was deleted')]
        words=" ".join(messages)
    wordcloud = WordCloud(width=800, height=400, max_words=200, background_color='white').generate(words)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off') 
    st.pyplot(fig)
def get_all_users(df):
    return list(df.Name.unique())
def weekely_activity_map(df,selected_user):
    if(selected_user=="All"):
        data=pd.crosstab(df["Time_duration"],df["Day"],values=df['Message'],aggfunc="count")
        data.fillna(0,inplace=True)
        return data
    else:
        res_data=df[df["Name"]==selected_user]
        data=pd.crosstab(res_data["Time_duration"],res_data["Day"],values=res_data["Message"],aggfunc="count")
        data.fillna(0,inplace=True)
        return data
def most_active_days(df,selected_user):
    if(selected_user=="All"):
        return df.groupby("Date").count()["Message"].sort_values(ascending=False)[0:10]
    else:
        return df[df["Name"]==selected_user].groupby("Date").count()["Message"].sort_values(ascending=False)[0:10]
def get_media_counts(df):
    media_counts=dict()
    for i in list(df["Name"]):
        media_counts[i]=df[(df["Message"]=="<Media omitted>") & (df["Name"]==i)].shape[0]
    return media_counts
def get_avg_msg_length(df):
    average_msg_len=dict()
    for i in df["Name"].unique():
        messages=df["Message"][df["Name"]==i]
        total_length=0
        for j in list(messages):
            total_length+=len(j)
        average_msg_len[i]=total_length/len(list(messages))
    return average_msg_len
def analyze_chat(file,index,chat_type):
    df = Create_df(file,index)
    if(df.shape[0]==0):
        st.error("select appropreate date format of the whatsapp chat")
    else:
        df["Month"] = df["Month"].map({1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                                    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"})
        # Top statistics
        users=["All"]
        users+=get_all_users(df)
        selected_user=st.sidebar.selectbox("Select User",options=users)
        st.header("Top Statistics")
        st.markdown("""
                    <div style="display:flex;flex-direction:column;justify-content:space-evenly;">
                        <div style="display:flex;flex-direction:row;align-items:center;justify-content:space-evenly">
                            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:25px;">
                                <div><i class='fas fa-comments'></i> Total Messages</div>
                                <div style="font-size:25px;font-family:arial;color:black;">{}</div>
                            </div>
                            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:25px;">
                                <div><i class="fas fa-file-word"></i> Total Words</div>
                                <div style="font-size:25px;font-family:arial;color:black;">{}</div>
                            </div>
                        </div>
                        <div style="display:flex;flex-direction:row;align-items:center;justify-content:space-evenly">
                            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:25px;">
                                <div><i class="fas fa-image"></i> Media Shared</div>
                                <div style="font-size:25px;font-family:arial;color:black;">{}</div>
                            </div>
                            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:25px;">
                                <div><i class="fas fa-link"></i> Links Shared</div>
                                <div style="font-size:25px;font-family:arial;color:black;">{}</div>
                            </div>
                        </div>
                    """.format(get_total_messages(df,selected_user), get_total_words(df,selected_user), get_total_media(df,selected_user), get_total_links(df,selected_user)), unsafe_allow_html=True)
        # Messages for each user
        if(selected_user=="All"):
            st.header("Most Busy User")
            plt.style.use("fivethirtyeight")
            number = st.number_input("Enter number of users to display", min_value=2, value=2,max_value=len(get_all_users(df)))
            data = get_busy_user(df)
            fig, ax = plt.subplots(figsize=(12,6))
            # Barplot for message count per user
            sns.barplot(x=data[:number].index, y=data[:number].values, ax=ax, palette="viridis")
            ax.set_title("Messages per User", fontsize=20)
            ax.set_xlabel("User", fontsize=14)
            ax.set_ylabel("Number of Messages", fontsize=14)
            ax.tick_params(axis='x', rotation=90)
            # Adding data labels on top of the bars
            for p in ax.patches:
                ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center', va='bottom', fontsize=12, color='black', weight='bold')
            st.pyplot(fig)
            st.header("Most busy users(Selected users only)")
            selected_users=st.multiselect("select multiple users",options=data.index)
            if(selected_users):
                selected_user_message_counts=[]
                for i in selected_users:
                    selected_user_message_counts.append(data[i])
                fig, ax = plt.subplots(figsize=(12,6))
                # Barplot for message count per user
                sns.barplot(x=selected_users, y=selected_user_message_counts, ax=ax, palette="viridis")
                ax.set_title("Messages per User", fontsize=20)
                ax.set_xlabel("User", fontsize=14)
                ax.set_ylabel("Number of Messages", fontsize=14)
                ax.tick_params(axis='x', rotation=90)
                # Adding data labels on top of the bars
                for p in ax.patches:
                    ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                                ha='center', va='bottom', fontsize=12, color='black', weight='bold')
                st.pyplot(fig)
        #daily activity timeline
        st.header("Daily Activity Timeline")
        fig1, ax = plt.subplots(figsize=(8, 4))
        daily_activity = get_daily_activity(df,selected_user)  
        # Get daily message counts
        sns.lineplot(data=pd.DataFrame(daily_activity), x=daily_activity.index, y=daily_activity.values, ax=ax, color="#2E86C1", linewidth=2.5)
        # Customize the appearance
        ax.set_title("Daily Activity", fontsize=14, fontweight='bold', color='#2E86C1')
        ax.set_xlabel("Date", fontsize=12, color='#1F618D')
        ax.set_ylabel("Messages", fontsize=12, color='#1F618D')
        plt.xticks(rotation=90, fontsize=10, color='#154360')
        plt.yticks(fontsize=10, color='#154360')
        st.pyplot(fig1)
        st.header("Monthly Activity Timeline")
        # Convert 'Date' column to datetime format
        monthly_activity,x=get_monthly_activity(df,selected_user)
        fig2, ax = plt.subplots(figsize=(8, 4))
        # Create a line plot with formatted Month-Year on the x-axis and message count on the y-axis
        sns.lineplot(x=x, y=monthly_activity.values, ax=ax, color="#1ABC9C", linewidth=2.5)
        # Customize the appearance of the plot
        ax.set_title("Monthly Activity", fontsize=14, fontweight='bold', color='#1ABC9C')
        ax.set_xlabel("Month-Year", fontsize=12, color='#16A085')
        ax.set_ylabel("Messages", fontsize=12, color='#16A085')
        # Rotate x-axis labels to fit better
        plt.xticks(rotation=45, fontsize=10, color='#0E6655')
        plt.yticks(fontsize=10, color='#0E6655')
        #Display the plot in Streamlit
        st.pyplot(fig2)
        st.header("Activity Maps")
        #most busy day
        fig3,ax=plt.subplots(1,2,figsize=(7,2))
        week=most_busy_day(df,selected_user)
        ax[0].bar([i[0:3] for i in list(week.index)],week.values, color='#1f77b4', width=0.5)
        ax[0].set_title("Most Busy Day")
        #most busy month
        month=most_busy_month(df,selected_user)
        ax[1].bar([i[0:3] for i in list(month.index)],month.values, color='#1f77b4', width=0.5)
        ax[1].set_title("Most Busy Month")
        plt.xticks(rotation=90,)
        st.pyplot(fig3)
        #most common words 
        st.header("Most Common Words")
        most_common_words = get_most_frequest_words(df,selected_user)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=most_common_words.values, y=most_common_words.index, ax=ax)
        ax.set_title("Most Common Words")
        ax.set_xlabel("Frequency")
        ax.set_ylabel("Word")
        st.pyplot(fig)
        st.header("Most Common Emojis")
        emoji_counts = extract_emojis(df,selected_user)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=emoji_counts.values[:10], y=emoji_counts.index[:10], ax=ax)
        ax.set_title("Most Common Emojis")
        ax.set_xlabel("Frequency")
        ax.set_ylabel("Emoji")
        st.pyplot(fig)
        #generating word cloud
        st.header("Word Cloud of Messages")
        generate_wordcloud(df,selected_user)
        # #User Message Distribution over Time (Hourly)
        st.header("Weekly Activity Map")
        data=weekely_activity_map(df,selected_user)
        fig,ax=plt.subplots()
        sns.heatmap(data)
        st.pyplot(fig)
        #top 10 most active days
        data=most_active_days(df,selected_user)
        st.header("Top 10 Most Active Days")
        col1,col2=st.columns([2.5,1.5])
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
        #which user sends most media
        if(selected_user=="All"):
            st.header("Which User sends the most Media??")
            data=pd.Series(get_media_counts(df)).sort_values(ascending=False)[0:15]
            plt.figure(figsize=(10, 8))
            # Create the bar plot
            fig, ax = plt.subplots(figsize=(10, 8))
            colors = sns.color_palette("viridis", len(data))  # Use a color palette
            # Create a bar plot with customized aesthetics
            sns.barplot(x=list(data.index), y=list(data.values), ax=ax, width=0.4, palette=colors)
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
            #first message initiator
            if(chat_type=="Normal Chat"):
                st.subheader("First Message of the Day")
                first_message = df.groupby("Date").first()["Name"].value_counts().reset_index()
                first_message.columns = ['User', 'Count']
                fig, ax = plt.subplots()
                sns.barplot(data=first_message, x='User', y='Count', palette='viridis',ax=ax,width=0.3)
                ax.set_title("First Message initiation in a day")
                ax.set_xlabel("User")
                ax.set_ylabel("no.of times initiated conversation")
                st.pyplot(fig)
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