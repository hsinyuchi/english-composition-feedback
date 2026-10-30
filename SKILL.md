---
name: sylvia-essay
metadata:
  aliases: "english-essay-feedback, english-composition-feedback, hsinyuchi-essay-feedback"
  version: "13.0"
description: Use when Sylvia requests high-school English essay marking, handwritten student feedback, revision worksheets, or classroom error-analysis materials, or asks to maintain the approved handwriting-plus-magazine feedback layout.
---

# Sylvia Essay Feedback Suite v13.0

預設採「Codex 已核准的首頁原位批改＋Antigravity 雜誌內頁及配套」混合母版。這是固定可重用版型，不只是一份內容清單。先讀 [版面契約](references/layout.md)；製作時讀 [資料與執行規格](references/magazine-contract.md)。

## 工作流程

1. 核對原稿頁首班級、座號及續頁，不把 PDF 頁碼當座號；只處理老師指定學生。先視讀原稿，逐字轉錄，標記不確定字形。
2. 每次查核當時最新的大考中心英文作文規準，讀 [評分與校對](references/rubric-and-marks.md) 及 [篇幅政策](references/length-policy.md)。先整體評分，再以四項各5分檢驗。保留學生原意；必要訂正和可選潤飾分開。
3. 填寫單生 JSON，依 `templates/magazine.schema.json` 與 `examples/magazine_demo.json`。必填逐句原文／正句／解析／可選升級、兩版全文及中譯、3項任務、5題挑錯、3項投影重點。真實學生資料放在該教材專案，不放入技能、範例、Git或分享包。
4. **唯一預設入口：** `python scripts/render_magazine.py input.json --out <全新版本目錄>`。不得執行 `build_111_suite.py`、`build_essay_suite.py` 或 `build_master_option_a.py` 的硬編碼批次流程；`render_feedback.py` 僅保留為舊版 PDF/Excel 相容工具，不是本版預設版型。
5. 逐頁渲染與目視檢查5份PDF；首頁紅字核對原詞、所有中文標籤檢查字形。完整書10頁、列印版2頁、兩張微講義各1頁、投影片5頁。前兩頁須與完整書逐像素相同；修訂舊稿時首頁須與老師核准的首頁相同。
6. HTML 需檢查5頁、上一頁／下一頁／方向鍵／邊界與行動版。未能實際開啟時，明列「僅靜態／導覽邏輯檢查」，不可宣稱瀏覽器驗收。回報完整路徑、檔案大小、實際驗收狀態。

## 必須保留的視覺

- **首頁：** THE WRITING EDIT、5個分數方塊、Sp/G/P/W/+/x圖例、完整清晰原稿；黑底白字微膠囊＋Helvetica-Bold紅字＋精準底線／刪除線。底部保留精簡雙語導師筆記。不改回手寫風紅字、編號便當盒或純文字頁。修改既有內頁時以 `first_page_pdf` 直接嵌入核准的第一頁；其他學生不得借用該頁。
- **內頁：** 深海軍藍標籤、淺灰框線表格、分層卡片。逐句頁固定「Sentence＋紅色原句／綠色正句／灰色解析／藍色可選升級」四列，避免退回連續段落。
- **講義：** 深色重點帶、淺灰原句框；學用版24pt間距點線，教用版淺綠診斷／正句／心法框。
- **簡報：** 16:9深色底，封面＋3張紅綠對照卡＋總結，底部綠色心法框。HTML沿用同樣結構，離線可開啟。

## 完整性與範圍

單生輸出6個成品：2頁列印PDF、10頁完整PDF、學用與教用挑錯PDF、5頁投影PDF及HTML。檔名以學生ID開頭。只看一篇時，配套寫「個案修訂重點」，不可稱為全班集體盲區或推斷全班頻率。全班批次另讀 [批次規格](references/batch.md)，逐生執行，不擴大老師指定範圍。

篇幅超過固定頁面容量時，程式會停止；調整卡片分配，或向老師提出較長版本，不能刪句、漏中譯、縮成微型字硬湊10頁。缺原稿不能靜默改成逐字稿批改；缺字型不能留下方框。

版型參考只作視覺依據，不自動帶入其中學生文字、分數、年級或「滿分／全國前1%」等宣稱。新指令以本文件及新版版面契約為準；README歷史紀錄與舊腳本不覆蓋本版規格。
