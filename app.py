import streamlit as st
import collections
from datetime import datetime
import re

st.title("LINEトーク発言数カウンター")

# 1. 期間指定のUI
st.sidebar.header("集計期間の設定")
start_date = st.sidebar.date_input("開始日", datetime(2025, 1, 1))
end_date = st.sidebar.date_input("終了日", datetime.today())

uploaded_file = st.file_uploader("LINEのトーク履歴(.txt)を選択してください", type="txt")

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8", errors="ignore")
    lines = content.splitlines()

    member_counts = collections.Counter()
    exclude_keywords = ["通話"]
    
    current_date = None
    # 日付形式「2025.04.29」にマッチするパターン
    date_pattern = re.compile(r'(\d{4}\.\d{2}\.\d{2})')

    for line in lines:
        line = line.strip()
        
        # 日付行のチェック（2025.04.29 火曜日 など）
        date_match = date_pattern.match(line)
        if date_match:
            try:
                # ドット区切りの日付をdatetimeオブジェクトに変換
                current_date = datetime.strptime(date_match.group(1), '%Y.%m.%d').date()
            except:
                pass
            continue

        # 発言行のチェック（12:44 [TAB] 名前 [TAB] 内容）
        parts = line.split('\t')
        if len(parts) >= 3 and current_date:
            # 期間内かどうか判定
            if start_date <= current_date <= end_date:
                sender = parts[1]
                message = parts[2]
                
                is_call_log = any(kw in message for kw in exclude_keywords)
                if not is_call_log:
                    member_counts[sender] += 1

    # 結果表示
    if member_counts:
        st.success(f"{start_date} から {end_date} の集計結果")
        # 表形式で表示
        data = [{"名前": name, "発言数": count} for name, count in member_counts.most_common()]
        st.table(data)
        
        # せっかくなので棒グラフも追加
        st.subheader("発言数ランキング")
        chart_data = {item["名前"]: item["発言数"] for item in data}
        st.bar_chart(chart_data)
    else:
        st.info("指定された期間内に発言が見つかりませんでした。")