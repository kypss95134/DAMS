# 公司數位設備管理系統 (DAMS)

Digital Asset Management System (DAMS) 是一個輕量、快速的數位設備管理平台，旨在幫助公司追蹤所有的硬體設備借出、歸還狀態，並能完整記錄設備的借用歷史（誰在什麼時候領用或歸還了哪台設備）。

## 開發技術棧 (Tech Stack)

此專案分為前後端分離架構，以確保擴充性與易用性：

- **後端 (Backend)**: Python, **FastAPI**, SQLAlchemy, Uvicorn
- **資料庫 (Database)**: MySQL (PyMySQL)
- **前端 (Frontend)**: 原生 HTML5, Vanilla JavaScript, CSS3
- **前端 UI 框架**: Bootstrap 5 (透過 CDN 引入)

---

## 專案目錄結構

```text
DAMS/
├── backend/                  # FastAPI 後端 API 伺服器
│   ├── main.py               # 應用程式主入口與 API 路由設定
│   ├── database.py           # MySQL 資料庫連線設定
│   ├── models.py             # SQLAlchemy 資料表結構 (裝置、歷史紀錄)
│   ├── schemas.py            # Pydantic 資料驗證模組
│   ├── create_db.py          # 自動建立 MySQL Database 的工具腳本
│   ├── requirements.txt      # Python 依賴清單
│   └── .venv/                # Python 虛擬環境
└── frontend/                 # 原生網頁前端
    ├── index.html            # 儀表板與所有操作彈窗 UI
    ├── style.css             # 客製化樣式與狀態標籤外觀
    ├── app.js                # 與後端 API 互動的 Fetch 邏輯
    └── package.json          # Node.js 初始化設定檔 (暫未使用打包工具)
```

---

## 快速開始 (Quick Start)

### 1. 準備 MySQL 資料庫服務
請確保您的本機已經安裝並且執行了 MySQL。
此專案預設連線帳密設定為：
- **Host**: `localhost`
- **User**: `root`
- **Password**: `1234`
- **Database**: `dams_db`

### 2. 環境安裝與建立資料庫
進入 `backend` 目錄內，啟動虛擬環境並安裝相依套件：

```powershell
cd backend
# 啟動虛擬環境後安裝套件
.\.venv\Scripts\pip install -r requirements.txt

# 自動建立名為 'dams_db' 的資料庫
.\.venv\Scripts\python create_db.py
```

### 3. 啟動 FastAPI 伺服器
在 `backend` 目錄下執行 uvicorn 啟動後端伺服器：

```powershell
.\.venv\Scripts\uvicorn main:app --reload
```

伺服器將會運行在 `http://localhost:8000`。
> **💡 提示**：您可以開啟 `http://localhost:8000/docs` 檢視由 Swagger UI 自動生成的 API 測試文件介面。

### 4. 開啟前端介面
不需要任何繁瑣的 Node.js 啟動指令，只需要在檔案管理員中找到 `frontend/index.html`，並**使用瀏覽器 (如 Chrome, Edge) 雙擊開啟它**，即可立即開始操作公司設備管理系統！

## 功能介紹 (Features)
- [x] **設備列表管理**：即時查看所有設備的當前狀態 (可使用 / 使用中)、所在部門與使用人。
- [x] **設備新增**：支援紀錄設備辨識碼 (Asset Tag)、設備名稱、系統型號、所在辦公室等資訊。
- [x] **設備領用與歸還**：一鍵設定設備為「使用中」並指派對象，或是一鍵「歸還」釋放設備。
- [x] **自動軌跡紀錄**：設備的每一次「新增」、「領用」、「歸還」，甚至被誰領用，都會留下不可動搖的時間戳印與歷史紀錄，隨時可以點擊「歷史」按鈕調閱。
- [x] **設備刪除**：安全地移除不再管理的設備與其歷史。