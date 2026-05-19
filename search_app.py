import streamlit as st
import pandas as pd
import io

# --- 1. 系統設定 ---
st.set_page_config(page_title="職業類別 & 銀行代號查詢系統", layout="wide")

# 強制調整按鈕與下載鍵的視覺樣式
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; margin-bottom: 10px; }
    .stDownloadButton>button { width: 100%; border-radius: 5px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 安全門禁系統 (Session State 隔離) ---
if "auth" not in st.session_state:
    st.session_state.auth = False

# 登入介面
if not st.session_state.auth:
    st.title("🔐 智慧查詢系統管理中心")
    st.subheader("請輸入授權密碼以確保隱私安全")
    
    with st.form("login_gate"):
        pwd = st.text_input("授權密碼", type="password", placeholder="請輸入安全登入密碼")
        submit = st.form_submit_button("確認登入")
        if submit:
            if pwd == "085799":  # 沿用兄弟你最熟悉的專屬密碼
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ 密碼錯誤，請重新輸入！")
    st.stop()

# --- 3. 初始化雲端資料庫（防系統休眠消失機制） ---
# 為了避免 Streamlit Cloud 閒置休眠後資料清空，提供「設定存檔與重新載入」功能
if "df_job" not in st.session_state:
    st.session_state.df_job = None
if "df_bank" not in st.session_state:
    st.session_state.df_bank = None

# --- 4. 主介面與側邊欄管理（手動登出與檔案建檔） ---
st.sidebar.title("⚙️ 系統管理中心")

# 一鍵手動登出
if st.sidebar.button("🔒 安全登出系統"):
    st.session_state.auth = False
    st.rerun()

st.sidebar.divider()
st.sidebar.subheader("📥 原始資料建檔區")

# 職業類別表上傳
job_file = st.sidebar.file_uploader("上傳『職業類別表』Excel", type=["xlsx", "xls"])
if job_file:
    try:
        st.session_state.df_job = pd.read_excel(job_file).fillna("").astype(str)
        st.sidebar.success("✅ 職業類別表建檔成功！")
    except Exception as e:
        st.sidebar.error(f"職業表讀取失敗: {str(e)}")

# 銀行代號表上傳
bank_file = st.sidebar.file_uploader("上傳『銀行代號表』Excel", type=["xlsx", "xls"])
if bank_file:
    try:
        st.sidebar.success("✅ 銀行代號表建檔成功！")
        st.session_state.df_bank = pd.read_excel(bank_file).fillna("").astype(str)
    except Exception as e:
        st.sidebar.error(f"銀行表讀取失敗: {str(e)}")

# 備份現有參數功能（防休眠備份）
st.sidebar.divider()
st.sidebar.subheader("💾 系統參數備份")
if st.session_state.df_job is not None or st.session_state.df_bank is not None:
    output_backup = io.BytesIO()
    with pd.ExcelWriter(output_backup, engine='xlsxwriter') as writer:
        if st.session_state.df_job is not None:
            st.session_state.df_job.to_excel(writer, index=False, sheet_name='職業類別資料')
        if st.session_state.df_bank is not None:
            st.session_state.df_bank.to_excel(writer, index=False, sheet_name='銀行代號資料')
    
    st.sidebar.download_button(
        label="📦 下載當前資料庫備份",
        data=output_backup.getvalue(),
        file_name="系統智慧資料庫備份.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.sidebar.info("暫無資料可供備份，請先上傳 Excel 檔案。")


# --- 5. 前台核心功能：智慧關鍵字搜尋系統 ---
st.title("🔍 職業類別 & 銀行代號智慧搜尋系統")
st.caption("📱 支援手機、平板、電腦跨裝置網頁瀏覽")

# 使用分頁區隔兩大搜尋功能
tab1, tab2 = st.tabs(["💼 職業類別快速查詢", "🏦 銀行代號快速查詢"])

# --- Tab 1: 職業類別查詢 ---
with tab1:
    st.subheader("💼 職業類別模糊搜尋")
    if st.session_state.df_job is not None:
        # 清除前後空格的乾淨資料
        df_job_clean = st.session_state.df_job.copy()
        for col in df_job_clean.columns:
            df_job_clean[col] = df_job_clean[col].str.strip()
            
        keyword_job = st.text_input("💬 請輸入職業關鍵字（例如：內勤、外勤、司機、工程師）", key="search_job")
        
        if keyword_job:
            keyword_job = keyword_job.strip()
            # 智慧多欄位模糊比對：只要任何一欄包含關鍵字就抓出來
            mask = df_job_clean.apply(lambda row: row.str.contains(keyword_job, case=False, na=False)).any(axis=1)
            result_job = df_job_clean[mask]
            
            if not result_job.empty:
                st.success(f"🎯 為您找到 {len(result_job)} 筆相關職業類別資料：")
                st.dataframe(result_job, use_container_width=True, hide_index=True)
            else:
                st.warning(f"🔍 找不到包含『{keyword_job}』的職業類別，請更換關鍵字再試試。")
        else:
            st.info("💡 提示：在上方輸入關鍵字後，系統會自動在整張表格（代號、職業名稱、類別階層等）中進行智慧盲搜。")
            st.dataframe(df_job_clean, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ 系統尚未建立職業類別資料。請先在左側面板上傳『職業類別表』Excel 檔案建檔。")

# --- Tab 2: 銀行代號查詢 ---
with tab2:
    st.subheader("🏦 銀行與分行代號模糊搜尋")
    if st.session_state.df_bank is not None:
        df_bank_clean = st.session_state.df_bank.copy()
        for col in df_bank_clean.columns:
            df_bank_clean[col] = df_bank_clean[col].str.strip()
            
        keyword_bank = st.text_input("💬 請輸入銀行名稱、分行或代碼關鍵字（例如：國泰、富邦、三民、高雄、013）", key="search_bank")
        
        if keyword_bank:
            keyword_bank = keyword_bank.strip()
            # 智慧多欄位模糊比對
            mask = df_bank_clean.apply(lambda row: row.str.contains(keyword_bank, case=False, na=False)).any(axis=1)
            result_bank = df_bank_clean[mask]
            
            if not result_bank.empty:
                st.success(f"🎯 為您找到 {len(result_bank)} 筆相關銀行資料：")
                st.dataframe(result_bank, use_container_width=True, hide_index=True)
            else:
                st.warning(f"🔍 找不到包含『{keyword_bank}』的銀行或分行，請重新輸入。")
        else:
            st.info("💡 提示：可以輸入銀行名稱、代號，甚至是地方地名（如：三民、鳳山），系統會自動過濾對應的分行資訊。")
            st.dataframe(df_bank_clean, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ 系統尚未建立銀行代號資料。請先在左側面板上傳『銀行代號表』Excel 檔案建檔。")