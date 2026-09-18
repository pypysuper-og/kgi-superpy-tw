# Quote events and recovery

Source: v1.37 processed event sections (TOC 239, 259, 276), raw event sections (294, 312), status appendix (384–387). These are quote events, not order events.

## Processed Quote / USQuote / FutQuote

Use `set_cb_event(callback)` on the chosen facade. Callback receives one `kgi.Event` with `event_code` and `respond_code` as shown in the manual. Do not use order-event `task/status` or raw-event `status_code` here.

| `kgi.Event.event_code` members | Meaning |
| --- | --- |
| `CONNECTED`, `CONNECTING` | Connection state |
| `MANUAL_DISCONNECT`, `DISCONNECTED` | Intentional/unexpected disconnect context |
| `RECONNECTING`, `RECONNECTED`, `RECONNECT_FAILED`, `RECONNECT_MAX_REACHED` | SDK reconnect progress/terminal failure |
| `HEARTBEAT_TIMEOUT`, `WS_TIMEOUT`, `WS_ERROR` | Liveness or transport trouble |
| `SUBSCRIBE_REQUEST`, `SUBSCRIBE_OK`, `SUBSCRIBE_OK_KBAR`, `SUBSCRIBE_FAIL` | Subscription stages |
| `UNSUBSCRIBE_REQUEST`, `UNSUBSCRIBE_OK`, `UNSUBSCRIBE_FAIL` | Unsubscription stages |
| `BACKPRESSURE`, `CALLBACK_SLOW`, `DROPPED_MESSAGE`, `CALLBACK_EXCEPTION` | Consumer cannot keep up, data loss or callback failure |

Shown `kgi.Event.respond_code` members include `SUCCESSFUL_OPERATION`, `QUOTE_SERVER_UNKNOWN_ERROR`, `QUOTE_SERVER_TOO_MANY_CONNECTIONS`, `QUOTE_SERVER_INVALID_TOKEN`, `QUOTE_SERVER_NO_PERMISSION_SUBSCRIPTION`, `QUOTE_SERVER_INVALID_SYMBOL_SUBSCRIPTION`, `QUOTE_WS_SUBSCRIPTION_LIMIT_EXCEEDED`, `QUOTE_STATICDATA_KBAR_DUPLICATE_SUBSCRIPTION`. The numeric Q-code appendix is not proof that every enum has a particular raw numeric representation.

Diagnostic groups in the appendix:

| Codes | Investigate |
| --- | --- |
| Q001–Q005 | Missing/invalid subscription parameters |
| Q006–Q011 | Permission retrieval, HTTP/JSON, rule or subscription rejection |
| Q012–Q016 | Topic limit, duplicate ID, invalid quote type/ID/parameter |
| Q017–Q021 | Connection, JSON decode, reconnect/resubscribe failures, exhausted retries |
| Q022–Q027 | Callback exception, function, arity, type, quote type or version |
| Q028–Q033 | Data market/facade/property access |
| Q034–Q039 | Static-data HTTP/fetch/parse/empty response, periodic fetch, product parsing, unsubscribe format |
| Q040–Q043 | Unsupported K-bar minute, duplicate subscription, missing/invalid unsubscribe ID |
| Q044–Q045 | WebSocket error/closed |

## Raw SWQuote

Use `api.SWQuote.set_event(callback)`. Callback receives one `kgi.SWEvent`; inspect `event_code` and `status_code`. Event-code members shown: `CONNECTED`, `DISCONNECTED`, `LOGIN_OK`, `LOGIN_FAIL`, `CONTRACTS_READY`, `SUBSCRIBE_OK`, `SUBSCRIBE_FAIL`, `UNSUBSCRIBE_OK`, `UNSUBSCRIBE_FAIL`.

| Code | `kgi.SWEvent.status_code` member shown | Meaning |
| --- | --- | --- |
| SW000 | `SUCCESSFUL_OPERATION` | Operation success |
| SW001 | `SW_DISCONNECTED` | Connection ended |
| SW002 | `SW_LOGIN_FAILED` | Login failed |
| SW003 | `SW_SUBSCRIBE_FAILED` | Subscribe request failed |
| SW004 | `SW_SUBSCRIBE_REJECTED` | Subscribe rejected |
| SW005 | `SW_UNSUBSCRIBE_FAILED` | Unsubscribe failed |
| SW006 | `SW_SUBSCRIBE_LIMITED` | Subscription quota reached |
| SW007 | `SW_LOGIN_EXHAUSTED` | Attempt ended: eligible channels failed **or an account-level error stopped subsequent tries** |
| SW008 | `SW_LOGIN_NO_AUTH_SOURCE` | No usable authentication source |
| SW009 | `SW_LOGIN_NO_CHANNEL` | Server returned no channels |
| SW010 | `SW_LOGIN_MISSING_CREDENTIALS` | Empty identity/password |
| SW011 | Not established in example | Login not attempted because preconnection gate failed |

Do not interpret SW007 solely as network-channel exhaustion; its detailed appendix is broader than its example message. Preserve unknown codes and context; do not invent the SW011 enum name.

## Application recovery guidance

The manual shows quote resubscription on processed `Event.event_code.DISCONNECTED` or raw `SWEvent.status_code.SW_DISCONNECTED`. It also exposes SDK automatic-reconnect events. These examples do not prove lossless replay or a required additional application reconnect loop.

If implementing recovery, keep desired subscriptions separately from the currently reported subscriptions, including market, mode, odd-lot flag and K-bar period. Reconcile after reconnect using that facade's `get_subscriptions()`. Use one recovery owner with an explicit attempt/deadline budget; stop on manual disconnect, permission/credential problems, exhausted retry budget or subscription quota. Do not create multiple sessions to bypass quota.

Keep callbacks short: enqueue work, track callback failures/backpressure, and surface dropped data. The manual's inline sleeps are examples, not a requirement. Connection restored is not proof all subscriptions or missing ticks were recovered. Reconcile actual payload arrival and timestamps. A quote recovery must not replay trading orders.
