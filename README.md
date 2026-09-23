<p align="center">
  <img src="assets/hero.png" alt="KGI SuperPy Skill：結合台灣、Python 與 API 連結意象的社群專案封面" width="100%">
</p>

<h1 align="center">讓 AI 更懂 SuperPy，讓你專注把交易工具做出來。</h1>

<p align="center">
  為台灣開發者整理的 <strong>凱基（KGI）SuperPy API 社群 Skill</strong><br>
  把 API 文件、市場差異與整合經驗，變成 AI 助手寫程式時可查用的知識。
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-0f766e" alt="MIT 授權"></a>
  <img src="https://img.shields.io/badge/Skill-1.37.7-0891b2" alt="Skill 版本 1.37.7">
  <img src="https://img.shields.io/badge/社群貢獻-非官方-475569" alt="非官方社群貢獻">
  <img src="https://img.shields.io/badge/README-繁體中文-0f766e" alt="繁體中文 README">
</p>

<p align="center">
  <a href="#quick-start">快速開始</a> ·
  <a href="#try-it">直接試問</a> ·
  <a href="#coverage">涵蓋範圍</a> ·
  <a href="#references">文件導覽</a> ·
  <a href="CONTRIBUTING.md">一起貢獻</a>
</p>

---

## 從「幫我寫一段 API」到「先把市場與流程搞清楚」

用 AI 串接交易 API，難的常常不是 Python 語法，而是細節：帳號選對了嗎？台股和美股的改單方式一樣嗎？方法已回傳，代表委託成功，還是只是等待處理？

**KGI SuperPy Skill 把這些容易踩到的差異，整理成 AI 助手能按需求查閱的指引。** 你可以用繁體中文描述需求，讓助手依市場、操作與文件版本找出對應規則，再協助撰寫、檢查或排查程式。

適合正在做這些事的你：

- **第一次串接 SuperPy**：釐清安裝、憑證、登入、選帳號與登出的順序。
- **用 AI 開發行情或交易工具**：讓生成的程式有文件依據，少靠名稱猜 API。
- **從台股擴展到美股或期貨**：先辨認市場差異，再處理委託、帳務與回報。
- **維護既有 Python 專案**：檢查回呼、委託狀態、斷線恢復與去識別化診斷紀錄。
- **設計交易介面與策略工作台**：組合狀態呈現、操作回饋、提醒與復原流程，保留自己的策略與買賣執行方式。

> 本專案由社群整理與維護，未受凱基官方背書。這是一套給 AI 助手使用的指引與參考文件；SuperPy SDK、券商服務與開通資格仍由官方提供。安裝 Skill 本身不會連線券商或執行交易。

## 這個 Skill 帶來什麼？

| 開發時常見的問題 | Skill 提供的協助 |
| --- | --- |
| 文件很多，不知道先讀哪一段 | 依市場與操作分流，從登入、下單、帳務到行情與回測逐步定位 |
| AI 寫出看似合理、其實不存在的方法 | 保留方法名稱、參數與來源；文件有矛盾時明確標示待查證處 |
| 把「方法回傳」誤當成「已成交」 | 區分方法返回、操作回報、委託狀態與成交證據 |
| 跨市場時沿用錯誤假設 | 分開整理帳號選擇、數量單位、委託識別與改撤單語意 |
| 發生問題，只剩一句「送單失敗」 | 提供操作關聯、狀態追蹤、敏感資訊遮蔽與診斷順序的設計參考 |
| 畫面顯示已連線，卻不知道策略是否在執行 | 分開呈現資料新鮮度、策略狀態與執行模式，提供可組合的交易 UIUX 模式 |

Skill 的作用是提供更有依據的開發脈絡；實際程式仍需依你的 SDK 版本與環境驗證。

<a id="quick-start"></a>

## 快速開始

### 1. 把 Skill 加入你的 AI 開發環境

本 repo 根目錄就是完整的 `kgi-superpy-tw` Skill，包含 `SKILL.md`、`references/` 與 Codex 顯示設定。

**在 Codex 對話中安裝**

```text
請使用 $skill-installer，從 https://github.com/pypysuper-og/kgi-superpy-tw
安裝 repo 根目錄的 skill，名稱為 kgi-superpy-tw。
```

**或在 Windows PowerShell 手動安裝**（需先安裝 Git）：

```powershell
$skillDir = Join-Path $HOME '.agents\skills\kgi-superpy-tw'
if (Test-Path -LiteralPath $skillDir) {
    throw "目標已存在，請先確認既有版本與本機修改：$skillDir"
}
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $skillDir) | Out-Null
git clone https://github.com/pypysuper-og/kgi-superpy-tw.git $skillDir
if ($LASTEXITCODE -ne 0) { throw 'Skill 下載失敗，請檢查上方錯誤。' }
```

Codex 的使用者層級 Skill 目錄為 `~/.agents/skills`；安裝後若尚未出現在清單，重新啟動 Codex。詳見 [OpenAI 官方 Skills 說明](https://developers.openai.com/codex/skills/)。若已在其他目錄安裝同名 Skill，請先確認要保留的版本，避免重複載入。

其他支援 `SKILL.md` 的 AI 開發工具，可依各工具的安裝規則載入完整資料夾；工具間的自動觸發與顯示設定可能不同，本 repo 不宣稱已逐一驗證。

### 2. 用一個明確的需求開始

```text
請使用 $kgi-superpy-tw，幫我規劃台股行情查詢工具。
先說明必要環境、登入與選帳號順序，再產生程式骨架。
這次只做程式開發，不執行登入或下單；不確定的 API 請標出文件依據。
```

你也可以直接說「幫我用凱基 SuperPy 寫一個……」，由支援自動選用 Skill 的助手判斷是否載入。明確指定 `$kgi-superpy-tw` 最容易確認使用的是這份指引。

### 3. 要執行程式時，再準備 SDK 與使用資格

Skill 和 Python 套件是分開安裝的。需要執行 SuperPy 程式時，請依 [官方使用指南](https://superpy.kgieworld.com.tw/kgipythonapi/guide/tw/) 與 [環境參考](references/session.md)，確認 Python／作業系統相容性、帳戶資格、API 開通與 CA 憑證。

```powershell
python -m pip install kgisuperpy
```

以上指令只安裝套件，不代表已完成資格開通、憑證設定或登入驗證。請勿把帳號、密碼或憑證內容貼進公開 Issue。

<a id="try-it"></a>

## 複製這些提問，開始做你的工具

**行情工具**

```text
請使用 $kgi-superpy-tw，規劃台股即時行情小工具。
我要訂閱成交與五檔，請說明回呼註冊、訂閱／取消訂閱與斷線恢復流程。
先產生程式與離線驗證方式，不連線券商。
```

**跨市場程式檢查**

```text
請使用 $kgi-superpy-tw，檢查這段美股複委託程式。
特別確認選帳號、改單方式與委託識別，不要直接套用台股規則。
請列出確定的文件依據與需要再確認的地方，不執行交易。
```

**歷史資料與回測**

```text
請使用 $kgi-superpy-tw，規劃台股歷史資料到回測的流程。
先確認資料表名稱、更新時間與數量單位，再提出程式骨架。
請區分文件列出的更新時程與資料實際新鮮度。
```

**除錯與維護**

```text
請使用 $kgi-superpy-tw，協助分析已去識別化的委託事件。
目前方法已返回，但沒有確認委託成功。
請區分可證實事實、推論與缺少的證據，提出查核步驟，不自動重送。
```

**交易工作台 UIUX**

```text
請使用 $kgi-superpy-tw，改善我的 SuperPy 定期買入工作台。
保留既有排程與委託方式，使用固定工作區，以分頁／頁面與彈窗收納功能。
整理登入到選帳、先登出再結束、連線指示與重連，以及可點開的操作說明。
有登入並訂閱行情時，在商品或策略旁動態展示最新成交價、來源時間與有效狀態；操作和交易生命週期須可由log追查。
請區分策略狀態與是否允許自動送單，說明停用按鈕的原因與下一步。
先提出介面設計與展示驗證情境，不登入券商或執行交易。
```

<a id="coverage"></a>

## 一份 Skill，按四個市場分別理解

| 市場 | 已整理的開發主題 | 使用時要留意 |
| --- | --- | --- |
| 台灣證券 | 委託、改撤單、帳務、行情、歷史資料與回測 | 委託數量與回測數量不能直接互換 |
| 美股複委託 | `SubOrder`／`SubAccount`、`USQuote`、`USData`／`USMSMP` | 手冊基準明載不提供美股模擬；改單採取消後重建 |
| 國內期貨／選擇權 | `FutOrder`／`FutAccount`、`FutQuote`、原始行情與歷史資料 | 行情別名與實際交易契約需分開處理 |
| 海外期貨／選擇權 | `OvfutOrder`／`OvfutAccount`、商品契約與回報 | 此 Skill 尚未建立海外行情／歷史資料介面的文件契約 |

另提供以實際操作為主的 [交易應用 UX 指南](references/trading-uiux.md)。視覺配色可以替換；以下體驗應按產品需求實作並驗證：

| 使用體驗 | 設計重點 |
| --- | --- |
| 固定工作區與功能收納 | 桌面主畫面盡量不整頁捲動；用分頁、頁面、詳情及彈窗收納，長資料在區域內捲動 |
| 登入與結束 | 即時遮蔽登入輸出；登入成功切換選帳，選帳成功關窗；先登出，確認結束後全畫面提示 |
| 指示燈與重連 | 區分本機、券商、行情、帳戶與交易權限；顯示退避等待、恢復與待對帳狀態 |
| 操作說明 | 功能附近提供可點的問號／說明彈窗，清楚交代前提、影響、結果與下一步 |
| 可稽核 log | 串起命令、SDK 呼叫、送撤單、回報、成交、重連與關閉；遮蔽敏感值並提供匯出 |
| 最新成交價 | 已登入且訂閱後，在適合的商品／策略位置持續更新；區分等待首筆、最新成交、過期與斷線 |

適用於人工交易、定期執行或其他策略；不要求固定三欄、OCO 或特定買賣方式。訂閱 API 返回不代表已收到成交；snapshot、試撮與委買賣報價也不能冒充最新實際成交。

台股本機 Web OCO（停損／停利擇一觸發）作為具體案例，說明整張／零股、庫存不足時僅提醒、資料保存及重連等設計。這些內容沒有附可直接啟動的交易應用，不代表 SDK 提供排程、網格或券商端 OCO 服務。

<a id="references"></a>

## 文件導覽

從 [SKILL.md](SKILL.md) 進入，或直接閱讀你需要的主題：

| 想了解什麼 | 參考文件 |
| --- | --- |
| 安裝、資格、憑證、登入與選帳號 | [Session 與環境](references/session.md) |
| 台股下單與帳務 | [委託 API](references/orders.md) · [帳務 API](references/accounts.md) |
| 方法返回、委託成功、成交的差別 | [委託生命週期與診斷](references/order-lifecycle.md) |
| 美股、國內期權、海外期權 | [美股複委託](references/us-stocks.md) · [國內期權](references/domestic-futures.md) · [海外期權](references/overseas-futures.md) |
| 行情訂閱、回呼、錯誤與恢復 | [行情](references/quotes.md) · [行情事件](references/quote-events.md) |
| 歷史資料、MSMP 與回測 | [資料與回測](references/data-and-backtest.md) |
| 通用交易介面、策略狀態與操作回饋 | [交易應用 UIUX 指南](references/trading-uiux.md) |
| 本機交易工具與可追查紀錄 | [Web OCO 設計參考](references/web-oco-application.md) · [診斷與支援](references/diagnostics-support.md) |
| 文件版本、矛盾與來源 | [手冊基準](references/manual-baseline.md) · [官方連結索引](references/official-index.md) |

README 與使用情境採繁體中文；部分技術參考採英文，保留 API 拼字與欄位名稱，方便助手查閱及程式對照。你仍可要求助手全程以繁體中文解釋。

## 版本與使用邊界

本版將 Web 指南重整為六項 UX 契約：功能收納、登入／結束、連線／重連、就地說明、完整稽核，以及訂閱後的最新成交價展示。提供設計與驗證建議，不附已完成訂閱整合的 Web 程式。

- **Skill 版本：`1.37.7`。** 先前版本新增通用交易 UIUX 指南，並擴充 OCO 案例的零股與僅提醒狀態；內容屬應用設計建議。文件基準為《凱基 Python API 使用手冊 v1.37》；其中版本紀錄涵蓋 SDK `V2.1.2`。Skill、手冊、SDK 是三種不同版本，詳見 [來源與差異](references/manual-baseline.md)。
- **文件整理不等於實機相容性保證。** 參考文件中的歷史觀察有其版本與條件；要判斷目前行為，仍需核對官方資訊與你的安裝環境。
- **正式登入與交易需要明確授權。** 登入的授權不包含下單；不因模擬環境不可用就改連正式環境。結果未知時先查核，不盲目重送。
- **這是開發輔助，不提供投資建議或獲利承諾。** 自動交易與本機 OCO 的行為、失效條件及監控責任，須由實際應用清楚定義與驗證。

## 一起讓台灣的 API 開發經驗更好

歡迎補充文件差異、修正參數說明、分享已去識別化的最小重現案例，或改善繁體中文使用體驗。提出修正時，附上 **SDK 版本、作業系統、市場與官方來源**，會更容易確認問題。

- 發現問題：[開啟 Issue](https://github.com/pypysuper-og/kgi-superpy-tw/issues)
- 想貢獻內容：[閱讀貢獻指南](CONTRIBUTING.md)
- 覺得有幫助：給專案一顆 Star，讓更多台灣開發者找到這份資源。

## 授權與致謝

本專案原創的 Skill 指引與整理內容採 [MIT License](LICENSE)。SuperPy SDK、官方文件、商標與第三方素材的權利仍屬各自權利人；本授權不替它們重新授權。Repo 不包含官方手冊原檔、SDK 安裝包、帳戶資料或憑證。

感謝凱基提供 SuperPy API 與文件，也歡迎社群一起補齊實際整合時需要的知識。封面以 AI 生成，僅供本社群專案視覺呈現，非官方品牌素材；[製作說明](assets/README.md)。
