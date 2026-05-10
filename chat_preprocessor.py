import re
import pandas as pd


def preprocess(data):

    # ALL POSSIBLE WHATSAPP DATE-TIME FORMATS
    patterns = [
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?[apAP][mM]\s-\s',
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s',
        r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s?[APap][mM]\]',
        r'\d{1,2}-\d{1,2}-\d{2,4},\s\d{1,2}:\d{2}\s?[APap][mM]\s-\s'
    ]

    messages = []
    dates = []

    used_pattern = None

    # Detect working pattern
    for pattern in patterns:

        test_messages = re.split(pattern, data)

        if len(test_messages) > 1:
            used_pattern = pattern
            break

    if used_pattern is None:
        return pd.DataFrame(columns=[
            'date', 'user', 'message',
            'only_date', 'Year', 'month_num',
            'Month', 'day_name', 'Day',
            'Hour', 'Minutes', 'Period'
        ])

    messages = re.split(used_pattern, data)[1:]
    dates = re.findall(used_pattern, data)

    df = pd.DataFrame({
        'user_message': messages,
        'message_date': dates
    })

    # CLEAN DATE
    df['message_date'] = (
        df['message_date']
        .str.replace('[', '', regex=False)
        .str.replace(']', '', regex=False)
        .str.strip()
    )

    # MULTIPLE DATE FORMAT SUPPORT
    parsed = None

    formats = [
        '%d/%m/%Y, %I:%M %p -',
        '%d/%m/%y, %I:%M %p -',
        '%d/%m/%Y, %H:%M -',
        '%d/%m/%y, %H:%M -',
        '%d-%m-%Y, %I:%M %p -',
        '%d-%m-%y, %I:%M %p -',
        '%d/%m/%Y, %I:%M:%S %p',
        '%d/%m/%y, %I:%M:%S %p'
    ]

    for fmt in formats:

        try:
            parsed = pd.to_datetime(
                df['message_date'],
                format=fmt,
                errors='raise'
            )

            break

        except:
            continue

    # FALLBACK
    if parsed is None:
        parsed = pd.to_datetime(
            df['message_date'],
            errors='coerce'
        )

    df['date'] = parsed

    df.dropna(subset=['date'], inplace=True)

    users = []
    messages = []

    for message in df['user_message']:

        entry = re.split(r'([\w\W]+?):\s', message)

        if len(entry) >= 3:

            users.append(entry[1])
            messages.append(entry[2])

        else:

            users.append('group_notification')
            messages.append(message)

    df['user'] = users
    df['message'] = messages

    df.drop(columns=['user_message'], inplace=True)

    # FORCE STRING
    df['message'] = df['message'].astype(str)

    # DATE FEATURES
    df['only_date'] = df['date'].dt.date
    df['Year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['Month'] = df['date'].dt.month_name()
    df['day_name'] = df['date'].dt.day_name()
    df['Day'] = df['date'].dt.day
    df['Hour'] = df['date'].dt.hour
    df['Minutes'] = df['date'].dt.minute

    # PERIOD
    period = []

    for hour in df['Hour']:

        if hour == 23:
            period.append("23-00")

        elif hour == 0:
            period.append("00-01")

        else:
            period.append(f"{hour}-{hour+1}")

    df['Period'] = period

    return df

