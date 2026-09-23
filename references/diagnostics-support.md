# SuperPy 應用的可追查 log 與支援指南

適用：開發或個人化 SuperPy 交易應用，需要使用者提供 log，讓另一位 agent 能重建操作、判讀結果與提出排查建議。本文整理本機交易應用的診斷設計經驗；這是應用開發建議，不是 SDK 官方 logging API，也不授權登入或交易。下列事件與檔名是實作建議，本 repo 沒有附上可執行的日誌收集器或應用程式。

## 不只保存事件，還要能串接因果

只寫「送單失敗」、只有成交清單、或只有零散 SDK print，不足以區分驗證失敗、未執行、已呼叫但未知，以及已獲券商回報。對具業務效果的命令，保存下列可關聯的階段；讀取快照／每個行情 tick 不必逐次重複記錄。

| 識別／欄位 | 用途 |
|---|---|
| schema、含時區時間、run_id、seq、PID | 解讀格式、區分程序執行批次、排序事件；PID 單獨不足以識別一次執行 |
| command_id、action、允許的參數 | 一次使用者操作的識別碼與輸入；只記錄白名單，不直接 dump request |
| received、started、waiting、finished/error、duration_ms | 區分入列、開始、等待非同步終態與完成／失敗 |
| mode、owner | 環境與帳戶分區；owner hash 不是加密、匿名化或授權證明 |
| unit_id、order_key、broker order_id、symbol、side | 將命令結果接到後續委託與成交；不要用股票代碼單獨關聯多組策略 |
| before/status、quantity、filled、average、reconciled | 每次**觀察到的**狀態改變與累計成交；相同快照不必重複寫 |
| error_type、file/function/line、已遮蔽訊息 | 分辨錯誤階段與程式位置；不保存 locals、原始 SDK repr 或可能帶密碼的任意 traceback 文字 |

參考時序：

```text
command_received(command_id, create, safe_parameters)
  → command_started(command_id)
  → DB intent 落盤 → SDK 呼叫
  → command_finished(command_id, unit_id 或 error)
  → order_changed(unit_id, order_key, order_id, 前後狀態／累計量)
  → 成交增量／OCO 觸發／後续撤單與出場
```

非同步回報不一定還有 command_id。建立 unit 的命令結果與後續 order_changed 的 unit_id/order_key 提供連接點；無法確認關聯時保留缺口，不猜是哪一筆。HTTP command id 不是券商單號，也不是跨重啟重送授權。

`command_finished.state=done` 僅代表應用方法完成；intent 的 `returned` 僅代表 SDK 返回。两者都不能代替委託成功、撤單終態或成交。Log 記錄的是應用可觀察結果，不保證攔截券商所有內部瞬間狀態。

## 啟動、故障與停止也要記錄

範本事件包括 bootstrap/launcher started 或 failed、server_start、server_ready、command 生命週期、order_changed、engine_event、actor_failed、server_shutdown_requested、actor_stopped、server_stopped、launcher_finished。

- actor 初始化或執行時崩潰也要留下錯誤類型與位置，拒收後續命令，並在 UI 顯示工作執行緒已停止；不能只讓 daemon thread 的 traceback 消失在隱藏視窗裡。
- 啟動記錄 Python 與來源指紋；支援封裝可附套件版本。收集時的版本／source 與故障時執行的版本可能不同，先核對，不把目前磁碟檔案當成當時執行證據。
- 日誌寫入故障應可見。補充診斷檔失敗不能把已獲接受的交易重新分類成未送出而重試；關鍵交易意圖／成交仍由資料庫保存。
- 隱藏啟動應配合 log 與啟動失敗提示。可用 `start.cmd → start.vbs → PowerShell hidden → pythonw`，但 `.cmd` 初始外殼可能瞬間閃過；直接用 `.vbs` 可省去外殼。`pythonw` 不表示 SDK 的任意原生輸出已自動保存。
- 缺少最後一筆 log 可能是斷電、強制結束、寫入失敗或通訊中斷，不能直接推論是哪一種。沒有 server_ready、沒有 started、沒有 finished 是不同證據缺口。
- 前端可回報有限類型的 client_event（network、command_error、timeout、script_error）及 command_id，不傳整個 state 或原始錯誤物件；後端已不可達時，回報本身也可能無法保存。

## 隱私與支援封裝

登入命令只記環境，不記 identity/password；其他命令的 symbol、quantity、price、stop/take、unit_id 等走白名單。字串進行遮蔽，登入 stdout 用完整行緩衝以防分段密碼外洩。人工原因、券商自由文字仍需留意，遮蔽不是任意新增欄位的安全保證。

若實作支援收集器（例如自行提供 `collect_logs.py --date YYYY-MM-DD`），只封裝指定日期的應用事件、診斷、登入與 bootstrap JSONL，以及套件版本／檔案 SHA-256。同一份讀取快照用於 hash 和封裝，避免運作中 log 追加造成 manifest 不一致。排除 DB、WAL/SHM、環境變數、憑證、原生 SDK log 和其他日期。

封裝仍有交易資料，分享前由使用者檢視。不要自動上傳或傳送給第三方，也不要因「有診斷需要」就索取密碼。確需原生 SDK 證據時先限定問題、日期與必要片段，要求去識別化；原生檔路徑與檔名也可能含帳戶身分。

## 另一位 agent 收到問題時

請使用者提供：時間與時區、使用環境、操作步驟、預期／實際結果、相關 unit 或委託識別，以及該日期的應用支援 log。不要從截圖的顏色或一段錯誤字串直接診斷全部因果。

| 證據 | 優先排查 | 不可直接建議 |
|---|---|---|
| received，沒有 started | queue、前一 SDK 呼叫阻塞、actor_failed、程序中止 | 重複按送出 |
| started，沒有 finished | DB intent、券商委託／成交、程序錯誤位置 | 假設未送達而重送 |
| 輸入驗證 error，且無新 unit／SDK 送單證據 | 修正如漲跌停範圍、數量等參數；核對是否真的停在驗證階段 | 因缺少 log 就保證券商沒收到 |
| 撤單方法 returned，仍未見终態 | 對齊原單與累計成交，查券商回報 | 把方法返回或灰階顯示當成已撤 |
| 部分成交後取消餘單 | 確認剩餘持倉與 OCO 是否仍監控 | 將整組 unit 當作已取消、無曝險 |
| SDK／交易重連後 | 帳號一致性、舊單匹配、庫存對帳與使用者恢復確認 | 自動重播未知操作 |
| 啟動／退出異常 | bootstrap、server_ready、logout、actor_stopped、server_stopped | 按任意 port/PID 強殺其他程序 |

回覆要分清「log 可證實的事實」「推論」「仍缺的證據」，列出最小的下一步與預期辨識結果。有未知外部效果時先核對；官方碼義、資格、行情／庫存欄位仍依該市場的文件與當時 SDK，不把個案泛化成通則。

## 對個人化開發者的驗證要求

新增命令、適配器、重試或背景工作時，沿用關聯識別與開始／終止語意，並更新 README 的支援收集方式。用假券商及獨立 DB 覆蓋正常、驗證拒絕、例外、未知結果、晚到成交、紀錄寫入失敗及程序啟停；確認重複輪詢不重複製造成交或狀態變更。

可將診斷、命令服務、交易引擎與收集器分成獨立模組，針對關聯識別、敏感值遮蔽、隱藏啟動與交易／UI 行為做對應檢查。將實際執行的結果與殘餘限制寫在你自己應用的文件；這份指南不附測試程式，也不代替真實券商驗收。

## 登入輸出與交易呼叫追蹤

互動登入必須在 SDK 呼叫仍進行時顯示經遮蔽的實際輸出，詳見 [UIUX 登入回饋](trading-uiux.md#互動登入的必要回饋)。摘要狀態與輸出互補，不能以「避免洩密」為由僅保留轉圈；應在完整行邊界遮蔽後再送 UI／診斷檔。未遮蔽的 SDK 自有檔案不納入一般支援匯出。

對需要逐次操作稽核的交易應用，明確說明追蹤範圍：使用者命令、策略決策、SDK 公開呼叫、持久意圖、送單／撤單、券商回報、成交入帳、對帳、重連及關閉。每筆至少保留時間、run_id、command_id（有使用者命令時）、call_id／父呼叫、操作類型、必要交易識別與結果／錯誤類型；背景事件用 run_id 與委託／策略 ID 關聯。不要承諾「所有函式」卻只記前端按鈕，也不需要逐次記錄框架與純格式函式。

實際 SDK 方法名稱不能和 SDK keyword 參數撞名，例如以 `operation` 命名包裝器的操作欄位，保留 `name` 給下單 API。驗證應實際穿過包裝器到假的 SDK create_order／cancel_order，不能只斷言 mock 的外層被呼叫。

呼叫返回、券商接受、成交與本地入帳是不同紀錄。副作用前先保留持久意圖與 dispatch 記錄；結果不明不自動重送。寫檔故障應可見並阻止新增實單，但不能抹除已受理的結果。分享前核對所選 run_id／時間範圍，排除帳密、原始 vendor logs、資料庫及其他不必要私人檔案。
