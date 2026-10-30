# v13資料與執行規格

唯一預設入口：`python scripts/render_magazine.py <單生JSON> --out <尚不存在的目錄>`。

此程式沒有匯入即寫檔的副作用，不能一次傳入`students`。輸出目錄若已存在會停止。稿件、預覽、資料及成果存入實際教材專案；技能內只留虛構範例與程式。

## JSON欄位

- `id`：安全檔名，如301_16；`class`、`seat`、`topic`為實際資料。
- `paragraphs`：逐字原稿段落；`sentences`：依序列出`original`、`corrected`、`analysis`、`optional`。原句合併須與段落完全相符，不能省略句子。10頁版接受4–12句；過長需重新議定長版，不自動刪減。
- `scores`：固定內容、組織、文法句構、字彙拼字，四項各5分；每項填`label/value/brief/reason/strategy`。`brief`用於第2頁短摘要；完整`reason/strategy`用於第3頁。
- `total/tier/deduction/self_count`：診斷總分、適用級距、另扣分、學生自填字數。程式獨立核算原稿字數，驗證總分合計。未知的自填字數省略。
- `feedback_zh/feedback_en`：第2頁簡短雙語評語；`tasks`：3個個人化修訂任務。
- `basic/enhanced`：各含`en`、`zh`對應段落陣列，另可填`note`說明新增觀點。基本版保留原想法；進階版是示範，不是學生表現。
- `worksheet`：5題，含`title/original/corrected/analysis/rule`。另填`source_sentence_ids`（從1起算）及`source_mode`：verbatim完整原句、excerpt連續摘句、adapted教學改寫、word_list詞組整理。程式核對引用句號及原文，教學改寫／詞組整理會另標示，不能冒充完整原句。
- `slide_indices`：挑上述5題的3個不重複索引，從0起算。`slide_title`為選填主題標題，未填為「作文修訂：三大重點」，不寫死公園或年份。
- `actions`：3項`title/steps`；`learning_summary`：讓學生知道可記錄的練習內容，不冒稱已完成的反思。
- `rubric`：當次查核的`title/url/checked`；`uncertainty`：辨識疑義與原意判讀。

## 首頁兩種來源

1. **保留已核准首頁：** `first_page_pdf`為同一學生已核准PDF的絕對或JSON相對路徑。必填`first_page_sha256`（該PDF檔案SHA-256）與`first_page_transcription_sha256`（將原稿段落以空白接合、連續空白正規化為一個空白後，UTF-8文字的SHA-256）。只嵌入第1頁，精確核對學生ID及題目，並核對兩項指紋。ID應為班級_座號，且class/seat一致；相近座號不共用首頁。首次建立關聯時仍須視讀確認，雜湊不會自動辨識手寫內容；之後可阻擋沿用舊JSON時忘了更換首頁。修改內頁時用此方式，不重畫核准頁。
2. **首次批改新學生：** `scan`為相對JSON的完整手稿影像；`scan_line_count`填實際手稿行數，`short_zh/short_en`為首頁短評。原圖不覆寫。影像過長（高寬比大於2.2，或超過22行）會停止，需人工規劃自然段分欄或較長列印版本；目前入口不自動硬縮長稿。`annotations`每筆填`label/text/x1/x2/y/text_x/text_y`，座標為完整影像左上角起0–1比例；`x1/x2/y`標原詞底線，`text_x/text_y`標上方黑膠囊左側基線。必要時`operation`填delete或insert，其餘為replace。英字用Helvetica-Bold，中文批註改用JHB並驗字形；文字框越界或互相碰撞即停止。須另目視核對原筆跡與座標，程式無法保證不遮住所有原字。

固定字型Windows路徑：msjh.ttc、msjhbd.ttc、georgia.ttf、georgiab.ttf、georgiai.ttf。缺少即停止；移植其他系統需明確配置相同角色的字型並重新驗收，不宣稱跨OS已驗證。PDF建立依賴requirements.txt。視覺檢驗可用PyMuPDF或Poppler，另查實際安裝狀態。

## 相容性

`templates/feedback.schema.json`與`render_feedback.py`保留供舊版PDF/Excel；不是v13資料格式。不要把舊範例直接丟入新入口。`build_*`保留為歷史資源，含固定學生／路徑，不直接執行或匯入。需要Excel時另走原批次資料流程，不能以它的舊版PDF取代本版6個成品。

程式的`audit.json`初始寫`visual_qa=pending`；檢視最終渲染後補記驗收範圍。執行成功不代表已完成視覺驗收，也不代表已在Antigravity內實跑。每次保留原稿與上一版，失敗預覽另用新目錄重試。
