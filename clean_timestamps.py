"""Put all three vendor files on one clean hourly grid in local market time (writes to clean/).

Every output file has a naive `timestamp` column (local market time, start of hour) with exactly
24 rows per day, 2021-01-01 00:00 .. 2023-12-31 23:00 (26,280 rows), so the files merge 1:1 on `timestamp`.

What was changed (timestamp issues only):
  - load.csv: dropped 140 exact duplicate rows.
  - renewables_weather.csv: was in UTC -> converted to local time; column `time` renamed to `timestamp`.
  - DST, all files (standard EPF practice):
      spring-forward days (23h): the missing 02:00 hour is inserted as the mean of 01:00 and 03:00;
      fall-back days (25h): the two 02:00 hours are averaged into one.
    These rows have `dst_adjusted = True`.

What was NOT changed (still yours to handle):
  - price sentinels (-9999) and every other value issue;
  - the 126-hour weather outage (2022-02-07 01:00 .. 2022-02-12 06:00 local) stays as NaN rows;
  - `daily_avg_price` is the vendor's value, which averages 23 or 25 hours on DST days, so on those
    6 days it no longer matches the mean of the 24 rows exactly.
"""
from pathlib import Path

import numpy as np
import pandas as pd

TZ = 'Europe/Berlin'
OUT = Path('clean')
LOCAL_GRID = pd.date_range('2021-01-01 00:00', '2023-12-31 23:00', freq='h')


def to_clean_local(df, ts_col, source_tz):
    df = df.rename(columns={ts_col: 'timestamp'})
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # 1. unambiguous UTC key
    if source_tz == 'UTC':
        utc = df['timestamp'].dt.tz_localize('UTC')
    else:
        utc = df['timestamp'].dt.tz_localize(TZ, ambiguous='infer').dt.tz_convert('UTC')
    df = df.drop(columns='timestamp').set_index(utc.rename('ts_utc'))
    assert df.index.is_unique

    # 2. full UTC grid (vendor gaps become NaN rows), then back to naive local wall-clock time
    utc_grid = pd.date_range(LOCAL_GRID[0].tz_localize(TZ), LOCAL_GRID[-1].tz_localize(TZ), freq='h').tz_convert('UTC')
    df = df.reindex(utc_grid)
    local = df.index.tz_convert(TZ).tz_localize(None)

    # 3. fall-back: two rows share 02:00 -> average them
    doubled = local.duplicated(keep=False)
    df = df.groupby(local).mean()
    df['dst_adjusted'] = df.index.isin(local[doubled])

    # 4. spring-forward: 02:00 does not exist -> insert as the mean of 01:00 and 03:00
    df = df.reindex(LOCAL_GRID)
    inserted = df.index.difference(local)
    num = df.columns.drop('dst_adjusted')
    for t in inserted:
        df.loc[t, num] = (df.loc[t - pd.Timedelta('1h'), num] + df.loc[t + pd.Timedelta('1h'), num]) / 2
    df.loc[inserted, 'dst_adjusted'] = True
    df['dst_adjusted'] = df['dst_adjusted'].astype(bool)

    return df.rename_axis('timestamp').reset_index()


def main():
    OUT.mkdir(exist_ok=True)

    prices = pd.read_csv('prices.csv')
    load = pd.read_csv('load.csv').drop_duplicates()
    weather = pd.read_csv('renewables_weather.csv')

    out = {
        'prices.csv': to_clean_local(prices, 'timestamp', TZ),
        'load.csv': to_clean_local(load, 'timestamp', TZ),
        'renewables_weather.csv': to_clean_local(weather, 'time', 'UTC'),
    }

    # the DST averaging/interpolation must never touch a -9999 sentinel
    dst_days = out['prices.csv'].loc[out['prices.csv']['dst_adjusted'], 'timestamp'].dt.normalize()
    raw_p = prices.assign(d=pd.to_datetime(prices['timestamp']).dt.normalize())
    assert not raw_p.loc[raw_p['d'].isin(dst_days), 'price_eur_mwh'].eq(-9999).any()

    for name, df in out.items():
        assert len(df) == len(LOCAL_GRID) and df['timestamp'].is_unique
        assert df.groupby(df['timestamp'].dt.normalize()).size().eq(24).all()
        df.to_csv(OUT / name, index=False)
        print(f'{name:24s} rows={len(df)}  dst_adjusted={df.dst_adjusted.sum()}  '
              f'rows with NaN={df.drop(columns="dst_adjusted").isna().any(axis=1).sum()}')


if __name__ == '__main__':
    main()
