import streamlit as st
import collections
from datetime import datetime
import re

st.title("LINEトーク発言数カウンター")

# 1. 期間指定のUI
st.sidebar.header("集計期間の設定")
# 2025年をデフォルトに
start_date = st.sidebar.date_input("開始日", datetime(2025, 1, 1))
end_date = st.sidebar.date_input("終了日", datetime(2025, 12, 31))

uploaded_file = st.file_uploader("LINEのトーク履歴(.txt)を選択してください", type="txt")

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8", errors="ignore")
    lines = content.splitlines()

    member_counts = collections.Counter()
    exclude_keywords = ["通話"]
    
    current_date = None
    # 日付形式「2025.04.29 火曜日」や「2025/04/29(火)」の両方に対応
    date_pattern = re.compile(r'(\d{4})[./](\d{2})[./](\d{2})')

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 日付行のチェック
        date_match = date_pattern.search(line)
        if date_match:
            try:
                # 正規表現で「年」「月」「日」をバラバラに抽出して結合
                y, m, d = date_match.groups()
                current_date = datetime(int(y), int(m), int(d)).date()
            except:
                pass
            continue

        # 発言行のチェック
        parts = line.split('\t')
        if len(parts) >= 3 and current_date:
            # 選択された期間内かチェック
            if start_date <= current_date <= end_date:
                sender = parts[1]
                message = parts[2]
                
                is_call_log = any(kw in message for kw in exclude_keywords)
                if not is_call_log:
                    member_counts[sender] += 1

    # 結果表示
    if member_counts:
        st.success(f"{start_date} から {end_date} の集計結果")
        data = [{"名前": name, "発言数": count} for name, count in member_counts.most_common()]
        st.table(data)
        st.bar_chart({item["名前"]: item["発言数"] for item in data})
    else:
        st.info("指定された期間内に発言が見つかりませんでした。日付形式が一致していない可能性があります。")
        # デバッグ用：ファイル内の最初の方の行を少し表示して確認する
        with st.expander("【確認用】ファイル内の先頭数行を表示"):
            st.code("\n".join(lines[:10]))