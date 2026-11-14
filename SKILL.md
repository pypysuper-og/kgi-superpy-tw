---
name: kgi-superpy-tw
description: Develop, explain, review, and debug KGI SuperPy (kgisuperpy) integrations, application state/module interactions, and trading UI/UX for Taiwan stocks, US sub-brokerage, domestic futures/options, and overseas futures/options. Use practical cases and engineering guidance for requirements, capability discovery, debugging, verification and delivery; compare brokerage APIs and create technical notes when requested. Use for SuperPy, kgisuperpy, KGI Python API, 凱基 Python API and related trading workflows; not for unrelated UI design, general broker rankings, or strategy profitability advice.
metadata:
  version: "1.38.0"
---

# KGI SuperPy API

This is a community-maintained skill, not an official KGI product. Use the relevant development references alongside the official website and evidence from the target SDK version. Reference notes are not a guarantee of current compatibility; follow [source verification](references/source-verification.md) when a contract needs confirmation. The identifier `kgi-superpy-tw` is retained for existing invocations; coverage includes all four markets.

## Choose the market before the API

| Market | Account selection | Trading / accounting | Quotes / data | Read |
| --- | --- | --- | --- | --- |
| Taiwan securities | `set_Account(account)` | `Order` / `Account` | `Quote`, `SWQuote`, `Data`, `MSMP` | [orders](references/orders.md), [accounts](references/accounts.md) |
| US sub-brokerage | `set_SubAccount(account)` | `SubOrder` / `SubAccount` | `USQuote`, `USData`, `USMSMP` | [US stocks](references/us-stocks.md) |
| Domestic futures/options | `set_FutAccount(account)` | `FutOrder` / `FutAccount` | `FutQuote`, `SWQuote`, `Data` | [domestic futures](references/domestic-futures.md) |
| Overseas futures/options | `set_OvfutAccount(account)` | `OvfutOrder` / `OvfutAccount` | No overseas quote/data facade established here | [overseas futures](references/overseas-futures.md) |

All facade names are on `api`. Do not construct names by analogy. Read only the relevant market and operation references.

## Reference routing

- Installation, eligibility, CA, simulation, login, account selection and logout: [session](references/session.md). For Taiwan startup, usage-flow diagrams or workflow reference notes, read its [Taiwan workflow](references/session.md#tw-workflow): separate account inspection from account selection, account queries from trading callbacks, and normal use from reconnect/logout.
- Designing or improving a SuperPy Web UI or trading workbench: [trading application UX](references/trading-uiux.md). Start with fixed workspace and tabs/dialogs, login and shutdown journeys, distinct connection/account indicators and reconnect feedback, contextual help dialogs, auditable operations, and dynamic latest-trade display when login and subscriptions are available. Treat colors, typography and example geometry as replaceable styling; preserve the user's strategy, execution policy and platform. A small API script does not need a workbench.
- Implementing OCO-specific persistent units, inventory reconciliation or reminder behavior in a local Web application: [Web OCO application example](references/web-oco-application.md). Its OCO and execution rules are examples, not defaults for other strategies or official SDK contracts; shared login, shutdown and layout requirements live in the UX guide.
- Substantive application design, state ownership, cross-module interactions, or a practical failure case: [practical development index](references/practical-development.md) and its [state/module model](references/application-state-models.md). Select only the relevant case: [delayed US identity](references/cases/us-delayed-identity.md), [cancel with late fill](references/cases/oco-cancel-late-fill.md), or [observation before exit eligibility](references/cases/observe-before-eligibility.md). These are application patterns and synthetic seams, not new SDK contracts.
- When a material assumption, product intention or verification decision needs a useful engineering second look: [human-agent development partner](references/human-agent-development.md). Its questions support the current developer's decisions; a short script or mechanical edit keeps its direct path. For material requirements or a capability, debugging, verification or delivery seam in that integration, select the relevant part of [integration engineering decisions](references/integration-engineering-workflow.md); its optional tools do not create new dependencies or phases.
- Frontend design choices and their evolution across grid and position-monitoring examples: [frontend evolution](references/frontend-evolution.md), alongside the existing UX contracts. Use it for progressive disclosure, asynchronous progress, bubble/list projections, recovery messages and isolated original-UI demonstrations.
- Choosing replay boundaries, interpreting synthetic versus live evidence, or evaluating skill changes: [testing and replay](references/testing-and-replay.md). The first edition includes offline teaching models and a fixed decision benchmark; neither certifies a trading application.
- Correlated operation/result logs, hidden-launch diagnostics, support bundles and agent troubleshooting: [diagnostics and support](references/diagnostics-support.md).
- Taiwan acknowledgement latency, pending-only diagnosis and SDK logging: [order lifecycle](references/order-lifecycle.md). Historical cases and field mappings are Taiwan-specific.
- US sub-brokerage missing identifiers, empty cache states, rejection scenarios, automatic/manual reconciliation, fill-time quality, settlement changes, cancellation confirmation and explicit user retries: [US order diagnostics](references/us-order-diagnostics.md). Distinguish callback, SDK cache, broker reports and the application's ledger; read this reference for callback-driven Trade updates and why no source is unconditionally the newest.
- Quote methods, payloads, subscription keys and quotas: [quotes](references/quotes.md).
- Comparing another brokerage API with SuperPy, finding equivalent fields across multiple methods, or turning findings into technical notes: [API comparison and technical notes](references/technical-notes.md). Keep a comparison-only answer in chat; create HTML/PDF when requested. Reference notes use concise, descriptive Traditional Chinese, highlighted Python and official links; HTML flow nodes link to the relevant document sections, with PDF destinations checked after export.
- Quote event enums, error codes and bounded recovery: [quote events](references/quote-events.md).
- Historical data, Taiwan index dataset/symbol differences, MSMP conversion, freshness and backtesting: [data and backtest](references/data-and-backtest.md).
- Source selection, version-specific evidence and unresolved contracts: [source verification](references/source-verification.md).
- Original Taiwan website links for refresh: [official index](references/official-index.md).

Answer in the user's language while preserving API spelling and dataset names exactly. Verify the affected signature, enum or version when sources conflict; do not invent a resolution or describe unverified material as publicly documented.

## Practical engineering partner

For material SuperPy design, debugging and acceptance decisions, quietly apply these case-derived prompts within the current work; surface a short suggestion when it changes the next useful action:

- Start from the intended user result and the confirmed missing-data policy. Ask what a guard actually protects and whether its field is direct evidence. Preserve already confirmed fills; when continued observation is part of the agreed job, gate the new effects that depend on missing data. Establish the behavioral change and its existing authority before moving a guard; ask only if a material product or authority decision remains unresolved.
- When facts conflict with presentation, an effect relies on indirect evidence, or a requested design crosses modules, locate the affected facts, intent, eligibility, effect progress and projection owners. Inspect only the quantities, reservations, time or generations that govern that transition, and preserve the developer's confirmed position/cost policy.
- Follow the real input-to-result path and its continuation: reconnect must restore monitoring, and an operation demonstration must exercise maintained controls. Validate the cheapest meaningful counterexample and a valid continuation.
- Prefer the smallest coherent change. Localize a safely identifiable conflict to its real dependents, retain shared-resource guards, and preserve existing authorization and user stops. A justified no-change decision is useful.

Use these as situational judgment, not a mandatory checklist, persona impersonation, extra agent call, new approval loop or full state inventory. Ask only for material unresolved product/authority choices; investigate engineering facts directly. Details and example prompts are in the [development partner guide](references/human-agent-development.md).

## Development invariants

- Use documented public methods, parameters, enums and lifecycle order. Do not invent fallback calls or infer input parameters from returned fields. Private SDK internals, `repr(api)`, `print(api)` and `api._ObjOrder.FIsLogon` are not documented login checks. The documented backtest parameter `_maxtrades` is an explicit exception to the underscore naming heuristic.
- `kgi.login(person_id, person_pwd, simulation=True)` selects simulation by default; `False` selects production. The [US service terms](https://superpy.kgieworld.com.tw/kgipythonapi/guide/us/terms) state that US simulation is unavailable. Never silently switch a test to production.
- This skill authorizes no brokerage effects. Require current explicit authorization before production login or live order/create/update/cancel operations; login-only authorization does not authorize an order. Reuse already-granted scope. Use placeholders or secure runtime input; do not retain credentials or private SDK logs in skill artifacts.
- Select the intended account from `show_account()` using account identity and market. Do not choose the first account or infer a broker route from an undocumented flag.
- Register the relevant order callback before submitting. A returned `Trade`, pending operation, acknowledged new order and fill are distinct observations. On an unknown outcome, reconcile using that market's reports; do not resend automatically.
- Treat reconnect as workflow recovery, not just a successful `api.login()`: restore the exact account, callbacks, required quote subscriptions or polling, fresh-data eligibility, order/fill tracking, and the previously enabled monitoring/evaluation loop. Under an existing automatic-resume agreement, reconcile automatically and restore eligible strategies without another confirmation; retain user stops and remaining limits, and isolate unresolved differences. See [workflow recovery](references/trading-uiux.md). These are application responsibilities, not SDK guarantees.
- `update_order(..., qty=N)` reduces quantity by N, not to N. Supply either price or qty, not both, and do not reduce beyond the remaining quantity. US modification is cancel-and-replace; preserve both operation histories.
- Quantity and identifier semantics differ by market and surface. Do not transfer backtest share quantities into Taiwan lot orders, US `org_seqnum` into Taiwan order IDs, or a futures quote alias into a dated trading contract.
- Keep Taiwan whole-lot and intraday odd-lot strategy data and orders separate through monitoring, reminders, exit and recovery. Use the strategy's own trading mode, not the currently selected UI product; never substitute another mode's quote when data is missing. See [quote separation](references/quotes.md#keep-taiwan-whole-lot-and-intraday-odd-lot-data-separate) and [orders](references/orders.md).
- Processed quote events, `SWQuote` events and order events have different fields. Raw `SWMarketData.data_type` identifies the updated group; other values may be stale from the prior update.
- Read exact dataset names and arguments from the appropriate `get_table()` catalog. Quote/Order product catalogs do not define the entire Data/index universe, and a Data symbol does not establish Quote acceptance. MSMP table names are not subscription symbols. Historical update schedules are expected processing times, not proof of freshness or an SLA.
- Keep documented behavior, document contradictions, version-specific runtime evidence and user-confirmed experience separate. The one-day account-processing observation remains in [session](references/session.md). For a current/latest claim, verify the official source and installed version.

## Documentation baseline

Revision `1.38.0` extends the engineering partner with on-demand integration guidance for requirements, existing provider capabilities, data consumers, debugging, verification, recovery and delivery. Optional tool and skill selection preserves a direct path when those capabilities are absent or unnecessary. Twelve prospective evaluation cases cover the new decisions and non-trigger controls; they have not been run as an AI comparison. Existing historical scores apply only to their original candidates. This revision changes no SDK contract or brokerage authorization.

Revision `1.37.17` removes nonpublic source metadata, adds source-verification guidance, and preserves the README's established layout and slogan while integrating practical development topics. Existing evaluation results identify their original candidates; they are not a behavioral evaluation of this revision.

Revision `1.37.16` adds a Taiwan/US practical edition covering state/module interactions, three complete case explanations with standard-library synthetic models, an implicit engineering-partner guide, frontend evolution patterns and a fixed before/after decision evaluation. Scope and evidence limits accompany each case. This is local development knowledge, not an SDK update, a trading application release or a live-broker certification; evaluation results are recorded separately in [the evaluation note](evals/evaluation.md).

Revision `1.37.15` adds the publicly documented historical minute-bar dataset that includes Taiwan indices and separates Data symbols from Quote/Order products and MSMP tables. Dated SDK 2.1.2 observations confirm Y9999/OTC99 daily-history retrieval, distinguish empty latest-day index results from a nonempty stock control, and record historical-minute access denial for all tested symbols. Historical retrieval, latest-trading-day data and streaming subscriptions require separate evidence; these observations are not a general entitlement or service guarantee.

Revision `1.37.14` adds a concise Taiwan startup and session workflow with official links, account-query and trading-callback branches, reconnect responsibilities, and logout semantics. Reference-note guidance uses descriptive prose and connects HTML flow nodes to their explanations, preserving internal destinations in requested PDF exports. These are documentation and authoring improvements, not new SDK capabilities or live trading evidence.

Revision `1.37.13` adds a source-grounded workflow for comparing brokerage API capabilities and producing concise SuperPy technical notes. It separates semantic equivalence from method-name similarity, documented contracts from SDK/Server/runtime evidence, and research findings from the requested HTML/PDF content. This is authoring guidance, not a new SDK capability.

Revision `1.37.12` clarifies SDK 2.1.2 callback-driven Trade updates, Pending events that leave aggregate status unchanged, and execution events without a matched Trade. It distinguishes cached objects from queried report snapshots: neither source nor arrival order alone establishes freshness, and calling OrderReport is not a promise to refresh Trade objects.

Revision `1.37.11` defines reconnect completion across account selection, callbacks, subscriptions, fresh quote consumption, reconciliation and previously enabled strategy evaluation. It separates login recovery from usable market data and resumed monitoring, preserves existing continuation authority and limits, and clarifies that an empty SDK Trade status is an in-memory observation, not a broker rejection. This is implementation guidance, not evidence that an application or live broker has passed these recovery scenarios.

Revision `1.37.10` expands the US diagnostic workflow with full-report fallback for matched orders whose SDK cache status is empty, evidence-based rejection handling, automatic versus manual pairing, confirmed fills with uncertain dates, editable settlement snapshots and report provenance. It includes a sanitized reserve-failure case without treating it as a universal error-code interpretation. These are application design references, not bundled executable trading features.

Revision `1.37.9` adds US order diagnostics: asynchronous Trade identity, full broker order reports, error messages and `errMsg.ini`, unresolved cancellation at shutdown, and guarded explicit retries. SDK implementation observations are version-specific to 2.1.2; these instructions do not establish live-broker verification.

Revision `1.37.8` integrates Taiwan whole-lot/odd-lot source and order separation with Windows windowless startup guidance. Local Web entrypoints should leave no persistent console, preserve streamed login feedback and sanitized audit, and expose startup failures. This is application guidance, not a bundled launcher or live-broker certification.

Revision `1.37.7` centers the Web guidance on six user-facing workflows: workspace organization, login/shutdown, session and reconnect feedback, contextual help, auditable lifecycles, and latest-trade display from verified subscriptions. This is design guidance, not a shipped Web application or evidence of live market-data integration.

Revision `1.37.6` makes Taiwan whole-lot/odd-lot separation explicit across quote caches, strategy cards, monitoring and exit orders. Revision `1.37.5` added strategy-independent trading UI/UX patterns and the OCO reminder case. These are application design recommendations, not new SDK guarantees. Check the [official release page](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/version) and target environment for SDK compatibility; source and evidence boundaries are in [source verification](references/source-verification.md).
