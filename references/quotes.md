# Realtime quote APIs

Source: v1.37 quote sections, TOC 227–319. For event enums and recovery, read [quote events](quote-events.md).

## Processed Taiwan `Quote`

Subscription methods do not directly return a quote object; normalized objects arrive through callbacks after subscription. Register the documented type-specific callback first.

| Subscribe method | Inputs | Payload |
| --- | --- | --- |
| `subscribe_tick(symbol, odd_lot=False)` | symbol, odd-lot flag | `Tick_Stock_v1`: OHLC, latest/cumulative volume, change, amount, flags |
| `subscribe_bidask(symbol, odd_lot=False)` | symbol, odd-lot flag | `BidAsk_Stock_v1`: five-level prices/volumes and diffs |
| `subscribe_all(symbol, odd_lot=False)` | symbol, odd-lot flag | `All_Stock_v1`: combined tick and bid/ask fields |
| `subscribe_kbar(symbol, minute)` | minute: 1, 3, 5, 15, 30, 60 | `KBar_Stock_v0`: OHLCV, average price, total amount |

```python
api.Quote.set_cb_tick(tick_callback)
api.Quote.set_cb_bidask(bidask_callback)
api.Quote.set_cb_kbar(kbar_callback)
api.Quote.set_cb_event(event_callback)

api.Quote.subscribe_tick("2330", odd_lot=False)
keys = api.Quote.get_subscriptions()
if keys:
    api.Quote.unsubscribe(keys[0])
api.Quote.unsubscribe_all()
```

`set_cb_event` receives connection, subscription, timeout, backpressure, callback, and reconnect events. The manual processed status appendix contains `Q001` through `Q045`.

## US and domestic futures processed quotes

| Facade | Methods and inputs | Callback payload |
| --- | --- | --- |
| `USQuote` | `subscribe_tick(symbol)` | `Tick_USStock_v1` |
| `USQuote` | `subscribe_bidask(symbol)` | `BidAsk_USStock_v0`: best bid/ask only (`best_bid_price`, `best_bid_volume`, `best_ask_price`, `best_ask_volume`), not Taiwan five-level lists |
| `USQuote` | `subscribe_all(symbol)` | `All_USStock_v1` |
| `USQuote` | `subscribe_kbar(symbol)` as documented | K-bar; no minute input established by the US parameter table |
| `FutQuote` | `subscribe_tick(symbol)` | `Tick_Future_v0` |
| `FutQuote` | `subscribe_bidask(symbol)` | `BidAsk_Future_v0` |
| `FutQuote` | `subscribe_all(symbol)` | `All_Future_v0` |

`USQuote` setters: `set_cb_tick`, `set_cb_bidask`, `set_cb_kbar`, `set_cb_event`. `FutQuote` setters: `set_cb_tick`, `set_cb_bidask`, `set_cb_event`; no futures `subscribe_kbar` or `set_cb_kbar` established here. No processed `set_cb_all` is established in the manual, despite combined subscriptions being documented. Do not invent it.

All three processed facades have `get_subscriptions()`, `unsubscribe(key)`, `unsubscribe_all()`. Use keys read from the same instance; never assume a symbol alone is a key. Examples:

| Market | Example keys (illustrative; use actual returned values) |
| --- | --- |
| Taiwan | `qtTickv1.TWStock.2330`, `qtBidAskv1.TWStock.2330`, `qtKBarv0.1.TWStock.2330`, `qtAllv1.TWStock.2330` |
| US | `qtTickv1.USStock.TSM`, `qtBidAskv0.USStock.TSM`, `qtKBarv0.1.USStock.TSM`, `qtAllv1.USStock.TSM` |
| Domestic futures | `qtTickv0.TWFuture.TXF`, `qtBidAskv0.TWFuture.TXF`, `qtAllv0.TWFuture.TXF` |

`FutQuote` examples use `TXF`; raw futures examples use a dated contract such as `TXFF6`. Neither is proof of the currently tradable contract for an order. Do not carry Taiwan `odd_lot` into US/futures subscriptions.

## Raw `SWQuote`

Raw subscriptions deliver incremental `SWMarketData` to one data callback; the subscribe call itself does not return that object.

```python
api.SWQuote.set_cb(raw_callback)
api.SWQuote.set_event(event_callback)
api.SWQuote.subscribe("2330", odd=False)

keys = api.SWQuote.get_subscriptions()
if keys:
    api.SWQuote.unsubscribe(keys[0])
api.SWQuote.unsubscribe_all()
```

`SWMarketData.data_type` identifies the updated group:

| Value | Group |
| --- | --- |
| `0` | Snapshot |
| `1` | Best-five order book |
| `2` | Match information |
| `3` | Cumulative match information |
| `4` | Day high/low |
| `5` | Opening information |

Other fields may contain values retained from the previous update. Exchange values include `TWSE`, `OTC`, `ES`, `TWSEOdd`, and `OTCOdd`.

Domestic futures use this same raw facade: `api.SWQuote.subscribe(contract_symbol)` and `exchange=TAIFEX`. Example keys include `TAIFEX.TXFF6`; Taiwan keys include `TWSE.2330` and `TWSEOdd.2330.Odd`. This does not establish US or overseas raw support.

Payload cautions: `simtrade=1` means indicative/test matching (試撮), not a real fill or proof the login is in simulation. Preserve raw timestamps; the field table and formatted examples differ. Do not assume identical volume/amount units across markets or processed/raw surfaces without verification.

Bit-packed fields are decoded by:

```python
status = kgi.SWQuote_status_remarks(data.status_remarks)
raise_fall = kgi.SWQuote_raise_fall_remarks(data.raise_fall_remarks)
```

The manual raw status appendix contains `SW000` through `SW011`.

## Connection and subscription limits

The v1.37 membership table states:

| Tier | Maximum connections | Symbols per connection |
| --- | --- | --- |
| 尊爵 | 9 | 100 |
| 菁英 | 3 | 50 |
| 新星 | 2 | 30 |

The connection chapters describe A+ as 9 × 100 = 900 symbols but demonstrate only seven API instances. Seven is an example, not the tier limit. Treat these as versioned entitlements, not confirmed current account permissions. Do not assume processed/raw or separate markets have independent additive quotas; use actual entitlement and server responses. A multi-connection example is not authorization to open multiple production sessions.

## Official pages

- Processed: [tick](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/quoteSubscribeTick), [bid/ask](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/quoteSubscribeBidAsk), [all](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/quoteSubscribeAll), [K-bar](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/quoteSubscribeKbar), [callbacks](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/quoteSetCB), [events](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/quoteSetEvent), [subscriptions](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/quoteGetSubscriptions), [unsubscribe](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/quoteUnsubscribe), [limits](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/connectionCount)
- Raw: [subscribe and fields](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/swQuoteSubscribe), [callback](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/swQuoteSetCB), [events](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/swQuoteSetEvent), [status decoder](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/statusRemarks), [raise/fall decoder](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/raiseRemarks), [subscriptions](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/swQuoteGetSubscriptions), [unsubscribe](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/swQuoteUnsubscribe), [limits](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/swConnectionCount)
- [Processed and raw status codes](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/event)
