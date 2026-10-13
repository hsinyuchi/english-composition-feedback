# 高中英文作文精批與修訂

此私有儲存庫保存可重複使用的英文作文批改 skill，不包含學生原稿、姓名或成績。

## 完整套件

下載 [english-essay-feedback-v1.zip](english-essay-feedback-v1.zip)，解壓縮至名為 `english-essay-feedback` 的資料夾。壓縮檔根目錄即為 skill 內容，不包含外層資料夾。

Codex 個人安裝位置為 `~/.codex/skills/english-essay-feedback/`；安裝完成後的檔案應是 `~/.codex/skills/english-essay-feedback/SKILL.md`。若已有舊版本，請先保留備份。

呼叫名稱：`$english-essay-feedback`。儲存庫名稱 `english-composition-feedback` 與 skill 呼叫名稱不同，這不影響使用。

## 批改規格

- 原稿上方紅色手寫風批改，Sp/G/W/P 黑底白字標籤。
- 第一頁成績表、字數核算與英中短評。
- 第二頁評分依據表、完整英中評語、三項個別化修訂任務與作答空間、量化與質化反思。
- 第三頁起逐句精修；基礎及進階完整範文皆有逐段中譯。
- 每生一份完整 PDF、全班前兩頁列印合併 PDF、教師 Excel 與匿名共通錯誤講義。
- Graphic Organizer 僅列課前選用，不預設加入批改成品。
- 預設先完成一位學生的樣本，教師確認後才全班處理。

## 套件內容與驗證

`SKILL.md`、`agents/openai.yaml`、三份 references，以及字數核算／前兩頁合併工具與測試。合併 PDF 工具需要 Python 的 `pypdf` 套件。

2026-10-13：skill 格式驗證及工具測試通過。本機來源版本為 `ef1da40`。此儲存庫透過網頁上傳完整 ZIP 備份，並非與本機 Git 歷史同步。
