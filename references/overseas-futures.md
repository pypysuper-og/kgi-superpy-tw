# Overseas futures and options

Source: v1.37 OvfutOrder (TOC 115–147), OvfutAccount (207–226). Use executable spelling `Ovfut`, not prose `OvFut`.

## Selection, contracts and create inputs

`api.set_OvfutAccount(account)` initializes `api.OvfutOrder` and `api.OvfutAccount`. Query `api.OvfutOrder.contract("df")` or `contract("dic")` (default dictionary). Contract fields include `Exchange`, `ComID`, `ComTyp`, `DecimalLength`, `SPPoint`, `Tick`, `SPTick`, `Currency`, `ContractValue`, `PMultiplier`, `PriceFlag`. Read actual tick/contract terms; don't assume stock tick rules or universal price scaling.

Register `api.OvfutOrder.set_event(callback)` before an authorized order. The callback takes one Event. Create inputs:

| Parameter | Contract |
| --- | --- |
| `exchange` | Required str: exchange code |
| `action`, `com_id`, `cp`, `com_ym` | Required first leg: action, product ID, option/futures type, contract year-month |
| `cp` | `kgi.CP.CallOption`, `PutOption`, `Futures` |
| `strike_price` | First-leg strike string; manual futures example supplies empty string |
| `action2`, `com_id2`, `cp2`, `com_ym2`, `strike_price2` | Second-leg fields for a complex/spread order; preserve all supplied leg identities |
| `qty` | Required int: contracts |
| `price` | Required numeric price; when `price_type=MKT`, manual says converted to market |
| `price_type` | Required: `PriceType.LMT`, `MKT`, `StopLossMarket`, `StopLossLimit` |
| `stop_price` | Required for either stop type; unnecessary for LMT/MKT |
| `time_in_force` | Default ROD; IOC/FOK also listed; manual restricts ROD to limit orders |

```python
# Integration fragment; values are supplied for the intended current contract.
trade = api.OvfutOrder.create_order(
    exchange=exchange,
    action=kgi.Action.Buy,
    com_id=product_id,
    cp=kgi.CP.Futures,
    com_ym=contract_year_month,
    strike_price="",
    qty=1,
    price=limit_price,
    price_type=kgi.PriceType.LMT,
    time_in_force=kgi.TimeInForce.ROD,
)
```

For two legs add the documented second-leg inputs, including its own action and month; do not flatten a spread into a stock-style `symbol` argument. The action table has uppercase spelling errors; examples/object fields use `kgi.Action.Buy`/`Sell`.

## Modification, cancellation and state

| Method | Contract |
| --- | --- |
| `OvfutOrder.update_order(order_id, price=..., qty=...)` | Either new price or reduction quantity; not both; qty <= remaining |
| `OvfutOrder.cancel_order(order_id)` | Single-order cancel |
| `OvfutOrder.cancel_order_all()` | Account-wide cancel, only if authorized |
| `OvfutOrder.get_trades(full=False)` | Active trades; True includes all |
| `OvfutOrder.get_deals()` | Deals grouped by symbol |
| `OvfutOrder.set_event(callback)` | Tasks NewOrder, UpdatePrice, UpdateQty, CancelOrder, Deal |

**Identifier ambiguity:** the update/cancel parameter table says `order_id`, but examples pass a value matching the displayed operation sequence rather than the success event's order number. Preserve both `Order.order_id` and `Operation.nid`/`Event.seqno`; resolve the accepted identifier with the target public interface/provider before sending a live change. Never try both or substitute one on an empty response.

`Trade` contains order, order_status and operations. `Order.market` / `Event.market` is the exchange; `symbol` is a structured `kgi.Symbol` with action, com_id, cp, com_ym, strike_price; a spread also has `symbol2` in examples/events. Preserve the structure and leg direction. Event quantity/price become fill quantity/price for `Task.Deal`.

Operation/Event statuses are Pending/Success/Failed; order statuses are Submitted/Filled/PartFilled/Cancelled/PartFilled_Cancelled. Deal objects hold price, quantity, ts, reportseq. Returned Trade or Pending is not proof of acceptance. Reconcile unknown outcomes before any repeat.

## Accounting

Call on `api.OvfutAccount`: `PositionSum()`, `PositionDetail()`, `COVER()`, `COVERDetail()`, `Margin()`, `Margin_EX()`, `OrderReport()`, `ExecReport()`. All are documented without inputs. They cover open positions, closed positions, equity/margin, extended equity and order/fill reports. Do not invent `OvfutOrder.get_position()`.

`OrderReport()` explicitly returns an empty DataFrame with columns when there are no records. Important fields: `ORDNO`, `OrgCnt`, `CNT`, `EXCHANGE`, `FCM`, `FFUT_ACCOUNT`, `ActNo`, `BrokerID`, `Symbol`, `ComYM`, `StrikePrice`, `CP`, `BS`, corresponding second-leg fields, `Price`, `StopPrice`, `BeforeQty`, `AfterQty`, `ErrCode`, `ErrMsg`. Do not expose account identifiers in shared examples.

`OrderFunc`: O=new, C=cancel, M=modify; these differ from both domestic futures and Taiwan stocks. Returned `TimeInForce` includes G=GTC, but the create table lists only ROD/IOC/FOK; report decoding does not prove a GTC create input is supported. Retain `FCM` and original sequence in reconciliation; do not infer private gateway calls from returned fields.

No dedicated overseas quote or historical-data facade is established by this manual. `FutQuote` and raw TAIFEX examples concern domestic futures. Do not invent `OvfutQuote`, `OvfutData` or route overseas symbols through domestic quotes without additional documentation.
