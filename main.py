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

# ================= PAGE CONFIG =================

st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="📱",
    layout="wide"
)

# ================= PREMIUM CSS =================

st.markdown("""
<style>

/* ================= APP ================= */

.stApp {
    background: linear-gradient(135deg,#020617,#0f172a);
    color: white;
}

/* ================= CONTAINER ================= */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* ================= SIDEBAR ================= */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#111827,#1e293b);
    border-right: 2px solid #334155;
}

/* ================= TITLES ================= */

.main-title {
    text-align: center;
    font-size: 52px;
    font-weight: bold;
    background: linear-gradient(to right,#38bdf8,#22c55e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

.subtitle {
    text-align: center;
    color: #cbd5e1;
    font-size: 18px;
    margin-bottom: 35px;
}

/* ================= METRIC CARDS ================= */

[data-testid="metric-container"] {
    background: rgba(30,41,59,0.7);
    border-radius: 22px;
    padding: 22px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    box-shadow: 0px 10px 25px rgba(0,0,0,0.35);
    transition: 0.3s;
}

[data-testid="metric-container"]:hover {
    transform: translateY(-5px);
    border: 1px solid #38bdf8;
}

/* ================= BUTTON ================= */

.stButton > button {
    width: 100%;
    border-radius: 14px;
    border: none;
    background: linear-gradient(90deg,#2563eb,#38bdf8);
    color: white;
    font-size: 16px;
    font-weight: bold;
    padding: 12px;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.03);
    box-shadow: 0px 0px 15px rgba(56,189,248,0.5);
}

/* ================= FILE UPLOADER ================= */

[data-testid="stFileUploader"] {
    border-radius: 18px;
    border: 2px dashed #38bdf8;
    background-color: rgba(15,23,42,0.8);
    padding: 15px;
}

/* ================= DATAFRAME ================= */

[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
}

/* ================= HIDE STREAMLIT ================= */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# ================= HERO SECTION =================

st.markdown(
    """
    <div class='main-title'>
    📱 WhatsApp Chat Analyzer
    </div>

    <div class='subtitle'>
    Advanced Chat Insights • Interactive Dashboard • AI Analysis
    </div>
    """,
    unsafe_allow_html=True
)

# ================= SIDEBAR =================

st.sidebar.title("📱 WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader(
    "Choose WhatsApp Chat File",
    type=["txt", "zip"]
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
    ### 👨‍💻 Developer

    **Rupak Bera**

    Built with Streamlit & Python
    """
)

# ================= MAIN APP =================

if uploaded_file is not None:

    st.success("✅ Chat Uploaded Successfully")

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

        with st.spinner("Analyzing WhatsApp Chat..."):

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

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
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

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
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

                fig, ax = plt.subplots(figsize=(12, 6))

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

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
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

            # ================= ACTIVE HOUR =================

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

                analysis = TextBlob(str(message))

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
                    values='Count'
                )

                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # ================= DOWNLOAD REPORT =================

            st.title("⬇ Download Analysis Report")

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

====================================
"""

            st.download_button(
                label="📥 Download Full Analysis Report",
                data=report,
                file_name="whatsapp_analysis_report.txt",
                mime="text/plain"
            )

else:

    st.info(
        "📤 Upload a WhatsApp exported TXT or ZIP file to begin analysis."
    )