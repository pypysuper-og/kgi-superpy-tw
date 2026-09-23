---
name: kgi-superpy-tw
description: Develop, explain, review, and debug KGI SuperPy (kgisuperpy) integrations and trading application UI/UX for Taiwan stocks, US sub-brokerage, domestic futures/options, and overseas futures/options. Use for SuperPy, kgisuperpy, KGI Python API, 凱基 Python API, and related trading workflows or workbench design; not for unrelated UI design or strategy profitability advice.
metadata:
  version: "1.37.7"
---

# KGI SuperPy API

This is a community-maintained skill, not an official KGI product. Use the references summarized from **凱基 Python API 使用手冊 v1.37** as the versioned baseline; the original manual and SDK are not bundled. The identifier `kgi-superpy-tw` is retained for existing invocations; coverage includes all four markets.

## Choose the market before the API

| Market | Account selection | Trading / accounting | Quotes / data | Read |
| --- | --- | --- | --- | --- |
| Taiwan securities | `set_Account(account)` | `Order` / `Account` | `Quote`, `SWQuote`, `Data`, `MSMP` | [orders](references/orders.md), [accounts](references/accounts.md) |
| US sub-brokerage | `set_SubAccount(account)` | `SubOrder` / `SubAccount` | `USQuote`, `USData`, `USMSMP` | [US stocks](references/us-stocks.md) |
| Domestic futures/options | `set_FutAccount(account)` | `FutOrder` / `FutAccount` | `FutQuote`, `SWQuote`, `Data` | [domestic futures](references/domestic-futures.md) |
| Overseas futures/options | `set_OvfutAccount(account)` | `OvfutOrder` / `OvfutAccount` | No overseas quote/data facade established here | [overseas futures](references/overseas-futures.md) |

All facade names are on `api`. Do not construct names by analogy. Read only the relevant market and operation references.

## Reference routing

- Installation, eligibility, CA, simulation, login, account selection and logout: [session](references/session.md).
- Designing or improving a SuperPy Web UI or trading workbench: [trading application UX](references/trading-uiux.md). Start with fixed workspace and tabs/dialogs, login and shutdown journeys, distinct connection/account indicators and reconnect feedback, contextual help dialogs, auditable operations, and dynamic latest-trade display when login and subscriptions are available. Treat colors, typography and example geometry as replaceable styling; preserve the user's strategy, execution policy and platform. A small API script does not need a workbench.
- Implementing OCO-specific persistent units, inventory reconciliation or reminder behavior in a local Web application: [Web OCO application example](references/web-oco-application.md). Its OCO and execution rules are examples, not defaults for other strategies or official SDK contracts; shared login, shutdown and layout requirements live in the UX guide.
- Correlated operation/result logs, hidden-launch diagnostics, support bundles and agent troubleshooting: [diagnostics and support](references/diagnostics-support.md).
- Taiwan acknowledgement latency, pending-only diagnosis and SDK logging: [order lifecycle](references/order-lifecycle.md). Historical cases and field mappings are Taiwan-specific.
- Quote methods, payloads, subscription keys and quotas: [quotes](references/quotes.md).
- Quote event enums, error codes and bounded recovery: [quote events](references/quote-events.md).
- Historical data, MSMP conversion, freshness and backtesting: [data and backtest](references/data-and-backtest.md).
- Source identity, manual section locators and contradictions: [manual baseline](references/manual-baseline.md).
- Original Taiwan website links for refresh: [official index](references/official-index.md).

Answer in the user's language while preserving API spelling and dataset names exactly. Consult the baseline when a signature, enum, version or example conflicts.

## Development invariants

- Use documented public methods, parameters, enums and lifecycle order. Do not invent fallback calls or infer input parameters from returned fields. Private SDK internals, `repr(api)`, `print(api)` and `api._ObjOrder.FIsLogon` are not documented login checks. The documented backtest parameter `_maxtrades` is an explicit exception to the underscore naming heuristic.
- `kgi.login(person_id, person_pwd, simulation=True)` selects simulation by default; `False` selects production. US simulation is explicitly unavailable in this manual despite generic test text. Never silently switch a test to production.
- This skill authorizes no brokerage effects. Require current explicit authorization before production login or live order/create/update/cancel operations; login-only authorization does not authorize an order. Reuse already-granted scope. Use placeholders or secure runtime input; do not retain credentials or private SDK logs in skill artifacts.
- Select the intended account from `show_account()` using account identity and market. Do not choose the first account or infer a broker route from an undocumented flag.
- Register the relevant order callback before submitting. A returned `Trade`, pending operation, acknowledged new order and fill are distinct observations. On an unknown outcome, reconcile using that market's reports; do not resend automatically.
- `update_order(..., qty=N)` reduces quantity by N, not to N. Supply either price or qty, not both, and do not reduce beyond the remaining quantity. US modification is cancel-and-replace; preserve both operation histories.
- Quantity and identifier semantics differ by market and surface. Do not transfer backtest share quantities into Taiwan lot orders, US `org_seqnum` into Taiwan order IDs, or a futures quote alias into a dated trading contract.
- Processed quote events, `SWQuote` events and order events have different fields. Raw `SWMarketData.data_type` identifies the updated group; other values may be stale from the prior update.
- Read exact dataset names and arguments from the appropriate `get_table()` catalog. Historical update schedules are expected processing times, not proof of freshness or an SLA.
- Keep documented behavior, document contradictions, version-specific runtime evidence and user-confirmed experience separate. The one-day account-processing observation remains in [session](references/session.md). For a current/latest claim, verify the official source and installed version.

## Documentation baseline

Revision `1.37.7` centers the Web guidance on six user-facing workflows: workspace organization, login/shutdown, session and reconnect feedback, contextual help, auditable lifecycles, and latest-trade display from verified subscriptions. This is design guidance, not a shipped Web application or evidence of live market-data integration.

Revision `1.37.5` adds strategy-independent trading UI/UX patterns and extends the OCO case with separate execution and reminder states. These are application design recommendations, not new SDK guarantees. The manual baseline remains v1.37, reviewed on 2026-09-16. Its release section lists SDK V2.1.2 (2026-09-15), including Python 3.14 support, although the filename ends in `_20260902`. This is a document baseline, not an SDK installation or live compatibility test. See [source identity and conflicts](references/manual-baseline.md).
