# Account query API

`api.Account` is initialized after `api.set_Account(account)`. Most results are pandas-style tables; `SettleAmtTrial` examples return grouped `Detail1`/`Detail2` results. Source: v1.37, TOC 148–173.

| Method | Inputs | Purpose |
| --- | --- | --- |
| `InventorySum(FType="A")` | `A` board lots; `B` shares | Aggregated securities inventory |
| `SettleAmtTrial(FType="D")` | `M`, `D`, `S`, `SS` | Current-day settlement trial; response can contain `Detail1` and `Detail2` |
| `SettleAmt(FType="SS")` | `S`, `S1`, `SS`, `SS1` | Three-day settlement amounts |
| `Inventory(FType="SS")` | `S`, `SS`, `M`, `M1`, `D`, `D1` | Inventory P/L and maintenance-rate trial |
| `RealizePL(FType="M", StartDate=None, EndDate=None)` | `M` summary / `D` detail; `yyyymmdd` | Realized P/L; default start is 30 days before end; default end is today |
| `SettleAmtDetail()` | none | Current non-day-trade settlement offset detail |
| `BalanceStatement(FType="M", StartDate=None, EndDate=None)` | `M` summary / `D` detail; `yyyymmdd`; omitted start equals end, omitted end is today | Account statement |
| `OrderReport()` | none | Order records, status, and errors |
| `ExecReport()` | none | Execution records |

```python
inventory = api.Account.InventorySum("B")
settlement = api.Account.SettleAmt(FType="SS")
realized = api.Account.RealizePL("D", "20260101", "20260131")
orders = api.Account.OrderReport()
fills = api.Account.ExecReport()
```

Key schema groups:

- Inventory: symbol/name, market, quantities by cash/margin/short/odd-lot, average price, market price, asset value, P/L.
- Settlement: trade and settlement dates, currency, receivable/payable amounts, trial/final marker.
- P/L and statements: trade date/type, symbol, quantity, price, amount, fee, tax, financing values, net amount, net P/L.
- Order report: `OrderNo`, `StockID`, `Side`, `Price`, `Qty`, `OrdLot`, `OrderFunc`, `OrdClass`, times, `ErrCode`, `ErrMsg`.
- Execution report: `OrderNo`, `StockID`, `Side`, `Price`, `DealQty`, class/lot/time fields, cumulative quantity.

## Query modes and precise field meanings

- `InventorySum`: A=lots, B=shares; one lot is 1000 shares in this report. This does not define every order or quote quantity unit.
- `SettleAmtTrial`: M=stock + transaction-type summary, D=detail, S=TWD summary excluding foreign currency, SS=account + currency summaries. Examples use `result['Detail1']` (settlement) and `result['Detail2']` (day-trade summary); return prose is inconsistent, so inspect the documented grouped result before calculations.
- `SettleAmt`: S/SS include today's provisional calculation; S1/SS1 put today's amount at zero until accounting closes. S/S1 return a TWD row; SS/SS1 return account/currency rows. That zero is not proof of no activity.
- `Inventory`: S=TWD account summary, SS=account/currency rows, M=stock/type subtotal, D=detail; M1/D1 separate margin/short positions and exclude cash stocks.
- Preserve method-specific casing: `Symbol`, `STOCK`, `StockID`, `BrokerID`, `BrokerId` are not interchangeable. Many numeric-looking columns are documented as object; validate conversion and retain source values and leading-zero identifiers.
- `OrderReport.OrderFunc`: I=new, C=quantity change, M=price change, D=cancel. `OrdLot`: 0=regular, 2=fixed price, 1=after-hours odd lot, 3=block, 4=intraday odd lot. These are report codes, not direct enum values.
- Reconciliation fields include `OrderNo`, `TradeDate`, `CNT`, `CNTN`, `BeforeQty`, `AfterQty`, `BeforeQtyN`, `AfterQtyN`, `ClientOrderTime`, `ClientOrderTimeN`, `ReportTime`, `ReportTimeN`, `ErrCode`, `ErrMsg`. `PriceFlagN`: 1=market, 2=limit.
- Empty reports, missing IDs and timeouts remain distinct from confirmed rejection. Do not infer a full order lifecycle from one report row.

## Official schema pages

- [InventorySum](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/accountInventorySum)
- [SettleAmtTrial](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/accountSettleAmtTrial)
- [SettleAmt](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/accountSettleAmt)
- [Inventory](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/accountInventory)
- [RealizePL](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/accountRealizePL)
- [SettleAmtDetail](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/accountSettleAmtDetail)
- [BalanceStatement](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/accountBalanceStatement)
- [OrderReport](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/accountOrderReport)
- [ExecReport](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/accountExecReport)
