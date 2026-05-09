import streamlit as st
import chat_preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from textblob import TextBlob
from collections import Counter
import pandas as pd
import zipfile
import io


# ================= PAGE CONFIG =================

st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="📱",
    layout="wide"
)

# ================= CUSTOM CSS =================

st.markdown("""
<style>

/* Main Background */

.main {
    background-color: #0E1117;
    color: white;
}

/* App Container */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1F1F2E, #111827);
    border-right: 2px solid #2E2E3A;
}

/* Titles */

h1 {
    color: #FFFFFF;
    font-size: 42px;
    font-weight: bold;
}

h2, h3, h4 {
    color: #F3F4F6;
}

/* Metric Cards */

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1E293B, #0F172A);
    border: 1px solid #334155;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
    transition: 0.3s;
}

/* Hover Effect */

[data-testid="metric-container"]:hover {
    transform: translateY(-5px);
    border: 1px solid #38BDF8;
}

/* Buttons */

.stButton > button {
    background: linear-gradient(90deg, #2563EB, #38BDF8);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: bold;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.05);
}

/* File Uploader */

[data-testid="stFileUploader"] {
    background-color: #1E293B;
    border-radius: 12px;
    padding: 10px;
    border: 1px solid #334155;
}

/* Dataframe */

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Scrollbar */

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-thumb {
    background: #38BDF8;
    border-radius: 10px;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================

st.sidebar.title("📱 WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader(
    "Choose WhatsApp Chat File",
    type=["txt", "zip"]
)

# ================= MAIN APP =================

if uploaded_file is not None:

    

    if uploaded_file.name.endswith(".zip"):

        with zipfile.ZipFile(uploaded_file, "r") as zip_ref:

            txt_files = [
                file for file in zip_ref.namelist()
                if file.endswith(".txt")
            ]

            if txt_files:

                extracted_file = zip_ref.open(txt_files[0])

                data = extracted_file.read().decode("utf-8")

            else:

                st.error("No TXT file found inside ZIP")

                st.stop()

    else:

        bytes_data = uploaded_file.getvalue()

        data = bytes_data.decode("utf-8")



    df = chat_preprocessor.preprocess(data)

    # ================= USER LIST =================

    user_list = df['user'].unique().tolist()

    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()

    user_list.insert(0, 'Overall')

    selected_user = st.sidebar.selectbox(
        "Show Analysis WRT",
        user_list
    )

    # ================= SHOW ANALYSIS =================

    if st.sidebar.button("Show Analysis"):

        st.title("📊 WhatsApp Chat Analysis Dashboard")

        # ================= TOP STATS =================

        num_messages, words, num_media_messages, num_links = helper.fetch_stats(
            selected_user,
            df
        )

        avg_words = helper.average_words_per_message(
            selected_user,
            df
        )

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Messages", num_messages)

        with col2:
            st.metric("Words", words)

        with col3:
            st.metric("Media", num_media_messages)

        with col4:
            st.metric("Links", num_links)

        with col5:
            st.metric("Avg Words", avg_words)

        # ================= MONTHLY TIMELINE =================

        st.title("📈 Monthly Timeline")

        timeline = helper.monthly_timeline(
            selected_user,
            df
        )

        fig = px.line(
            timeline,
            x='time',
            y='message',
            markers=True,
            color_discrete_sequence=['#38BDF8']
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ================= DAILY TIMELINE =================

        st.title("📅 Daily Timeline")

        daily_timeline = helper.daily_timeline(
            selected_user,
            df
        )

        fig = px.line(
            daily_timeline,
            x='only_date',
            y='message',
            color_discrete_sequence=['#22C55E']
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ================= ACTIVITY MAP =================

        st.title("🔥 Activity Map")

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Most Busy Day")

            busy_day = helper.weekly_activity_map(
                selected_user,
                df
            )

            fig, ax = plt.subplots()

            ax.bar(
                busy_day.index,
                busy_day.values,
                color='orange'
            )

            plt.xticks(rotation='vertical')

            st.pyplot(fig)

        with col2:

            st.subheader("Most Busy Month")

            busy_month = helper.monthly_activity_map(
                selected_user,
                df
            )

            fig, ax = plt.subplots()

            ax.bar(
                busy_month.index,
                busy_month.values,
                color='green'
            )

            plt.xticks(rotation='vertical')

            st.pyplot(fig)

        
        # ================= HEATMAP =================

        st.title("🗓 Weekly Activity Heatmap")

        user_heatmap = helper.activity_heatmap(
            selected_user,
            df
        )

        if not user_heatmap.empty:

            fig, ax = plt.subplots(figsize=(10, 5))

            sns.heatmap(
                user_heatmap,
                cmap='YlGnBu',
                ax=ax
            )

            st.pyplot(fig)

        else:

            st.warning(
                "No activity data available for heatmap."
            )
    


        # ================= BUSY USERS =================

        if selected_user == 'Overall':

            st.title("👥 Most Busy Users")

            x, new_df = helper.most_busy_users(df)

            col1, col2 = st.columns(2)

            with col1:

                fig, ax = plt.subplots()

                ax.bar(
                    x.index,
                    x.values,
                    color='purple'
                )

                plt.xticks(rotation='vertical')

                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # ================= WORD CLOUD =================

        st.title("☁️ WordCloud")

        df_wc = helper.create_wordcloud(
            selected_user,
            df
        )

        fig, ax = plt.subplots(figsize=(10, 5))

        ax.imshow(df_wc)

        ax.axis('off')

        st.pyplot(fig)

        # ================= MOST COMMON WORDS =================

        st.title("📝 Most Common Words")

        most_common_df = helper.most_common_words(
            selected_user,
            df
        )

        fig = px.bar(
            most_common_df,
            x=0,
            y=1,
            labels={
                '0': 'Words',
                '1': 'Frequency'
            },
            color_discrete_sequence=['#F97316']
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ================= EMOJI ANALYSIS =================

        st.title("😂 Emoji Analysis")

        emoji_df = helper.emoji_helper(
            selected_user,
            df
        )

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:

            if not emoji_df.empty:

                top_emoji = emoji_df.head(10)

                fig, ax = plt.subplots(figsize=(8, 8))

                ax.pie(
                    top_emoji[1],
                    labels=None,
                    autopct="%0.2f%%",
                    startangle=90
                )

                ax.legend(
                    top_emoji[0],
                    title="Emojis",
                    loc="center left",
                    bbox_to_anchor=(1, 0.5),
                    fontsize=12
                )

                st.pyplot(fig)

            else:
                st.write("No Emoji Found")

        # ================= MOST ACTIVE HOUR =================

        st.title("⏰ Most Active Hour")

        active_hour = helper.most_active_hour(
            selected_user,
            df
        )

        fig, ax = plt.subplots()

        ax.plot(
            active_hour.index,
            active_hour.values,
            color='red',
            linewidth=3
        )

        plt.xlabel("Hour")
        plt.ylabel("Messages")

        st.pyplot(fig)

        # ================= SENTIMENT ANALYSIS =================

        st.title("😊 Sentiment Analysis")

        if selected_user != 'Overall':
            temp_df = df[df['user'] == selected_user]
        else:
            temp_df = df

        sentiments = []

        for message in temp_df['message']:

            analysis = TextBlob(message)

            polarity = analysis.sentiment.polarity

            if polarity > 0:
                sentiments.append("Positive")

            elif polarity < 0:
                sentiments.append("Negative")

            else:
                sentiments.append("Neutral")

        sentiment_df = pd.DataFrame(
            Counter(sentiments).items(),
            columns=['Sentiment', 'Count']
        )

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(sentiment_df)

        with col2:

            fig = px.pie(
                sentiment_df,
                names='Sentiment',
                values='Count',
                color='Sentiment',
                color_discrete_map={
                    'Positive': 'green',
                    'Negative': 'red',
                    'Neutral': 'gray'
                }
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        

     
        # ================= DOWNLOAD ANALYSIS REPORT =================

        st.title("⬇ Download Analysis Report")

        # Generate Report Text

        report = f"""
        WHATSAPP CHAT ANALYSIS REPORT
        ====================================

        Selected User: {selected_user}

        ------------------------------------
        BASIC STATISTICS
        ------------------------------------

        Total Messages : {num_messages}

        Total Words : {words}

        Media Shared : {num_media_messages}

        Links Shared : {num_links}

        Average Words Per Message : {avg_words}

        ------------------------------------
        SENTIMENT ANALYSIS
        ------------------------------------
        """

        # Add Sentiment Counts

        for index, row in sentiment_df.iterrows():

            report += f"""
        {row['Sentiment']} Messages : {row['Count']}
        """

        # Most Active User

        if selected_user == 'Overall':

            most_active_user = df['user'].value_counts().idxmax()

            report += f"""

        ------------------------------------
        MOST ACTIVE USER
        ------------------------------------

        {most_active_user}
        """

        # Final Summary

        report += """

        ------------------------------------
        PROJECT SUMMARY
        ------------------------------------

        This report was generated using the
        WhatsApp Chat Analyzer developed
        with Python, Streamlit, Pandas,
        Matplotlib, Seaborn and Plotly.

        ====================================
        """

        # Download Button

        st.download_button(
            label="📥 Download Full Analysis Report",
            data=report,
            file_name="whatsapp_analysis_report.txt",
            mime="text/plain"
        )


else:

    st.title("📱 WhatsApp Chat Analyzer")

    st.write(
        "Upload a WhatsApp exported chat file to begin analysis."
    )

