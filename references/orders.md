# Taiwan securities order API

Source: v1.37, TOC 27–59. Other markets have separate references.

`api.Order` is initialized after `api.set_Account(account)`.

For acknowledgement measurement, missing callbacks, query reconciliation and native
SDK logging, read [Order lifecycle diagnostics](order-lifecycle.md).

## Event callback

```python
def on_order_event(event):
    print(event.task, event.status, event.order_id, event.msg)

api.Order.set_event(on_order_event)
```

`set_event(event: callable)` registers a one-argument callback. Event tasks include `Task.NewOrder`, `CancelOrder`, `UpdatePrice`, `UpdateQty`, and `Deal`. Operation states include `Status.Pending`, `Success`, and `Failed`.

## Create

```python
trade = api.Order.create_order(
    action=kgi.Action.Buy,
    symbol="2330",
    qty=1,
    price=kgi.PriceType.MKT,
    time_in_force=kgi.TimeInForce.ROD,
    order_cond=kgi.OrderCond.CASH,
    odd_lot=kgi.OddLot.Common,
    name="strategy-id",
)
```

| Parameter | Type | Values / meaning |
| --- | --- | --- |
| `action`* | `kgi.Action` | `Buy`, `Sell` |
| `symbol`* | `str` | Taiwan-stock symbol |
| `qty`* | `int` | Order quantity |
| `price` | `float` or `kgi.PriceType` | valid tick price, `MKT`, `LimitUp`, `LimitDown`, `Reference`; omitted buy defaults `LimitUp`, sell defaults `LimitDown` |
| `time_in_force` | `kgi.TimeInForce` | `ROD` (default), `IOC`, `FOK` |
| `order_cond` | `kgi.OrderCond` | `CASH` (default), `MARGIN`, `SHORT_SELLING`, `Lend_SELLING`, `CASH_SELLING` |
| `odd_lot` | `kgi.OddLot` | `Common` (default), `Fixing`, `Odd_AfterMarket`, `Odd` |
| `name` | `str` | Strategy identifier |

`*` denotes a required field in the official guide.

## Update and cancel

```python
trade = api.Order.update_order(order_id, price=42.0)
trade = api.Order.update_order(order_id, qty=4)
trade = api.Order.cancel_order(order_id)
api.Order.cancel_order_all()
```

| Method | Contract |
| --- | --- |
| `update_order(order_id, price=..., qty=...)` | Pass exactly one input. `qty` reduces quantity and cannot exceed the remaining quantity; market orders cannot be repriced |
| `cancel_order(order_id)` | Cancels the identified order |
| `cancel_order_all()` | Cancels all eligible orders for the selected account |

In the official quantity example, an original quantity of 5 with `qty=4` produces `NewQty_1`.

## Query methods

```python
open_trades = api.Order.get_trades()       # full=False
all_trades = api.Order.get_trades(True)    # full=True
deals = api.Order.get_deals()
positions = api.Order.get_position()
contracts = api.Order.contract("df")       # "dic" or "df"
credit = api.Order.TSECreditInfo("2330")
```

- `get_trades(full=False) -> dict[str, Trade]`: false returns orders still in market; true returns all tracked trades.
- `get_deals() -> dict[str, list[Event]]`: deal events grouped by symbol.
- `get_position()`: position table with quantity buckets, average prices, market price, unrealized P/L, and realized P/L.
- `contract(type="dic")`: contract dictionary or DataFrame. Fields include symbol/name, market, update date, price limits, reference price, and day-trade status.
- `TSECreditInfo(symbol)`: credit and trading-status table; includes `ErrCode` and `ErrMsg`.

## Input and report boundaries

The create-order table calls qty a stock quantity without an explicit lot-unit guarantee. Common examples use qty=1 or 5; do not multiply by 1000 from an inventory or backtest schema. Consult [lifecycle quantity notes](order-lifecycle.md) if the distinction affects a live operation.

`MARGIN_DayTrade` and `SHORT_DayTrade` appear in returned-object enum tables but not in the create-order accepted-input list. Do not promote them to accepted order inputs without target-version confirmation. `Action.Sell` is a sell direction; short-sale semantics also depend on order condition and holdings.

## Object model

`Trade` contains `order`, `order_status`, and `operations`.

- `Order`: `order_id`, `action`, `symbol`, `quantity`, `price`, `order_cond`, `time_in_force`, `price_type`, `odd_lot`.
- `OrderStatus`: `nid`, `status`, `modified_time`, `modified_quantity`, `modified_price`, `deals`.
- `Operation`: `nid`, `task`, `status`, `op_time`, `msg`.
- `Event`: task/status plus order ID, sequence, action, symbol, quantity, price, order condition, time-in-force, lot mode, timestamp, and message as applicable.
- Order status values include `Submitted`, `Filled`, `PartFilled`, `Cancelled`, and `PartFilled_Cancelled`.
- `OrderStatus.deals` contains `Deal` objects with `price`, `quantity`, `ts`, and `reportseq`; do not serialize these as if they were full callback `Event` objects.

## Official pages

- [Create](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/orderCreate), [update](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/orderUpdate), [cancel](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/orderCancel), [cancel all](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/orderCancelAll)
- [Trades](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/orderGetTrades), [deals](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/orderGetDeals), [positions](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/orderGetPosition), [contracts](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/orderContract), [credit](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/orderTSECreditInfo)
- [Order callback](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/orderSetEvent), [Trade fields](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/tradeObject), [Event fields](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/eventObject)
