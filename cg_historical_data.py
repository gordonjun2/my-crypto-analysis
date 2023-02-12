from pycoingecko import CoinGeckoAPI
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt
import numpy as np
import math

### Variables to edit

# format: year, month, day, hour, minute, second
start_date_time = datetime(2020, 12, 1, 0, 0, 0)
end_date_time = datetime(2023, 2, 1, 0, 0, 0)      

timeframe_hour = 24

# add coin ids into this list
coins_list = ['bitcoin', 'solana']

### Utils

def calculate_hours_apart(start_date_time, end_date_time):
    delta = end_date_time - start_date_time
    total_seconds = delta.total_seconds()
    total_hours = total_seconds / (60 * 60)

    return total_hours

if not isinstance(timeframe_hour, int) or timeframe_hour <= 0:
    print("'timeframe_hour' has to be integer equal or more than 1!")
    raise ValueError

print('\nTimeframe is set to be {} hour.'.format(str(timeframe_hour)))

### Data retrievings

cg = CoinGeckoAPI()

hours_apart = calculate_hours_apart(start_date_time, end_date_time)
time_array = np.array([start_date_time + timedelta(hours=i) for i in range(1, math.floor(hours_apart) + 1)])
hours_in_90_days = 90 * 24
unix_timestamp_split = []

# 90 days have 90 x 24 hours
if hours_apart > hours_in_90_days:
    num_unix_timestamp_batch = math.ceil(hours_apart / hours_in_90_days)
    for n in range(num_unix_timestamp_batch):
        start_date_time_batch = start_date_time + timedelta(hours = n * hours_in_90_days)
        if n == num_unix_timestamp_batch - 1:
            end_date_time_batch = start_date_time_batch + timedelta(hours = hours_apart % hours_in_90_days)
        else:
            end_date_time_batch = start_date_time_batch + timedelta(hours = hours_in_90_days - 1)
        unix_timestamp_split.append([time.mktime(start_date_time_batch.timetuple()), time.mktime(end_date_time_batch.timetuple())])
else:
    unix_timestamp_split.append([time.mktime(start_date_time.timetuple()), time.mktime(end_date_time.timetuple())])

'''
Method: cg.get_coin_market_chart_range_by_id

Get historical market data include price, market cap, and 24h volume within a range of timestamp (granularity auto)

Data granularity is automatic (cannot be adjusted)
Less than or equals to 90 days from current time = hourly data
above 90 days from current time = daily data (00:00 UTC)
'''

percentage_change_dict = {}

for coin in coins_list:
    print('\nRetrieving {} data ...'.format(coin.capitalize()))

    data_volume_prices = np.empty((0,2))

    for start_unix_timestamp, end_unix_timestamp in unix_timestamp_split:
        data = np.array(cg.get_coin_market_chart_range_by_id(id=coin, vs_currency='usd', from_timestamp=start_unix_timestamp, to_timestamp=end_unix_timestamp)['prices'])
        data_volume_prices = np.vstack((data_volume_prices, data))

    data_prices = data_volume_prices[:, 1]

    if len(data_prices) != len(time_array) + 1:
        print('The length of the retrieved data is not the same as the total hours within the specified period. \nPerforming interpolation ...')
        time_index = np.arange(len(data_prices))
        new_time_index = np.linspace(0, len(data_prices) - 1, len(time_array) + 1)
        data_prices = np.interp(new_time_index, time_index, data_prices)

    data_prices = data_prices[::timeframe_hour]

    percentage_change = []

    for i in range(1, len(data_prices)):
        percentage_change.append(100 * (data_prices[i] - data_prices[i-1]) / data_prices[i-1])

    percentage_change_dict[coin] = percentage_change

### Plot the time series data

time_array = time_array[::timeframe_hour]

for coin, percentage_change in percentage_change_dict.items():
    plt.plot(time_array, percentage_change, label=coin.capitalize())

plt.xlabel('Date and Time')
plt.ylabel('Price % Change')
plt.title('{} Hourly Percentage Change'.format(str(timeframe_hour)))
plt.xlim(time_array[0], time_array[-1])
plt.grid()
plt.legend()
plt.show()

print('\nCompleted, did you learn anything? =)')
