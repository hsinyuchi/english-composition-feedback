# 高中英文作文精批與修訂

此私有儲存庫保存可重複使用的英文作文批改 skill，不包含學生原稿、姓名或成績。

## 完整套件

目前最新版：[english-essay-feedback-v7.zip](english-essay-feedback-v7.zip)（2026-10-14）。第二頁恢復任務1、2、3三項獨立個別化修訂任務，另列2–3題量化／質化反思，預設2題，不用反思替代第三個任務。資料版本仍為4.0，反思數量放寬為2–3；Excel預留三題欄位，不足三題時留白。公開分享版仍為本機授權草案預覽，未發布；此庫維持私人開發備份。

歷史版本：[english-essay-feedback-v6.zip](english-essay-feedback-v6.zip)（2026-10-14）。第一頁長解釋採原稿位置[1]、[2]…與下方同編號補充，不叫學生數句。行距依頁面適度調整，最多約原稿1.5–2倍，不縮字、不拉伸筆跡；取消可選潤飾框的規則不變。通用引擎不自動辨識行界，需由agent製作並驗收原稿版面。

歷史版本：[english-essay-feedback-v5.zip](english-essay-feedback-v5.zip)（2026-10-14）。曾要求保留原行距，v6改為適度彈性調整。取消「也可以這樣寫」及可選潤飾框，替代寫法集中逐句精修頁；此規則仍保留。

歷史版本：[english-essay-feedback-v4.zip](english-essay-feedback-v4.zip)（2026-10-14）。曾在第一頁呈現可選細框，v5已取消。第二頁整合學生自己的修訂、理由、內容強化、下一篇目標、完成數、自評、日期與教師核閱，作答完成即可繳交為單次修訂反思紀錄。

v4資料格式升為4.0，新增原句片段與可選潤飾欄位；已測試5個可選框及刪除僅畫線，保留短文、長文、雙面合併及資料驗證測試。下方v3、v2、v1皆為歷史版本。

歷史版本：[english-essay-feedback-v3.zip](english-essay-feedback-v3.zip)（2026-10-14）。第一頁取消短評、完整版英中評語集中第二頁；必要修正保留學生原用字，可選升級不算錯誤；加入caret插字、刪除／替換定位及黑白列印辨識規格。所有作文（包括自編題與舊題）統一使用最新大考中心英文學測四項各5分規準，記錄官方來源與查核日期。套件資料版本升為3.0，詳見內附README。

完成驗證的通用skill更新持續備份於本私有儲存庫，保留舊版；學生原稿、身份與成績不隨套件上傳。下方v2、v1為歷史版本。

歷史版本：[english-essay-feedback-v2.zip](english-essay-feedback-v2.zip)（2026-10-14）。包含跨 agent JSON 資料規格、固定 PDF / Excel 模板、渲染器、虛構範例與測試。解壓縮後先讀套件內的 README.md。需要 Python、requirements.txt 中的套件及合法可用的中文字型／手寫英文字型；不需要 chezmoi。

v2 已測試短文、840字120句長文、全班前兩頁合併、紅筆原稿註記與 Excel 公式更新；尚未在其他 agent 或 macOS / Linux 實測。長文完整保留、詳解延伸，第一頁容量不足時標示節錄；短文以個別補寫任務引導，不代寫學生原稿。字數扣分以當次官方規準為準。原始版本保留如下。

下載 [english-essay-feedback-v1.zip](english-essay-feedback-v1.zip)，解壓縮至名為 `english-essay-feedback` 的資料夾。壓縮檔根目錄即為 skill 內容，不包含外層資料夾。

Codex 個人安裝位置為 `~/.codex/skills/english-essay-feedback/`；安裝完成後的檔案應是 `~/.codex/skills/english-essay-feedback/SKILL.md`。若已有舊版本，請先保留備份。

呼叫名稱：`$english-essay-feedback`。儲存庫名稱 `english-composition-feedback` 與 skill 呼叫名稱不同，這不影響使用。

## 批改規格

- 原稿上方紅色手寫風批改，Sp/G/W/P 黑底白字標籤。
- 第一頁成績表、字數核算與必要修正；完整版英中評語集中第二頁。
- 第二頁評分依據表、完整英中評語、三項個別化修訂任務與作答空間、量化與質化反思。
- 第三頁起逐句精修；基礎及進階完整範文皆有逐段中譯。
- 每生一份完整 PDF、全班前兩頁列印合併 PDF、教師 Excel 與匿名共通錯誤講義。
- Graphic Organizer 僅列課前選用，不預設加入批改成品。
- 預設先完成一位學生的樣本，教師確認後才全班處理。

## 套件內容與驗證

`SKILL.md`、`agents/openai.yaml`、三份 references，以及字數核算／前兩頁合併工具與測試。合併 PDF 工具需要 Python 的 `pypdf` 套件。

2026-10-13：skill 格式驗證及工具測試通過。本機來源版本為 `ef1da40`。此儲存庫透過網頁上傳完整 ZIP 備份，並非與本機 Git 歷史同步。
