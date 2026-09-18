# Taiwan order lifecycle and diagnostic evidence

Use for order tests, acknowledgement latency, missing callbacks, or reconciliation.
Official pages below were checked on 2026-09-05. The observed case uses kgisuperpy
2.1.1; distinguish its diagnostics from the documented public API contract.

The v1.37 manual confirms the Taiwan object/event distinctions below; the pending-only incident remains a historical 2.1.1 observation. US and futures workflows must use their own market references.

## Official lifecycle

After documented login/CA completion and `api.set_Account(account)`, register
`api.Order.set_event(callback)` before the order operation. The callback accepts
one `Event`. The official example registers it before `create_order`; without
registration, the documented default is to print complete events.

`create_order` returns a `Trade` with `order`, `order_status`, and `operations`.
These objects allow subsequent state inspection; freeze snapshots at capture time
because keeping a reference alone does not preserve the earlier state.

| Observation | Meaning and limit |
| --- | --- |
| Method returned a Trade | Method-return evidence; not acknowledgement or fill proof |
| Operation `Pending` | Official wording: system received the request but processing is unfinished; the documentation does not identify the acknowledged system layer precisely enough to prove exchange receipt |
| Event `NewOrder/Success` | New-order operation succeeded; distinguish from a Deal event |
| Event/Operation `Failed` | Operation failed; capture `msg` when supplied |
| `order.order_id` | Officially populated after successful order placement |
| `order_status.status` | Submitted, Filled, PartFilled, Cancelled or PartFilled_Cancelled; distinct from operation Pending/Success/Failed |
| `Task.Deal` or `OrderStatus.deals` | Execution evidence; Deal fields are price, quantity, ts and reportseq |

Capture operation `nid`, task, status, op_time and msg, and event task, status,
order_id, seqno, action, symbol, quantity, price, order_cond, time_in_force,
odd_lot, ts and msg. Keep null/missing values unknown rather than inventing a status.

For event attribution use documented IDs: Event.order_id corresponds to Order.order_id;
Event.seqno corresponds to Operation.nid. Normalize string/integer representations
without converting identifiers to floating point. Do not assume a sequence value
stays identical across all stages: the official Pending and Success examples show
different sequences. Preserve all operation IDs and event records. Symbol and
quantity alone do not identify a particular order.

## Measuring acknowledgement

- Record `perf_counter_ns()` immediately before the operation and at method return.
- Timestamp at callback entry, before formatting, file I/O and matching. Handle a
  callback arriving before the method returns; buffer it for later correlation.
- Report method-return latency, correlated NewOrder/Success latency and correlated
  NewOrder/Failed latency separately. Missing callback means no callback latency,
  not a successful order taking exactly the timeout duration.
- State a finite observation window. An application event deadline does not impose
  a timeout on a synchronous SDK call. No-event, uncorrelated-event, exception and
  confirmed failure are different outcomes; do not automatically resend on unknown.
- File logging can affect subsequent scheduling. This measures instrumented local
  application latency, including SDK/network/server work, not pure network latency.
  One order is one sample, not a benchmark distribution.

## Official query surfaces

| Surface | Use |
| --- | --- |
| `api.Account.OrderReport()` | Order records including OrderNo, OrderFunc, CNT/CNTN, TradeDate, ClientOrderTime/ClientOrderTimeN, ReportTime/ReportTimeN, BeforeQty/AfterQty, PriceFlagN, ErrCode and ErrMsg |
| `api.Order.get_trades(True)` | All tracked trades; documented as dictionary keyed by order_id |
| `api.Order.get_trades(False)` | Trades still in the market |
| `api.Account.ExecReport()` | Execution records, order number, filled quantity/price and timestamps |
| `api.Order.get_deals()` | Current-day execution Event lists grouped by symbol |

For a before/after test, preserve a baseline OrderReport and a final report after
the bounded observation, including failure/no-event paths when the process and SDK
remain usable. Keep queries outside the order-timing interval. Compare rows while
preserving duplicate counts. New/changed rows can reflect other account activity;
attribute by IDs rather than treating every difference as this order's success.
An unsuccessful baseline is unknown, not an empty table. Empty reports alone do
not prove that a request was rejected, never delivered or cannot execute later.

The reviewed current Taiwan public documentation did not expose a direct query by
requestID/nid, forced status refresh, or callback replay method. Do not import the
older `superpy.place_order/update_status` interface into the current `kgisuperpy`
contract. Likewise, US/futures report status definitions are not Taiwan definitions.

## Native SDK logs and observed container shape

The official FAQ identifies `kgisuperpy/pushClient` and `kgisuperpy/log` as log
locations for support. Inspect the actual installed package under the selected
virtual environment: capturing stdout/stderr alone may miss native log files.
Match run times/request IDs, preserve original evidence, and redact credentials,
account identifiers, IPs, certificate/signature material before sharing. A native
Send record proves that code reached a logged send path, not remote acknowledgement.
An errMsg.ini entry is dictionary text, not evidence that the error occurred.

Observed on 2026-09-05 with 2.1.1: `get_trades(True)` returned `{'無效單': []}`.
This is not the simple dict[str, Trade] shape shown in the public reference. For
diagnostic capture preserve nested dict/list/tuple containers and actual Trade
items; keep an unknown leaf's type and diagnostic representation rather than a
fabricated null-filled Trade. Separate dictionary-entry count, actual Trade count
and unparsed-item count. An empty invalid-order category contains zero orders and
is not rejection evidence. Raw repr is diagnostic only, not trading application logic.

## Boundaries learned from the pending-only case

A production test with Common/CASH/ROD returned NewOrder/Pending but received no
callbacks in 30 seconds, had no order_id or msg, and returned empty before/after
reports and no active trades. A native log contained the order's Send record.
This establishes an unresolved pending-only observation, not its cause. It does
not establish that weekends or quantities cause silent rejection. Deal queries
were identified as additional surfaces but were not executed in that case.

Quantity: the current create_order table says only "stock quantity". Its successful
Common examples use small qty values (including qty=1 in the service-terms example),
consistent with board-lot units. Do not change qty=1 to 1000 merely because one lot
equals 1000 shares. Keep this example-supported interpretation distinct from an
explicit unit guarantee; clarify with the provider when the decision depends on it.

Preorders: no explicit prohibition or guarantee for current Taiwan production
weekend/preorders was found in the reviewed documents. The business-day
08:30-to-next-day-05:00 service window is under simulation/testing terms. Older
1.0.4 documentation lists PreSubmitted but uses a different interface, and cannot
establish 2.1.1 behavior. Keep this compatibility question unresolved.

## Sources

- [Create](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/orderCreate)
- [Trade](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/tradeObject)
- [Event](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/eventObject)
- [Callback](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/orderSetEvent)
- [Tracked trades](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/orderGetTrades)
- [Order report](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/accountOrderReport)
- [Execution report](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/accountExecReport)
- [Deal events](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/orderGetDeals)
- [FAQ/log locations](https://superpy.kgieworld.com.tw/kgipythonapi/faq)
- [Service terms](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/terms)
- [Historical 1.0.4 interface, not current API authority](https://pypi.org/project/kgisuperpy/1.0.4/)
