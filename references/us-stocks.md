# US stocks through sub-brokerage

Source: v1.37, sections SubOrder (TOC 60–90) and SubAccount (174–184). Read [session](session.md) first for eligibility and the explicit absence of US simulation. Quotes and data use [USQuote](quotes.md) and [USData/USMSMP](data-and-backtest.md).

## Account and orders

Select the intended 複委託 account with `api.set_SubAccount(account)`; this initializes `SubOrder` and `SubAccount`. API eligibility requires manual application through the account's sales representative. The following is an integration fragment, not authorization to trade:

```python
api.set_SubAccount(account)
api.SubOrder.set_event(on_order_event)  # callback accepts one event
trade = api.SubOrder.create_order(
    action=kgi.Action.Buy,
    symbol="AAPL",
    qty=4,
    price=230.0,
    currency=kgi.Currency.TWD,
    name="strategy-id",
)
```

| Input | Contract |
| --- | --- |
| `action`, `symbol`, `qty`, `price` | Required; `Buy`/`Sell`, symbol string, integer quantity, numeric price |
| `currency` | `kgi.Currency.TWD` or `kgi.Currency.MUT`; account report describes TWD as Taiwan dollars and MUT as foreign currency settlement; no default established in the parameter table |
| `name` | Strategy identifier |

Do not add Taiwan `odd_lot`, `order_cond`, `time_in_force` or a market-price enum to this signature. `Market.US` appears in returned objects; it is not a documented create input here.

| Method | Contract |
| --- | --- |
| `SubOrder.update_order(org_seqnum, price=..., qty=...)` | Supply exactly one of price or qty; qty is the reduction and cannot exceed remaining quantity. Modification deletes the old order and creates a new order |
| `SubOrder.cancel_order(org_seq)` | Cancel by original order identifier; preserve the documented parameter spelling or use positional form |
| `SubOrder.cancel_order_all()` | Account-wide cancellation; use only if all relevant orders are in authorized scope |
| `SubOrder.get_trades(full=False)` | Default active trades; `True` includes all tracked trades |
| `SubOrder.get_deals()` | Deal information grouped by symbol |
| `SubOrder.get_position()` | Position information |
| `SubOrder.contract(type="dic")` | US product catalog; `dic` or `df` |
| `SubOrder.set_event(callback)` | One event argument |

## Identity and state differences

`Trade` still contains `order`, `order_status`, `operations`, but its schema differs from Taiwan:

- `Order.org_seqnum`: original order identity for management; `Order.order_id`: order number after success. Preserve both.
- `Event.org_seqnum` corresponds to the original identity. The field table places `order_id` on `Task.Deal` and `seqno` on non-Deal events; do not require every field in every callback.
- Tasks listed: `NewOrder`, `UpdateQty`, `CancelOrder`, `Deal`. The update method documents a price input even though task tables omit `UpdatePrice`; do not invent a callback task sequence for price replacement.
- `OrderStatus.status` additionally lists `Status.PendingSubmitted` (預約單).
- `Operation.status` and `Event.status` may be `kgi.Status` **or strings**. Initial state is `Status.Pending`; examples also show `處理中`. Later strings include `預約單`, `委託上手中`, `委託成功`, `委託失敗`, `逾期單`, `作廢單`, `無效單`, `已下單至交易室`, `處理失敗`, `上手系統處理中`.
- Do not compare all US statuses only to `Status.Success`, use string truthiness as success, or equate `Submitted` with a fill. Preserve unrecognized values. Confirm fills from Deal events or execution reports.
- Track the original order, cancellation and replacement separately; a timeout does not prove either side failed. Do not replay an uncertain replacement.

## Accounting

Use `api.SubAccount` according to the accounting headings, examples and account initialization contract. The manual concatenates assignment and display text in places (`df=...()df`); split these into valid Python statements rather than copying that formatting.

| Method | Inputs | Useful returned fields |
| --- | --- | --- |
| `StockPositionReport()` | None | `symbol`, `symbol_name`, `market`, `currency`, `settle_currency`, `Qty`, `buyqty`, `market_price`, `close_date` |
| `DeliveryReport()` | None | `CustomerId`, `BS`, `TradeCurrency`, `SettleCurrency`, `Symbol`, signed `TotalAmt`, `Commission`, `CustodyFee`, `OtherFee` |
| `PositionDetailReport(currency)` | Currency string; omission queries all | `currency`, `balance_twd`, `pp1`–`pp5`, `pp6_twd`, `pp7_twd`, `pp8_twd` |
| `OrderReport()` | None | `seqnum`, `orig_seqnum`, `orderno`, `qty`, `replace_qty`, `price`, `replace_price`, `order_err_code`, `order_err_msg`, `sales_status`, `sales_status_code`, `exe_qty`, `exe_status_code` |
| `ExecReport()` | None | `orderno`, `symbol`, `trade_date`, `trade_type`, `exe_qty`, `exe_avg_price`, `exe_price`, `trade_currency`, `settle_currency` |

Note the distinct spellings `org_seqnum` (order/event) and `orig_seqnum` (account report). Report `exe_status_code` is 0=unfilled, 1=partial, 2=filled; `sales_status_code` is 0=reserved, 1=forwarding, 2=accepted, 3=failed, 4=expired, 5=voided, 6=invalid, 7=processing, 8=sent to trading desk, 9=processing failed, 10=upstream processing. Preserve source values alongside any application mapping.

The stock-position table has conflicting descriptions for `Qty` and `settle_currency`; do not infer units or meaning from those erroneous descriptions alone. Validate schema against the target public interface before calculations.
