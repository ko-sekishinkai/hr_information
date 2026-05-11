import streamlit as st
import pandas as pd

import streamlit as st

def check_password():
    """パスワードが正しいか確認し、結果をTrue/Falseで返す"""

    def password_entered():
        """入力されたパスワードをチェックする"""
        if st.session_state["password"] == st.secrets["app_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # セッションからパスワードを削除（安全のため）
        else:
            st.session_state["password_correct"] = False

    # すでにログイン済みならTrueを返す
    if st.session_state.get("password_correct", False):
        return True

    # ログイン画面を表示する
    st.title("認証が必要です")
    st.text_input(
        "パスワードを入力してください", 
        type="password", 
        on_change=password_entered, 
        key="password"
    )

    if "password_correct" in st.session_state:
        st.error("😕 パスワードが正しくありません")
    
    return False

# --- アプリのメイン処理 ---
if check_password():
    # ここから下に、本来のアプリ（スプレッドシートの読み込みやソート）を書く
    
    # --- 設定は必ず一番最初に行う ---
    st.set_page_config(page_title="人事情報", layout="wide")

    # --- 【修正ポイント1】読み込み処理の変更 ---
    @st.cache_data
    def load_data():
        # パスを変数に格納
        EXCEL_FILE = "hr_information.xlsx"
        # pd.read_excel を使わず、動く方のアプリと同じ pd.ExcelFile + engine指定 を使用する
        xl = pd.ExcelFile(EXCEL_FILE, engine="openpyxl")
        # 最初のシート(index 0)を読み込む
        df = xl.parse(xl.sheet_names[0])
        # 「年度」列が存在する場合、中身を文字列（str）に変換する
        if "年度" in df.columns:
            df["年度"] = df["年度"].astype(str).str.replace(".0", "", regex=False)
        # ------------------
        return df


    # データのロードを実行
    try:
        df = load_data()
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {e}")
        st.stop()

    # --- その後に画面表示の命令 ---
    st.title("人事情報") # タイトルを綺麗に修正

    st.write("### 絞り込み検索")
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_years = st.multiselect(
            "年度を選択",
            options=sorted(map(str, df["年度"].unique().tolist()), reverse=True),
            default=[]
        )

    with col2:
        selected_offices = st.multiselect(
            "事業所を選択",
            options=sorted(map(str, df["事業所"].unique().tolist())),
            default=[]
        )

    with col3:
        selected_depts = st.multiselect(
            "辞令を選択",
            options=sorted(map(str, df["辞令"].dropna().astype(str).unique().tolist())),
            default=[]
        )

    filtered_df = df.copy()
    if selected_years:
        filtered_df = filtered_df[filtered_df["年度"].isin(selected_years)]
    if selected_offices:
        filtered_df = filtered_df[filtered_df["事業所"].isin(selected_offices)]
    if selected_depts:
        filtered_df = filtered_df[filtered_df["辞令"].isin(selected_depts)]

    csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 表示中のデータをCSVで保存",
        data=csv_data,
        file_name='extracted_data.csv',
        mime='text/csv',
    )

    st.write(f"表示件数: {len(filtered_df)} 件")
    st.dataframe(
        filtered_df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "年度": st.column_config.NumberColumn(
                "年度",
                format="%d"  # カンマなしの整数として表示
            )
        }
    )

    st.markdown("""
        <style>
        div[data-testid="stDataFrame"] { font-size: 0.85rem; }
        </style>
        """, unsafe_allow_html=True)
    
    # 例: df = load_data(st.secrets["spreadsheet_id"])
    # st.dataframe(df.sort_values("日付"))
else:
    # ログインしていない時はここで処理を止める
    st.stop()