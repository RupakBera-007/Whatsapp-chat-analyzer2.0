import re
import pandas as pd

def preprocess(data):

    # Universal WhatsApp Pattern
    pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4},\s\d{1,2}:\d{2}(?:\s?[apAP][mM])?\s-\s'

    # Extract messages and dates
    messages = re.split(pattern, data)[1:]

    dates = re.findall(pattern, data)

    # Create DataFrame
    df = pd.DataFrame({
        'user_message': messages,
        'message_date': dates
    })

    # Convert dates safely
    df['message_date'] = pd.to_datetime(
        df['message_date'],
        errors='coerce',
        dayfirst=True
    )

    # Rename column
    df.rename(
        columns={'message_date': 'date'},
        inplace=True
    )

    users = []
    messages = []

    # Extract users and messages
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

    # Add columns
    df['user'] = users
    df['message'] = messages

    # Remove null dates
    df.dropna(subset=['date'], inplace=True)

    # Time Features
    df['only_date'] = df['date'].dt.date
    df['Year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['Month'] = df['date'].dt.month_name()
    df['day_name'] = df['date'].dt.day_name()
    df['Day'] = df['date'].dt.day
    df['Hour'] = df['date'].dt.hour
    df['Minutes'] = df['date'].dt.minute

    # Period Column
    period = []

    for hour in df['Hour']:

        if hour == 23:

            period.append("23-00")

        elif hour == 0:

            period.append("00-1")

        else:

            period.append(f"{hour}-{hour+1}")

    df['Period'] = period

    return df
