# Data, MSMP, and backtest API

Use the public catalog links below and the target SDK to confirm dataset contracts. Dataset names, times and fee defaults in these notes are reference values, not current market-rule or freshness guarantees.

The public Taiwan Data/MSMP catalogs were checked for the index-specific entries below on 2026-11-02. Runtime observations are labeled separately from those documented call shapes.

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
- `取得歷史分K(含加權/櫃買指數)`
- `批次取得個股盤中行情`
- `籌碼集中渙散/主力買賣超-單檔股票多個區間`

Documented date arguments use `yyyyMMdd`.

## Practical Taiwan dataset arguments

Get the exact current catalog via `api.Data.get_table()` before using a dataset not already bound to the target version. A target SDK may print the catalog and return `None`; inspect that output before deciding an entry is absent. Selected dataset entries, including the index-history entry listed in the [public catalog](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/getTable):

| Dataset | Positional arguments after table |
| --- | --- |
| `取得即時分K(最後交易日)` | symbol, minutes (1/3/5/15/30/60) |
| `取得歷史分K(含加權/櫃買指數)` | symbol, minutes (1/3/5/15/30/60); no date argument |
| `取得歷史分K(指定日期前)` | symbol, date (yyyyMMdd), minutes |
| `取得歷史3分K(指定當日)` / `取得歷史5分K(指定當日)` | symbol, date |
| `取得歷史1分K(指定日期前5天)` | symbol, endDate |
| `批次取得個股盤中行情` | list of symbols |
| `批次取得個股盤中行情-含興櫃(tick含試搓)` | list of symbols; preserve the catalog's exact spelling |
| `查詢TOP15主力分點買賣超加總資料(指定起訖日)` | symbol, startDate, endDate |
| `查詢近100日該分點資料` | symbol, brokerId in catalog format, e.g. `9268 凱基台北` |

### Taiwan indices: dataset and symbol boundaries

The public catalog explicitly lists historical minute bars including the weighted and OTC indices. Its two arguments are `symbol` and `minutes`; `取得歷史分K(指定日期前)` is a different dataset that also takes a date. Do not add a date to the index-history call by analogy.

```python
# Query examples for an already authorized, logged-in Data session.
# Check the returned identity, date range and empty state for each symbol.
daily_table = "還原日K價量資料(個股、ETF、大盤)-單檔股票多個區間"
taiex_daily = api.Data.get(daily_table, "Y9999")
otc_daily = api.Data.get(daily_table, "OTC99")
index_history = api.Data.get("取得歷史分K(含加權/櫃買指數)", "Y9999", 5)
index_latest_day = api.Data.get("取得即時分K(最後交易日)", "Y9999", 5)
```

These calls select separate datasets. A historical result does not establish latest-day availability, a streaming subscription or updates during market hours. An empty result for one dataset does not establish that the symbol has no historical data elsewhere.

Keep the identifier namespaces separate:

- A Data dataset's accepted symbols are not defined by `Order.contract()` or the products accepted by `Quote`. Absence from either product catalog does not establish absence from all Data/index datasets.
- A symbol accepted by a Data dataset does not establish acceptance by `Quote.subscribe_tick` or `Quote.subscribe_kbar`. The official [K-bar subscription page](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/quoteSubscribeKbar) demonstrates a stock; it does not establish index subscriptions.
- The [MSMP catalog](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/getMSMPTable) lists `TSE` and `OTC`, with weekly/monthly variants, as **table names**. For example, `api.MSMP.get("TSE", "Close")` uses a table and field. Do not pass those table names to Quote as inferred index symbols; no MSMP runtime result is claimed here.

### SDK 2.1.2 observations on 2026-11-02

An after-hours check used Python 3.13.5 and SDK 2.1.2. The following is a sanitized result summary, not a general service guarantee:

| Surface and inputs | Y9999 / OTC99 | Stock control: 2330 |
| --- | --- | --- |
| `Quote.subscribe_tick(symbol, odd_lot=False)` | Both stopped by local SDK symbol validation before subscription; no server acceptance observed | Subscription accepted; one callback received |
| `Data.get("取得即時分K(最後交易日)", symbol, 1)` | Both returned empty DataFrames | 266 rows, 11 columns; source `datetime` 2026-11-02 09:01–13:30 |
| Same latest-day dataset, 5 minutes | Both returned empty DataFrames | 54 rows, 11 columns; source `datetime` 2026-11-02 09:05–13:30 |
| `Data.get(daily_table, symbol)`, using the exact daily dataset above | Each returned 1,000 rows × 14 columns; source dates 2022-09-14 through 2026-11-02 | Same shape and source date range |
| `Data.get("取得歷史分K(含加權/櫃買指數)", symbol, minutes)`, separately at 1 and 5 minutes | All four calls raised SDK `FORBIDDEN` (`D403`); no minute data retrieved | Both calls had the same access denial |

All six latest-day Data calls ran in the same session. The nonempty stock control rules out a blanket conclusion that this dataset returns no after-hours data; the four empty index results remain specific to those symbols, dataset, version and observation. Preserve the SDK's timezone-naive source timestamps without claiming a timezone conversion.

The daily and historical-minute calls ran in a later single session. The daily results establish that both index symbols have retrievable daily history in this dataset. The observed 1,000 rows and start date are a returned sample, not a promise about retention or pagination. Weekly/monthly retrieval was not tested.

All six historical-minute attempts, including the stock control, were denied access in that session. Verify the dataset/service entitlement with KGI before another attempt; do not retry unchanged calls, guess replacement symbols or bypass the denial. This does not establish invalid index symbols, absence of index minute history, or a denial affecting every user. `D403` is the SDK mapping for `FORBIDDEN`; no separate raw HTTP status was captured. The public catalog establishes the call shape, while a successful historical-minute payload remains unverified here.

This check did not verify `SWQuote`, index `Quote.subscribe_kbar`, alternative index symbols or continuous intraday refresh. Do not turn local symbol validation into a server rejection, or an empty DataFrame into permanent non-support. Confirm the intended index interface and symbol with KGI before promising a live index feed; do not silently substitute a futures contract or ETF.

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

`msmp_to_dic(names, *dataframes, startday=None)` returns a dictionary keyed by symbol with `date`, `id`, named input columns and `adjclose`, `adjopen`, `adjhigh`, `adjlow`. It filters suspended dates. `names` and DataFrames correspond positionally. Confirm the output `qty` unit; do not reuse it directly as a Taiwan board-lot order quantity.

## US data and USMSMP

Use `api.USData.get_table()` and `api.USData.get(table, *args)`; do not send US symbols to the Taiwan dataset namespace.

```python
us_daily = api.USData.get("日K價量資料(個股、ETF)-單檔股票多個區間", "AAPL")
us_intraday = api.USData.get("取得全天含盤前盤後歷史分k(最後交易日)", "AAPL", "F")
us_close = api.USMSMP.get("日_K", "Close")
```

The intraday market argument is F=full day, P=premarket, M=regular session, A=after-hours. Use exact current catalog names. `取得歷史1/3/5/15/30/60分K` takes symbol and minutes; `批次取得個股盤中最新行情` takes a symbol list.

Verify whether the target `USData.get_snapshots` signature accepts varargs or a list before generating the call; do not invent a `symbol=` keyword from the Taiwan interface.

`USMSMP.get_table()` gives exact tables/fields; `USMSMP.get(table, name)` and property access are shown. Its ProboDataFrame alignment matches the documented common behavior. `USMSMP.msmp_to_dic(names, *dataframes, startday=...)` returns per-symbol frames with `date`, `id`, named columns, **`Close` and `Open`**; do not assume Taiwan `adjclose`/`adjopen` columns. The description mentions adjusted prices, but the field table does not establish a corporate-action adjustment guarantee for US output.

## Domestic futures data

Use `api.Data`, not an invented `FutData`. Catalog entries include `期貨商品基本資訊`, `台指期日K`, `台指期週K`, `台指期月K`, and their `(夜盤)` versions. The K datasets take a futures symbol/alias. `取得台指近日盤歷史分K` and `取得台指近夜盤歷史分K` take minutes (1/3/5/15/30/60).

Distinguish continuous/nearby historical series from a specific tradable expiry. No futures MSMP or overseas-futures dataset facade has been verified here; do not construct one by analogy.

## Expected update times

Check the [public update-schedule page](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/databaseUpdateTime) and the dataset's actual observation/publication dates. Reference times below do not establish a timezone or guaranteed deadline.

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

A schedule does not prove the dataset is fresh. Forward-filling and period-to-trading-date conversion do not independently prove point-in-time availability; guard against look-ahead bias when aligning fundamentals and signals.

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

`qty` selects the quantity column. `earn`, `loss` and `moveloss` use percentage points (20 means 20%), whereas `fee`, `tax` and `slippage` use fractions (0.001 means 10 bp). Fee/slippage apply on entry and exit. Use explicit cost assumptions for the target market; Taiwan defaults are not a current statutory-rate guarantee and must not be applied to US trades by default.

For a long position, the shown trailing threshold is maximum observed `sig_value` since entry × (1 − 0.01 × moveloss); for short, minimum × (1 + 0.01 × moveloss). Keep signal timing (`open_shift`/`close_shift`) explicit. Backtest fills do not prove executable live order prices or market access.

Result surfaces:

- `result.report`: performance metrics.
- `result.trade`: transaction details.
- `result.position`: daily positions.
- `result.daily`: daily account P/L.
- `result.plotly`: performance figures.
- `result.dashboard(path=..., view=...)`: HTML/dashboard output.
- `result.save(save_path=..., fig=False)`: local result export. Check figure-export dependency compatibility before changing the environment; do not automatically downgrade unrelated dependencies.

For notebook Plotly display failures, check the actual dependency error and target API, including the accepted `dashboard(view=...)` spelling. These export dependencies are unrelated to brokerage-login success.

## Official pages

- Data: [snapshots](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/getSnapshots), [catalog](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/getTable), [get](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/getData), [update schedule](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/databaseUpdateTime)
- MSMP: [catalog](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/getMSMPTable), [get](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/getMSMP), [ProboDataFrame](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/dataFrame), [conversion](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/msmpToDic)
- Backtest: [backtest](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/backtest), [dashboard](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/dashboard), [plotly](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/plotly), [save](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/save), [report](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/report), [trades](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/trade), [daily](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/daily), [positions](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/position)
