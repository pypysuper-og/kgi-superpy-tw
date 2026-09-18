# Data, MSMP, and backtest API

Source: v1.37, TOC 320–383. Dataset names, times and fee defaults below are manual snapshots, not current market-rule or freshness guarantees.

## Data

```python
snapshots = api.Data.get_snapshots(["2330", "2454"])
catalog = api.Data.get_table()
prices = api.Data.get(
    "還原日K價量資料(個股、ETF、大盤)-單檔股票多個區間",
    "2330",
)
```

- `Data.get_snapshots(data: list[str]) -> dict[str, Stock]`: exchange, timestamp, last price/volume, cumulative volume, OHLC, best bid/ask, limits, and reference price.
- `Data.get_table()`: exact available dataset names and positional arguments.
- `Data.get(table, *args)`: DataFrame for an exact catalog name.

Catalog groups include multi-stock/single-period, single-stock/multi-period, minute bars, batch intraday, broker branches, and other datasets. Example exact names:

- `上市櫃/ETF清單(含當沖限制)`
- `還原日K價量資料(個股、ETF、大盤)-單檔股票多個區間`
- `取得即時分K(最後交易日)`
- `批次取得個股盤中行情`
- `籌碼集中渙散/主力買賣超-單檔股票多個區間`

Documented date arguments use `yyyyMMdd`.

## Practical Taiwan dataset arguments

Get the exact current catalog via `api.Data.get_table()` before using a dataset not already bound to the target version. Selected manual entries:

| Dataset | Positional arguments after table |
| --- | --- |
| `取得即時分K(最後交易日)` | symbol, minutes (1/3/5/15/30/60) |
| `取得歷史分K(指定日期前)` | symbol, date (yyyyMMdd), minutes |
| `取得歷史3分K(指定當日)` / `取得歷史5分K(指定當日)` | symbol, date |
| `取得歷史1分K(指定日期前5天)` | symbol, endDate |
| `批次取得個股盤中行情` | list of symbols |
| `批次取得個股盤中行情-含興櫃(tick含試搓)` | list of symbols; preserve the catalog's exact spelling |
| `查詢TOP15主力分點買賣超加總資料(指定起訖日)` | symbol, startDate, endDate |
| `查詢近100日該分點資料` | symbol, brokerId in catalog format, e.g. `9268 凱基台北` |

## MSMP and ProboDataFrame

```python
catalog = api.MSMP.get_table()
adj_close = api.MSMP.get("日_K", "adj_Close")
adj_close = api.MSMP.日_K.adj_Close
```

`MSMP.get(table, name)` returns `ProboDataFrame`, with time on the index and symbols on columns.

Added methods:

- `index_str_to_date()` converts year, quarter, month, or date string indexes to trading dates.
- `first_of_week()`, `last_of_week()`, `first_of_month()`, `last_of_month()` select period boundaries.
- `reshape(df1, df2)` intersects columns, starts at the later shared date range, converts frequencies to trading dates, and forward-fills gaps.
- Arithmetic and comparison operators automatically align through the same reshape behavior.

```python
payload = api.MSMP.msmp_to_dic(
    ["sig", "qty"],
    signal_frame,
    quantity_frame,
    startday="20260101",
)
```

`msmp_to_dic(names, *dataframes, startday=None)` returns a dictionary keyed by symbol with `date`, `id`, named input columns and `adjclose`, `adjopen`, `adjhigh`, `adjlow`. It filters suspended dates. `names` and DataFrames correspond positionally. The manual defines output `qty` as shares; do not reuse it directly as a Taiwan board-lot order quantity.

## US data and USMSMP

Use `api.USData.get_table()` and `api.USData.get(table, *args)`; do not send US symbols to the Taiwan dataset namespace.

```python
us_daily = api.USData.get("日K價量資料(個股、ETF)-單檔股票多個區間", "AAPL")
us_intraday = api.USData.get("取得全天含盤前盤後歷史分k(最後交易日)", "AAPL", "F")
us_close = api.USMSMP.get("日_K", "Close")
```

The intraday market argument is F=full day, P=premarket, M=regular session, A=after-hours. Use the catalog name without the trailing space accidentally shown in a manual example. `取得歷史1/3/5/15/30/60分K` takes symbol and minutes; `批次取得個股盤中最新行情` takes a symbol list.

`USData.get_snapshots` exists, but its varargs example and list parameter table conflict. Resolve its public signature against the target version before generating the call; do not invent a `symbol=` keyword from the Taiwan interface.

`USMSMP.get_table()` gives exact tables/fields; `USMSMP.get(table, name)` and property access are shown. Its ProboDataFrame alignment matches the documented common behavior. `USMSMP.msmp_to_dic(names, *dataframes, startday=...)` returns per-symbol frames with `date`, `id`, named columns, **`Close` and `Open`**; do not assume Taiwan `adjclose`/`adjopen` columns. The description mentions adjusted prices, but the field table does not establish a corporate-action adjustment guarantee for US output.

## Domestic futures data

Use `api.Data`, not an invented `FutData`. Catalog entries include `期貨商品基本資訊`, `台指期日K`, `台指期週K`, `台指期月K`, and their `(夜盤)` versions. The K datasets take a futures symbol/alias. `取得台指近日盤歷史分K` and `取得台指近夜盤歷史分K` take minutes (1/3/5/15/30/60).

Manual examples use `TXF` or a dated contract. Distinguish continuous/nearby historical series from a specific tradable expiry. No futures MSMP or overseas-futures dataset facade is established in this manual.

## Expected update times

These are the manual's stated processing schedules; it does not explicitly establish the timezone or a guaranteed deadline. Verify the dataset's actual observation/publication dates before using it.

| Market / data | Stated update |
| --- | --- |
| Taiwan financial statements | Friday 21:00 |
| Taiwan basic OHLCV | Business day 19:00 |
| Taiwan technical indicators and chips | Business day 23:00 |
| Taiwan three institutional investors | Business day 21:00 |
| Taiwan major shareholders | Saturday 13:00 |
| Taiwan margin/short | Business day 01:00 |
| Taiwan premarket files | Business day 08:30 |
| US listed database groups | Business day 13:30 |
| Domestic futures day-session OHLCV | Business day 19:00 |
| Domestic futures night-session OHLCV | Business day 09:00 |

The manual allows delays caused by exchange announcements, transfer processing or communications. A schedule does not prove the dataset is fresh. Forward-filling and period-to-trading-date conversion do not independently prove point-in-time availability; guard against look-ahead bias when aligning fundamentals and signals.

## Backtest

`api.backtest(data, ...)` accepts a DataFrame or `dict[symbol, DataFrame]`.

| Parameter | Contract |
| --- | --- |
| `date` | Date-column name |
| `symbol` | Symbol-column name for single-DataFrame input; dictionary keys provide it otherwise |
| `sig_value` | Required reference-price column for stop calculations |
| `open_value`, `close_value` | Entry/exit price columns; each defaults to `sig_value` |
| `open_shift`, `close_shift` | Default `True`; execute on next bar rather than signal bar |
| `longsig`, `shortsig` | Entry-signal columns; at least one required; `True` enter, `False` exit, `NaN` no action |
| `longout`, `shortout` | Optional explicit exit columns; exit wins when entry and exit are both true |
| `qty` | Required quantity-column name |
| `tax` | Tax rate; documented Taiwan defaults: stock `0.003`, ETF `0.001`, stock day trade `0.0015` |
| `fee` | Fee rate; documented default `0.00025` |
| `slippage` | Documented default `0` |
| `earn`, `loss` | Take-profit / stop-loss percentages |
| `moveloss` | Trailing-stop percentage |
| `max_hold` | Maximum holding days |
| `continuous_wins` | `(N, M)` / list: after N wins, quantity multiplier M |
| `force_exit` | List of symbols whose held positions must exit on the final K-bar; not a Boolean |
| `benchmark` | Series indexed by date |
| `messages` | Progress output; default `True` |
| `_maxtrades` | Maximum trades; documented default `10000` |

```python
result = api.backtest(
    data_by_symbol,
    date="日期",
    qty="qty",
    sig_value="收盤價",
    open_value="開盤價",
    close_value="開盤價",
    longsig="sig",
    longout="sigout",
)
```

`qty` is a column name despite an inconsistent int type cell. `earn`, `loss` and `moveloss` use percentage points (20 means 20%), whereas `fee`, `tax` and `slippage` use fractions (0.001 means 10 bp). Fee/slippage apply on entry and exit. Use explicit cost assumptions; Taiwan defaults are not a current statutory-rate guarantee and must not be applied to US trades by default. The manual explicitly says US tax must be set by the user.

For a long position, the shown trailing threshold is maximum observed `sig_value` since entry × (1 − 0.01 × moveloss); for short, minimum × (1 + 0.01 × moveloss). Keep signal timing (`open_shift`/`close_shift`) explicit. Backtest fills do not prove executable live order prices or market access.

Result surfaces:

- `result.report`: performance metrics.
- `result.trade`: transaction details.
- `result.position`: daily positions.
- `result.daily`: daily account P/L.
- `result.plotly`: performance figures.
- `result.dashboard(path=..., view=...)`: HTML/dashboard output.
- `result.save(save_path=..., fig=False)`: local result export; the manual suggests `kaleido==0.1.0.post1` only as a figure-export troubleshooting workaround. Do not automatically downgrade an unrelated environment; check compatibility first.

For notebook Plotly display failures caused by missing `nbformat`, the manual suggests installing it. `dashboard(view=...)` has a `notebook`/`Notebook` spelling conflict; verify the target API if that mode is required. These export dependencies are unrelated to brokerage-login success.

## Official pages

- Data: [snapshots](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/getSnapshots), [catalog](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/getTable), [get](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/getData), [update schedule](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/databaseUpdateTime)
- MSMP: [catalog](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/getMSMPTable), [get](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/getMSMP), [ProboDataFrame](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/dataFrame), [conversion](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/msmpToDic)
- Backtest: [backtest](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/backtest), [dashboard](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/dashboard), [plotly](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/plotly), [save](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/save), [report](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/report), [trades](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/trade), [daily](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/daily), [positions](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/position)
