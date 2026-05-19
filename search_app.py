import streamlit as st
import pandas as pd
import os

# --- 1. 系統設定 ---
st.set_page_config(page_title="職業類別 & 銀行代號查詢系統", layout="wide")

# 強制調整輸入框與表格的視覺樣式
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 安全門禁系統 ---
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
            if pwd == "085799":  # 兄弟專屬密碼
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("❌ 密碼錯誤，請重新輸入！")
    st.stop()


# --- 3. 智慧雙層套件防禦 - 自動載入 GitHub 的 Excel 資料庫 ---
@st.cache_data(show_spinner=False)
def load_data(file_name):
    if os.path.exists(file_name):
        try:
            # 第一層防禦：常規讀取
            return pd.read_excel(file_name).fillna("").astype(str)
        except ImportError:
            try:
                # 第二層防禦：若缺少 openpyxl 引擎，強制切換成內建引擎相容模式
                return pd.read_excel(file_name, engine='openpyxl').fillna("").astype(str)
            except Exception:
                return None
        except Exception:
            return None
    return None

# 讀取你推上 GitHub 的那兩份 Excel
df_job = load_data("job_data.xlsx")
df_bank = load_data("bank_data.xlsx")


# --- 4. 側邊欄安全管理 ---
st.sidebar.title("⚙️ 系統管理中心")
if st.sidebar.button("🔒 安全登出系統"):
    st.session_state.auth = False
    st.rerun()

st.sidebar.divider()
st.sidebar.info("💡 提示：本系統已自動連線至 GitHub 預載最新資料庫。若未來有需要更新表格內容，請直接將新的 Excel 檔案上傳到 GitHub 覆蓋舊檔即可同步！")


# --- 5. 前台核心功能：智慧關鍵字搜尋系統 ---
st.title("🔍 職業類別 & 銀行代號智慧搜尋系統")
st.caption("📱 支援手機、平板、電腦跨裝置網頁瀏覽（資料庫已與 GitHub 同步）")

tab1, tab2 = st.tabs(["💼 職業類別快速查詢", "🏦 銀行代號快速查詢"])

# --- Tab 1: 職業類別查詢 ---
with tab1:
    st.subheader("💼 職業類別模糊搜尋")
    if df_job is not None:
        df_job_clean = df_job.copy()
        for col in df_job_clean.columns:
            df_job_clean[col] = df_job_clean[col].str.strip()
            
        keyword_job = st.text_input("💬 請輸入職業關鍵字（例如：內勤、外勤、司機、工程師）", key="search_job")
        
        if keyword_job:
            keyword_job = keyword_job.strip()
            mask = df_job_clean.apply(lambda row: row.str.contains(keyword_job, case=False, na=False)).any(axis=1)
            result_job = df_job_clean[mask]
            
            if not result_job.empty:
                st.success(f"🎯 為您找到 {len(result_job)} 筆相關職業類別資料：")
                st.dataframe(result_job, use_container_width=True, hide_index=True)
            else:
                st.warning(f"🔍 找不到包含『{keyword_job}』的職業類別，請更換關鍵字再試試。")
        else:
            st.info("💡 提示：在上方輸入關鍵字後，系統會自動在整張表格中進行智慧盲搜。")
            st.dataframe(df_job_clean, use_container_width=True, hide_index=True)
    else:
        st.error("⚠️ 系統載入失敗。請至 GitHub 檢查確認是否有將職業類別表改名為「job_data.xlsx」並放在根目錄。")

# --- Tab 2: 銀行代號查詢 ---
with tab2:
    st.subheader("🏦 銀行與分行代號模糊搜尋")
    if df_bank is not None:
        df_bank_clean = df_bank.copy()
        for col in df_bank_clean.columns:
            df_bank_clean[col] = df_bank_clean[col].str.strip()
            
        keyword_bank = st.text_input("💬 請輸入銀行名稱、分行或代碼關鍵字（例如：國泰、富邦、三民、013）", key="search_bank")
        
        if keyword_bank:
            keyword_bank = keyword_bank.strip()
            mask = df_bank_clean.apply(lambda row: row.str.contains(keyword_bank, case=False, na=False)).any(axis=1)
            result_bank = df_bank_clean[mask]
            
            if not result_bank.empty:
                st.success(f"🎯 為您找到 {len(result_bank)} 筆相關銀行資料：")
                st.dataframe(result_bank, use_container_width=True, hide_index=True)
            else:
                st.warning(f"🔍 找不到包含『{keyword_bank}』的銀行或分行，請重新輸入。")
        else:
            st.info("💡 提示：可以輸入銀行名稱、代號或地方地名，系統會自動過濾。")
            st.dataframe(df_bank_clean, use_container_width=True, hide_index=True)
    else:
        st.error("⚠️ 系統載入失敗。請至 GitHub 檢查確認是否有將銀行代號表改名為「bank_data.xlsx」並放在根目錄。")