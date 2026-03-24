import numpy as np
import pandas as pd

# Case 1: Membership wins
# Frequent rider, lots of e-bikes, longer rides. (e.g., 60 rides/month)
np.random.seed(42)
dates_1 = pd.date_range(start="2024-05-01", end="2024-05-31", freq="12H")  # 60 rides
data_1 = {
    "started_at": dates_1,
    "ended_at": dates_1
    + pd.to_timedelta(np.random.randint(15, 60, size=len(dates_1)), unit="m"),
    "rideable_type": np.random.choice(
        ["electric_bike", "classic_bike"], size=len(dates_1), p=[0.8, 0.2]
    ),
    "start_station_name": ["Station A"] * len(dates_1),
    "end_station_name": ["Station B"] * len(dates_1),
}
df1 = pd.DataFrame(data_1)
df1.to_csv("test_membership_wins.csv", index=False)

# Case 2: Pay per use wins
# Infrequent rider, mostly classic bikes, short rides. (e.g., 5 rides/month)
dates_2 = pd.date_range(start="2024-05-01", periods=5, freq="5D")
data_2 = {
    "started_at": dates_2,
    "ended_at": dates_2
    + pd.to_timedelta(np.random.randint(5, 15, size=len(dates_2)), unit="m"),
    "rideable_type": np.random.choice(
        ["electric_bike", "classic_bike"], size=len(dates_2), p=[0.1, 0.9]
    ),
    "start_station_name": ["Station A"] * len(dates_2),
    "end_station_name": ["Station C"] * len(dates_2),
}
df2 = pd.DataFrame(data_2)
df2.to_csv("test_pay_per_use_wins.csv", index=False)

print("Generated test datasets: test_membership_wins.csv and test_pay_per_use_wins.csv")
