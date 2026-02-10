import streamlit as st
import collections
from datetime import datetime
import re

st.title("LINEトーク発言数カウンター")

# 1. 期間指定のUI
st.sidebar.header("集計期間の設定")
start_date = st.sidebar.date_input("開始日", datetime(2025, 1, 1))
end_date = st.sidebar.date_input("終了日", datetime(2025, 12, 31))

uploaded_file = st.file_uploader("LINEのトーク履歴(.txt)を選択してください", type="txt")

if uploaded_file is not None:
    # 2025.txtの形式に合わせて読み込み
    content = uploaded_file.read().decode("utf-8", errors="ignore")
    lines = content.splitlines()

    member_counts = collections.Counter()
    # 通話系キーワード（Unknownのログも考慮）
    exclude_keywords = ["通話"]
    
    current_date = None
    # 日付形式「2025/1/1(水)」や「2025/03/31(月)」にマッチするパターン
    date_pattern = re.compile(r'^(\d{4})/(\d{1,2})/(\d{1,2})')

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 1. 日付行の判定と更新
        date_match = date_pattern.match(line)
        if date_match:
            try:
                y, m, d = date_match.groups()
                current_date = datetime(int(y), int(m), int(d)).date()
            except:
                pass
            continue

        # 2. メッセージ行の解析（タブ区切り）
        parts = line.split('\t')
        
        # 2025.txtは「時刻[TAB]名前[TAB]内容」の3要素構成
        if len(parts) >= 3 and current_date:
            # 期間内かチェック
            if start_date <= current_date <= end_date:
                sender = parts[1]   # 2列目が名前
                message = parts[2]  # 3列目が内容
                
                # 送信者が「Unknown」の場合や通話ログを除外
                is_call_log = any(kw in message for kw in exclude_keywords)
                if sender != "Unknown" and not is_call_log:
                    member_counts[sender] += 1

    # 結果表示
    if member_counts:
        st.success(f"{start_date} から {end_date} の集計結果")
        
        # 集計データを降順でリスト化
        sorted_data = [{"名前": name, "発言数": count} for name, count in member_counts.most_common()]
        
        # 表を表示
        st.table(sorted_data)
        
        # グラフを表示
        st.subheader("発言数ランキング")
        chart_data = {item["名前"]: item["発言数"] for item in sorted_data}
        st.bar_chart(chart_data)
        
    else:
        st.info("指定された期間内に発言が見つかりませんでした。")
        with st.expander("【デバッグ用】ファイルの先頭5行"):
            st.code("\n".join(lines[:5]))