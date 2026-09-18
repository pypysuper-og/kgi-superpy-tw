# Domestic futures and options

Source: v1.37 FutOrder (TOC 91–114), FutAccount (185–206). Session and CA requirements are in [session](session.md); quotes/history in [quotes](quotes.md) and [data](data-and-backtest.md).

## Orders

`api.set_FutAccount(account)` initializes `FutOrder` and `FutAccount`. Register `api.FutOrder.set_event(callback)` before an authorized operation. Callback takes one Event.

```python
# Integration fragment; contract_symbol must identify the intended current contract.
trade = api.FutOrder.create_order(
    action=kgi.Action.Buy,
    symbol=contract_symbol,
    qty=1,
    price=limit_price,
    time_in_force=kgi.TimeInForce.ROD,
)
```

| Parameter | Contract |
| --- | --- |
| `action` | Required; code/object examples use `kgi.Action.Buy` / `Sell` |
| `symbol` | Required str; futures or options contract |
| `qty` | Required int; contracts (口數) |
| `price` | Required numeric limit price or `PriceType.MKT`, `StopLossMarket`, `RangeMarket` |
| `time_in_force` | `ROD` default; `IOC`, `FOK`; manual restricts ROD to limit orders |

The parameter table's uppercase `BUY`/`SELL` conflicts with examples; see [baseline](manual-baseline.md). No `stop_price`, `position_effect`, `trade_hour`, `category`, `order_cond`, `odd_lot`, or `name` input is established by this create table. Returned `PositionEffect` or `TradeHour` does not authorize adding such keywords. A stop-trigger workflow needs additional public-contract confirmation because the listed `StopLossMarket` enum does not establish a trigger-price input.

| Method | Contract |
| --- | --- |
| `FutOrder.update_order(order_id, price=..., qty=...)` | Either price or reduction qty, never both; reduction <= remaining quantity |
| `FutOrder.cancel_order(order_id)` | Target one order |
| `FutOrder.cancel_order_all()` | All eligible orders on selected account, only within authorized scope |
| `FutOrder.get_trades(full=False)` | Active trades; `True` includes all |
| `FutOrder.get_deals()` | Deals grouped by symbol |
| `FutOrder.set_event(callback)` | Tasks `NewOrder`, `UpdatePrice`, `UpdateQty`, `CancelOrder`, `Deal` |

The manual does not establish `FutOrder.contract()` or `FutOrder.get_position()`; use the documented Data catalog and FutAccount position queries instead of inventing symmetric methods.

## Trade, Event and reports

`Trade` has `order`, `order_status`, `operations`. Order/Event fields include `category` (`Category.FUTURE`/`OPTION`), `symbol`, quantity, price, time-in-force and `trade_hour` (`TradeHour.REGULAR`/`POSTMARKET`). Preserve the session; don't collapse night trading into a calendar-day assumption.

Operation/Event status: `Pending`, `Success`, `Failed`. Order status: `Submitted`, `Filled`, `PartFilled`, `Cancelled`, `PartFilled_Cancelled`. `Event.order_id` corresponds to `Order.order_id`; `Event.seqno` to `Operation.nid`. Deal quantity/price describe the fill, not the original order. `OrderStatus.deals` holds Deal objects (`price`, `quantity`, `ts`, `reportseq`). Keep identifiers as strings, and correlate with account/date/market context.

## Accounting

Call these on `api.FutAccount`:

| Method | Purpose |
| --- | --- |
| `PositionSum()` | Position summary: `Symbol`, `Exchange`, `ComType`, `ComID`, `ComYM`, `CP`, `BS`, `Currency`, `OTQty`, `TrdPrice`, `MPrice`, `PRTLOS`, `DealPrice` |
| `PositionDetail()` | Position detail |
| `COVER()` | Closed-position summary |
| `COVERDetail()` | Closed-position details |
| `Margin()` | Account equity/margin |
| `Margin_EX()` | Extended equity, including RMB and domestic/overseas withdrawable amounts |
| `OrderReport()` | Order status/errors |
| `ExecReport()` | Executions |

The first six sections show no-argument calls and say no arguments, while also listing an unexplained `MType`; do not invent values.

Order-report fields: `OrderNo`, `CNT`, `Symbol`, `ActNo`, `BrokerID`, `TradeDate`, `TradeHour`, `OrderFunc`, `BeforeQty`, `AfterQty`, `ErrCode`, `ErrMsg`. Here `OrderFunc` uses I=new, C=quantity change, **R=price change**, D=cancel (Taiwan securities use M for price change). `PositionEffect` describes O=open, C=close, T=day trade, A=auto in returned reports only.

Execution-report fields include `OrderNo`, `CNT`, `DealPrice`, `DealQty`, `CumQty`, `LeaveQty`, `MarketNo`; complex reports may expose `Symbol1`, `Symbol2`, `DealPrice1/2`, `Qty1/2`, `BS1/2`. That does not define a two-leg create signature on FutOrder. Use the actual method's schema rather than Taiwan or overseas field names.
