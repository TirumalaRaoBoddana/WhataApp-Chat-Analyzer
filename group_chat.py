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
    pattern = r"(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}\s*[ap]m) - ([^:]+): (.+)"  
    chat_data = file.readlines()
    dates, times, names, messages = [], [], [], []
    df = pd.DataFrame()

    for line in chat_data:
        match = re.match(pattern, line.decode("utf-8"))
        if match:
            # Extract the date, time, name, and message
            date = match.group(1)
            time = match.group(2)
            name = match.group(3).strip()  # Trim any leading/trailing whitespace
            message = match.group(4).strip()  # Trim any leading/trailing whitespace

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

    # Finding the users
    unique_names = df["Name"].unique()
    # Replace "Not Empty" with "You" and keep the first user as is
    if "Not Empty" in unique_names:
        first_user = unique_names[unique_names != "Not Empty"][0]  # Get the first valid user
        df["Name"] = df["Name"].replace("Not Empty", "You")
        df["Name"] = df["Name"].replace(first_user, first_user)  # Ensure the first user is kept
    else:
        df["Name"] = df["Name"].replace("Not Empty", "You")  # Replace if no valid users
    df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y").dt.date
    df = pd.concat([df, extracting_columns(df["Date"])], axis=1, ignore_index=True)
    df.columns = ["Date", "Time", "Name", "Message", "Day", "Month", "Year"]
    # Extracting am/pm from the Time 
    df = df.assign(AmPm=df["Time"].astype(str).str[-2:])
    time_duration = []
    for i in list(df["Time"]):
        time_obj = datetime.strptime(i, '%H:%M %p')
        hours = time_obj.hour
        time_duration.append(str(hours) + "-" + str(hours + 1) + i[-2:])
    df["Time_duration"] = time_duration
    df["Time"] = df["Time"].str[:-2] # Remove am/pm from Time
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
        messages=messages[messages!="<Media omitted>"]
        total_words=[]
        for i in list(messages):
            total_words+=i.split(" ")
        words=pd.Series(total_words)
        return words.value_counts()[0:15]
    else:
        user_messages=df[df["Name"]==selected_user]
        messages=user_messages["Message"][user_messages["Message"]!="<Medial omitted>"]
        messages=messages[messages!="<Media omitted>"]
        total_words=[]
        for i in list(messages):
            total_words+=i.split(" ")
        words=pd.Series(total_words)
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
        messages=df["Message"][df["Message"]!="<Media omitted>"]
        all_messages = " ".join(messages)
    else:
        messages=df[df["Name"]==selected_user]
        messages=messages["Message"][df["Message"]!="<Media omitted>"]
        all_messages=" ".join(messages)
    wordcloud = WordCloud(width=800, height=400, max_words=200, background_color='white').generate(all_messages)
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
def analyze_group_chat(file):
    df = Create_df(file)
    df["Month"] = df["Month"].map({1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
                                   7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"})
    
    # Top statistics
    users=["All"]
    users+=get_all_users(df)
    selected_user=st.selectbox("Select User",options=users)
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
        number = st.number_input("Enter number of users to display", min_value=2, value=2)
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