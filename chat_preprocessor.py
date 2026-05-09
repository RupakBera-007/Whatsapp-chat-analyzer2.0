import re
import pandas as pd

def preprocess(data):

    # Universal WhatsApp Pattern
    pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4},\s\d{1,2}:\d{2}\s(?:am|pm|AM|PM)?\s?-\s'

    messages = re.split(pattern, data)[1:]

    dates = re.findall(pattern, data)

    df = pd.DataFrame({
        'user_message': messages,
        'message_date': dates
    })

    # Date conversion
    df['message_date'] = pd.to_datetime(
        df['message_date'],
        errors='coerce'
    )

    df.rename(
        columns={'message_date': 'date'},
        inplace=True
    )

    users = []
    messages = []

    for message in df['user_message']:

        entry = re.split(
            r'([\w\W]+?):\s',
            message
        )

        if len(entry) >= 3:

            users.append(entry[1])

            messages.append(entry[2])

        else:

            users.append('group_notification')

            messages.append(message)

    df['user'] = users

    df['message'] = messages

    # Remove null dates
    df = df.dropna(subset=['date'])

    # Extra features
    df['only_date'] = df['date'].dt.date
    df['Year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['Month'] = df['date'].dt.month_name()
    df['day_name'] = df['date'].dt.day_name()
    df['Day'] = df['date'].dt.day
    df['Hour'] = df['date'].dt.hour
    df['Minutes'] = df['date'].dt.minute

    # Time Period
    period = []

    for hour in df['Hour']:

        if hour == 23:
            period.append(f"{hour}-00")

        elif hour == 0:
            period.append(f"00-{hour+1}")

        else:
            period.append(f"{hour}-{hour+1}")

    df['Period'] = period

    return df