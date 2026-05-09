from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()


# ================= FETCH STATS =================

def fetch_stats(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]

    words = []

    for message in df['message']:
        words.extend(message.split())

    num_media_messages = df[
        df['message'].str.contains('Media omitted', na=False)
    ].shape[0]

    links = []

    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)


# ================= MOST BUSY USERS =================

def most_busy_users(df):

    x = df['user'].value_counts().head()

    new_df = round(
        (df['user'].value_counts() / df.shape[0]) * 100,
        2
    ).reset_index()

    new_df.columns = ['name', 'percent']

    return x, new_df


# ================= WORDCLOUD =================

def create_wordcloud(selected_user, df):

    with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
        stop_words = set(f.read().split())

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']

    temp = temp[
        ~temp['message'].str.contains('Media omitted', na=False)
    ].copy()

    def remove_stop_words(message):

        y = []

        for word in message.lower().split():

            if word not in stop_words:
                y.append(word)

        return " ".join(y)

    temp['message'] = temp['message'].apply(remove_stop_words)

    wc = WordCloud(
        width=600,
        height=400,
        min_font_size=10,
        background_color='white'
    )

    df_wc = wc.generate(temp['message'].str.cat(sep=" "))

    return df_wc


# ================= MOST COMMON WORDS =================

def most_common_words(selected_user, df):

    with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
        stop_words = set(f.read().split())

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']

    temp = temp[
        ~temp['message'].str.contains('Media omitted', na=False)
    ]

    words = []

    for message in temp['message']:

        for word in message.lower().split():

            if word not in stop_words:
                words.append(word)

    common_df = pd.DataFrame(
        Counter(words).most_common(20)
    )

    return common_df


# ================= EMOJI ANALYSIS =================

def emoji_helper(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []

    for message in df['message']:

        emojis.extend([
            c for c in message
            if c in emoji.EMOJI_DATA
        ])

    emoji_df = pd.DataFrame(
        Counter(emojis).most_common(len(Counter(emojis)))
    )

    return emoji_df


# ================= MONTHLY TIMELINE =================

def monthly_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(
        ['year', 'month_num', 'month']
    ).count()['message'].reset_index()

    time = []

    for i in range(timeline.shape[0]):

        time.append(
            timeline['month'][i] +
            "-" +
            str(timeline['year'][i])
        )

    timeline['time'] = time

    return timeline


# ================= DAILY TIMELINE =================

def daily_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby(
        'only_date'
    ).count()['message'].reset_index()

    return daily_timeline


# ================= WEEKLY ACTIVITY =================

def weekly_activity_map(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


# ================= MONTHLY ACTIVITY =================

def monthly_activity_map(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


# ================= HEATMAP =================

def activity_heatmap(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(
        index='day_name',
        columns='period',
        values='message',
        aggfunc='count'
    ).fillna(0)

    return user_heatmap


# ================= MOST ACTIVE HOUR =================

def most_active_hour(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['hour'].value_counts().sort_index()


# ================= AVG WORDS =================

def average_words_per_message(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    total_words = []

    for message in df['message']:
        total_words.extend(message.split())

    if df.shape[0] == 0:
        return 0

    return round(len(total_words) / df.shape[0], 2)

