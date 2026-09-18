# Session and environment API

Source: v1.37, TOC 9–26; see [manual baseline](manual-baseline.md) for version conflicts.

## Environment contract

- Package: `kgisuperpy`
- Install command: `python -m pip install kgisuperpy`
- Documented Python: 64-bit Python 3.9 through 3.14 in the Taiwan/futures requirements. The manual attributes 3.14 support to SDK V2.1.2; the US table still says 3.13 but its later version check says 3.14. Verify the installed SDK/platform instead of treating this as a runtime test
- Documented Windows: 64-bit Windows 10 or later
- Documented Linux: Red Hat 7 or Ubuntu 20 or later, with KGI `libCGCrypt.so` and certificate utility installed
- Production use requires a KGI account, API eligibility, accepted service documents, and an active CA certificate.
- Taiwan securities simulation: business days 08:30 through 05:00 the next day. Futures simulation: business days 10:00–22:00. These are test-service windows, not production exchange hours.
- The testing terms specify Taiwan-only IP during 08:00–20:00; they do not establish access permissions outside that interval.
- US stocks: the manual explicitly says simulation is not offered. Generic testing paragraphs that follow do not override that statement. Never switch to production merely to make a test work.
- Testing instructions say to separate stock, futures and sub-brokerage accounts and keep order-test intervals greater than one second. This is a documented test condition, not an established universal production rate limit.
- Sub-brokerage API eligibility requires manual application through the sales representative; do not assume securities API activation enables every market.
- The official terms conditionally say that users with functional-testing needs can apply to a relevant KGI unit for a test account. This is not stated as a universal requirement for simulation use.
- The public documentation does not name that unit, provide a test-account application method, or state whether production credentials can be used in simulation. Keep these points unknown rather than inferring them.

## CA setup details

Windows: use the provider certificate component, apply for the certificate, then its certificate environment checker. Linux: install `libCGCrypt.so` with executable permissions in the distribution-appropriate library directory and run the provider `KGI_CGCrypt genDat` utility; the manual identifies `CGSetCertConfig [ 0 ]` as certificate installation success. Certificate installation success is separate from API login success. Renewal instructions remove the old certificate before reinstalling; do not delete a working certificate without explicit scope and a recoverable replacement.

## Account activation and processing delay

Account activation may be followed by platform account-information processing (帳戶資訊過檔). A reported case required waiting until the next day. Completing the application or local certificate setup does not imply immediate platform account readiness.

Source and scope: a community-reported case dated 2026-09-05 attributed the preceding day's login failure to account processing and reported a successful next-day login/CA sequence. Its private login artifacts are not distributed here, so readers cannot independently verify that case from this repository. It is not a waiting-period statement verified in the public guide.

The exact batch cutoff, whether “one day” means a calendar or business day, and a guaranteed 24-hour completion time are unspecified. Do not invent those details or generalize this case into a diagnosis for every login failure. Readiness is still confirmed using the official success sequence below.

## Login

```python
import kgisuperpy as kgi

api = kgi.login(person_id, person_pwd, simulation=True)
```

| Parameter | Type | Meaning |
| --- | --- | --- |
| `person_id` | `str` | User identity number |
| `person_pwd` | `str` | Account password |
| `simulation` | `bool` | `True` for simulation; `False` for production; default `True` |

Both environments use the documented `person_id` and `person_pwd` login parameters; simulation is not documented as anonymous or login-free.

## Official production and CA login confirmation

For production, call only the documented login entry point:

```python
api = kgi.login(person_id, person_pwd, simulation=False)
```

The official successful-login example shows this sequence:

1. `OnConnected()`
2. `OnLogonResponse()`
3. `IsSucceed:True ReplyString:登入成功`
4. Automatic account-list output
5. `CA 驗證通過，帳務與下單功能已初始化。`
6. `API 加載完成，歡迎使用。`

Use that documented sequence as the CA-login success evidence. The documentation does not define an `is_logged_in()` method or other Boolean login-status API. Do not substitute `repr(api)`, `print(api)`, `api._ObjOrder.FIsLogon`, or any other private/internal member as an application-level success check.

After the documented success sequence, the public account query may be used to verify that the documented account surface is usable:

```python
accounts = api.show_account()
print(accounts)
```

`show_account()` is documented as an account query, not as a CA-status method. Do not describe it as an official Boolean login checker.

The official login page states that account login and CA activation provide permission for quotes, historical data, and orders. It does not define quote availability after CA login fails. Do not rely on, promise, or encode quote-without-CA behavior as an official contract; any such runtime observation is version-specific diagnostic evidence only.

## Market selection

| Market | Method | Initialized surfaces |
| --- | --- | --- |
| Taiwan stocks | `api.set_Account(account)` | Order, Account |
| US sub-brokerage | `api.set_SubAccount(account)` | SubOrder, SubAccount |
| Domestic futures/options | `api.set_FutAccount(account)` | FutOrder, FutAccount |
| Overseas futures/options | `api.set_OvfutAccount(account)` | OvfutOrder, OvfutAccount |

Select the account using the `account_flag` label and exact user-selected account identity; do not hardcode a first list element. Domestic and overseas futures selection remain separate even if a displayed account identity is shared. Selection examples show report backfill and completion; preserve that context before interpreting order tracking after reconnect.

## Account and lifecycle methods

```python
accounts = api.show_account()
api.set_Account(account)
selected = api.login_info()
api.logout()
```

- `show_account()` returns a list of dictionaries with `account`, `account_flag`, and `broker_id`.
- `set_Account(account: str)` selects a securities account and initializes `Order` and `Account`.
- `login_info()` returns selected login data keyed by account class such as `證券`, `期貨`, and `複委託`.
- `logout()` ends the session.

## Disconnect callback

For a local Web application, read [the application pattern](web-oco-application.md) for actor-owned login, redacted progress output, inventory confirmation, and logout followed by server shutdown. SDK `api.logout()` alone does not stop a Web server; the linked design is application behavior, not an additional KGI API.

```python
def re_login():
    api.login()

api.set_disconnect_cb(re_login)
```

The callback receives no documented argument. The official example calls `api.login()` on the existing instance. This is trading-session recovery, separate from quote resubscription. In an application, apply a finite reconnect budget, retain account context, and reconcile pending orders; never replay unknown orders as a consequence of reconnect.

## Official pages

- [Prerequisites](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/prefix)
- [Service terms and runtime requirements](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/terms)
- [Login](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/inAccount)
- [Show accounts](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/showAccount)
- [Select securities account](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/setTransaction)
- [Show selected accounts](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/showInAccount)
- [Logout](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/logout)
- [Reconnect login](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/reLogin)
