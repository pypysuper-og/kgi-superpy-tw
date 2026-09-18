# Manual baseline and source conflicts

## Source identity

- Source document: `凱基Python API 使用手冊v1.37_20260902.docx`. The original document is not redistributed in this repository; consult KGI for the manual applicable to your SDK.
- Cover: Version 1.37, Sep 2026. Reviewed 2026-09-16.
- SHA-256: `903d75f9e1a18962002c0fa361e58331b8b31d982d6492d7bf37de10489fab99`.
- Release section: V2.1.2 (2026/09/15), Python 3.14 support; V2.1.1 (2026/08/27), fixes and membership adjustments.
- Original skill: Taiwan website snapshot from 2026-09-04; diagnostics supplemented on 2026-09-05. Historical observations remain labeled.

The filename date is not the latest content date. References summarize actionable contracts rather than duplicate the manual. Locators below are the manual's own TOC page labels, not freshly rendered pagination.

## Section lookup

| Topic | Manual TOC pages | Skill reference |
| --- | --- | --- |
| Membership, setup, terms, login, accounts | 7–26 | [session](session.md), [quotes](quotes.md) |
| Taiwan orders, Trade and Event | 27–59 | [orders](orders.md), [lifecycle](order-lifecycle.md) |
| US orders, Trade and Event | 60–90 | [US stocks](us-stocks.md) |
| Domestic futures orders, Trade and Event | 91–114 | [domestic futures](domestic-futures.md) |
| Overseas futures orders, Trade and Event | 115–147 | [overseas futures](overseas-futures.md) |
| Taiwan / US / domestic / overseas accounting | 148–173 / 174–184 / 185–206 / 207–226 | Respective market references |
| Processed Taiwan / US / futures quotes | 227–247 / 248–267 / 268–284 | [quotes](quotes.md), [events](quote-events.md) |
| Raw Taiwan / domestic futures quotes | 285–301 / 302–319 | [quotes](quotes.md), [events](quote-events.md) |
| Taiwan / US / futures historical data | 320–338 / 339–352 / 353–359 | [data and backtest](data-and-backtest.md) |
| Backtest and results | 360–383 | [data and backtest](data-and-backtest.md) |
| Quote status codes; SDK versions | 384–388 | [events](quote-events.md), this file |

## Conflicts affecting generated code

| Location | Conflict or gap | Handling |
| --- | --- | --- |
| US service terms | Says no US simulation, then includes generic simulation text | Do not promise simulation or automatically fall back to production |
| Python requirements | US table says 3.09–3.13; later version check and V2.1.2 release say 3.14 | Attribute 3.14 to V2.1.2; verify platform/package compatibility separately |
| Futures action tables | `Action.BUY`/`SELL`; code and object tables use `Action.Buy`/`Sell` | Use example/object spelling; do not assert uppercase aliases exist |
| Overseas facade spelling | Prose uses `OvFutOrder`/`OvFutAccount`; executable calls use `OvfutOrder`/`OvfutAccount` | Use executable spelling |
| Overseas update/cancel | Parameter `order_id`, but example argument resembles `Operation.nid` and differs from successful event's `order_id` | Preserve both IDs; resolve accepted identifier before live mutation; never guess or try both |
| Domestic account queries | Says no arguments, but lists `MType` without supported values | Use no-arg examples; do not invent `MType` values |
| US snapshots | `get_snapshots('AAPL','TSM')` example conflicts with list-of-strings parameter table | Resolve before implementing; neither a keyword name nor list/varargs signature is proven by both |
| US K-bar | Symbol-only example/table; Taiwan exposes `minute` | Do not copy Taiwan's minute argument or intervals |
| Processed callbacks | Heading `Quote.set_cb`; examples use type-specific setters | Use `set_cb_tick`, `set_cb_bidask`, `set_cb_kbar`; no invented generic `set_cb` or `set_cb_all` |
| `subscribe_all` | Combined payload documented; all-callback setter absent in shown sections | Keep callback registration unresolved |
| Raw timestamp | Table says `HHMMSSSSS`; examples show `HH:MM:SS.mmm` | Preserve representation; validate parser against target version |
| `SettleAmtTrial` | Return prose says DataFrame; examples index `Detail1` and `Detail2` | Respect grouped example result; do not assume all account results are one DataFrame |
| Taiwan day-trade enums | Object tables add `MARGIN_DayTrade`/`SHORT_DayTrade`; create input table omits them | Output decoding does not establish accepted create inputs |
| Backtest `qty` | Type says int; description and examples use column name | Supply quantity column name |
| Dashboard `view` | Example `notebook`, table `Notebook` | Do not assert both cases work; verify if this output mode matters |

Examples also contain smart quotes, mismatched outputs and stale contracts. Rewrite as valid Python, sanitize identifiers, and check syntax offline. Manual examples are not live test receipts. Stop only an affected unresolved call; continue unaffected work.
