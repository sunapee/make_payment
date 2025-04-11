import streamlit as st
import pandas as pd
import time
import os   
import math

def load_css():
    with open('style1.css', encoding='utf-8') as f:
        st.markdown(f'<style1>{f.read()}</style1>', unsafe_allow_html=True)

# スタブデータ - データベースの代わりに使用
sample_data = []



# Sidebar with menu
menu = st.sidebar.radio("メニューを選択してください", ["入金", "データ覧"])

if menu == "入金":
    st.header("入金伝票")
    col1, col2, col3 = st.columns([1,1,1])

    with col1:
        st.subheader("基本情報")
        
        method = st.selectbox("入金タイプ", ["前受入金", "売掛"])
        currency = st.selectbox("通貨", ["JPY", "USD", "EUR"])
        paytype = st.selectbox("一部or全部", ["全部", "一部"])
        customer = st.text_input("顧客名")

        if (method == "売掛" or method == "前受入金") and currency == "USD":
            today_rate_usd = st.number_input("今日のレート (USD)", placeholder="入力",key="rate_usd")
        elif (method == "売掛" or method == "前受入金") and currency == "EUR":
            today_rate_eur = st.number_input("今日のレート (EUR)", placeholder="入力",key="rate_eur")    

    with col2:
        st.subheader("計画/Invoice")
        if method == "前受入金":
            num_plans = st.number_input("計画番号の数", min_value=1, value=1)
            total_advance_amount: float = 0.0
            plan_details = []

            for i in range(int(num_plans)):
                plan_number = st.text_input(f"計画番号 {i+1}")
                if currency == "JPY":
                    advance_amount = st.number_input(f"前受額{i+1} JPY", placeholder="入力",key=f"advance_jpy_{i}")
                elif currency == "USD":
                    usd_amount = st.number_input(f"前受額{i+1} USD", placeholder="入力",key=f"advance_usd_{i}")
                    advance_amount = usd_amount * 103.00
                    st.write(f"JPY換算: {advance_amount:,.0f}")
                elif currency == "EUR":
                    eur_amount = st.number_input(f"前受額{i+1} EUR", placeholder="入力",key=f"advance_eur_{i}")
                    advance_amount = eur_amount * 120.00
                    st.write(f"JPY換算: {advance_amount:,.0f}")

                plan_details.append({
                    "plan_number": plan_number,
                    "advance_amount": advance_amount
                })
                total_advance_amount += advance_amount

        elif method == "売掛":
            if currency == "JPY":
                num_plans = st.number_input("計画番号の数", min_value=1, value=1)
                total_urikake_amount: float = 0.0
                plan_details = []

                for i in range(int(num_plans)):
                    plan_number = st.text_input(f"計画番号 {i+1}")
                    urikake_date = st.date_input(f"売掛日 {i+1}")
                    urikake_amount = st.number_input(f"売掛額{i+1} JPY", placeholder="入力")

                    plan_details.append({
                        "plan_number": plan_number,  
                        "urikake_amount": urikake_amount,
                        "urikake_date": urikake_date
                    })
                    total_urikake_amount += urikake_amount
            else:
                num_invoice = st.number_input("Invoiceの数", min_value=1, value=1)
                total_urikake_amount: float = 0.0
                plan_details = []

                for i in range(int(num_invoice)):
                    invoice_number = st.text_input(f"Invoice番号 {i+1}")
                    urikake_date = st.date_input(f"売掛日 {i+1}")

                    if currency == "USD":
                        usd_amount = st.number_input(f"売掛額{i+1} USD", placeholder="入力")
                        urikake_amount = usd_amount * 103.00
                        st.write(f"JPY換算: {urikake_amount:,.0f}")
                    elif currency == "EUR":
                        eur_amount = st.number_input(f"売掛額{i+1} EUR", placeholder="入力")
                        urikake_amount = eur_amount * 120.00
                        st.write(f"JPY換算: {urikake_amount:,.0f}")

                    plan_details.append({
                        "invoice_number": invoice_number,
                        "urikake_amount": urikake_amount,
                        "urikake_date": urikake_date
                    })
                    total_urikake_amount += urikake_amount

    with col3:
        st.subheader("金額詳細")
        if method == "前受入金":
            st.write(f"合計前受額 JPY: {total_advance_amount:,.0f}")
            
            if currency == "JPY":
                deposit_amount = st.number_input("入金額 JPY", min_value=0.0, max_value=float(total_advance_amount))
                fee_amount = total_advance_amount - deposit_amount
                if abs(fee_amount) <= 1:
                    fee_amount = 0

                st.write(f"手数料 JPY: {abs(fee_amount):,.0f}")
            elif currency == "USD":
                deposit_amount = st.number_input(f"入金額 {currency}", min_value=0.0,key="deposit_usd_advance")
                jpy_deposit_amount = math.floor(deposit_amount * today_rate_usd)
                # 差益の計算：(当日レート - 103) * USD額
                # 103.00はコード上の基準レート
                base_rate = 103.00
                usd_amount = total_advance_amount / base_rate  # 基準レートでUSDに換算
                profit_margin = (today_rate_usd - base_rate) * usd_amount
                st.text_input("入金額 JPY", value=f"{int(jpy_deposit_amount):,.0f}", key="deposit_amount_jpy_advance", placeholder="自動計算されます")
                # 差益JPYをtext_inputで表示（自動更新されるように）
                st.text_input("差益 JPY", value=f"{int(profit_margin):,.0f}", key="profit_margin_advance_usd", placeholder="自動計算されます")
                
                fee_amount = total_advance_amount + profit_margin - jpy_deposit_amount
                # 手数料が1以下なら0に設定
                if abs(fee_amount) <= 1:
                    fee_amount = 0
                st.text_input("手数料 JPY", value=f"{abs(fee_amount):,.0f}", key="fee_amount_advance_jpy", placeholder="自動計算されます")
                
            elif currency == "EUR":
                deposit_amount = st.number_input(f"入金額 {currency}", min_value=0.0)
                jpy_deposit_amount = math.floor(deposit_amount * today_rate_eur)

                # 差益の計算：(当日レート - 120) * EUR額
                # 120.00はコード上の基準レート
                base_rate = 120.00
                eur_amount = total_advance_amount / base_rate  # 基準レートでEURに換算
                profit_margin = (today_rate_eur - base_rate) * eur_amount

                # 入金額JPYをtext_inputで表示
                st.text_input("入金額 JPY", value=f"{int(jpy_deposit_amount):,.0f}", key="deposit_amount_jpy_advance_eur", placeholder="自動計算されます") 

                # 差益JPYをtext_inputで表示（自動更新されるように）
                st.text_input("差益 JPY", value=f"{int(profit_margin):,.0f}", key="profit_margin_advance_eur", placeholder="自動計算されます")

                fee_amount = total_advance_amount + profit_margin - jpy_deposit_amount
                # 手数料が1以下なら0に設定
                if abs(fee_amount) <= 1:
                    fee_amount = 0
                st.text_input("手数料 JPY", value=f"{abs(fee_amount):,.0f}", key="fee_amount_advance_jpy", placeholder="自動計算されます")

        elif method == "売掛":
            st.write(f"合計売掛額 JPY: {total_urikake_amount:,.0f}")

            if currency == "JPY":
                deposit_amount = st.number_input("入金額 JPY", min_value=0.0, max_value=float(total_urikake_amount))
                fee_amount = total_urikake_amount - deposit_amount
                # 手数料が1以下なら0に設定
                if abs(fee_amount) <= 1:
                    fee_amount = 0
                st.write(f"手数料 JPY: {abs(fee_amount):,.0f}")
            
            if currency == "USD":
                deposit_amount = st.number_input(f"入金額 {currency}", min_value=0.0)
                jpy_deposit_amount = math.floor(deposit_amount * today_rate_usd)

                # 差益の計算：(当日レート - 103) * USD額
                base_rate = 103.00
                usd_amount = total_urikake_amount / base_rate  # 基準レートでUSDに換算
                profit_margin = (today_rate_usd - base_rate) * usd_amount
                # 入金額JPYをtext_inputで表示
                st.text_input("入金額 JPY", value=f"{int(jpy_deposit_amount):,.0f}", key="deposit_amount_jpy_urikake_usd", placeholder="自動計算されます")
                
                # 差益JPYをtext_inputで表示（自動更新されるように）
                st.text_input("差益 JPY", value=f"{int(profit_margin):,.0f}", key="profit_margin_urikake_usd", placeholder="自動更新されます")
                
                # 手数料の計算：売掛額 + 差益 - 入金額
                fee_amount = total_urikake_amount + profit_margin - jpy_deposit_amount
                # 手数料が1以下なら0に設定
                if abs(fee_amount) <= 1:
                    fee_amount = 0
                st.text_input("手数料 JPY", value=f"{abs(fee_amount):,.0f}", key="fee_amount_urikake_jpy", placeholder="自動計算されます")
            
            elif currency == "EUR":
                deposit_amount = st.number_input(f"入金額 {currency}", min_value=0.0)
                jpy_deposit_amount = math.floor(deposit_amount * today_rate_eur)

                # 差益の計算：(当日レート - 120) * EUR額
                base_rate = 120.00
                eur_amount = total_urikake_amount / base_rate  # 基準レートでEURに換算
                profit_margin = (today_rate_eur - base_rate) * eur_amount

                st.text_input("入金額 JPY", value=f"{int(jpy_deposit_amount):,.0f}", key="deposit_amount_jpy_urikake_eur", placeholder="自動計算されます")
                
                # 差益JPYをtext_inputで表示（自動更新されるように）
                st.text_input("差益 JPY", value=f"{int(profit_margin):,.0f}", key="profit_margin_urikake_eur", placeholder="自動更新されます")
                
                # 手数料の計算：売掛額 + 差益 - 入金額
                fee_amount = total_urikake_amount + profit_margin - jpy_deposit_amount
                # 手数料が1以下なら0に設定
                if abs(fee_amount) <= 1:
                    fee_amount = 0
                st.text_input("手数料 JPY", value=f"{abs(fee_amount):,.0f}", key="fee_amount_urikake_jpy", placeholder="自動計算されます")

    # データベースへの追加ボタンをデータ表示に変更
    if st.button("データを表示"):
        entry = {}
        if method == "前受入金":
            if currency == "JPY":
                profit_margin = 0  # JPYの場合は差益なし
            elif currency == "USD":
                profit_margin = int(jpy_deposit_amount + fee_amount - total_advance_amount)
            elif currency == "EUR":
                profit_margin = int(jpy_deposit_amount + fee_amount - total_advance_amount)
            
            # 表示用データ
            for detail in plan_details:
                entry = {
                    "id": len(sample_data) + 1,
                    "method": method,
                    "currency": currency,
                    "paytype": paytype,
                    "customer": customer,
                    "total_advance_amount": detail["advance_amount"],
                    "deposit_amount": deposit_amount,
                    "fee_amount": int(fee_amount),
                    "profit_margin": profit_margin,
                    "plan_number": detail["plan_number"]
                }
                sample_data.append(entry)
        
        elif method == "売掛":
            for detail in plan_details:
                if currency == "USD":
                    profit_margin = int((today_rate_usd - 103) * (total_urikake_amount/103.00))
                elif currency == "EUR":
                    profit_margin = int((today_rate_eur - 120) * (total_urikake_amount/120.00))
                else:  # JPY
                    profit_margin = 0
                
                # 表示用データ
                entry = {
                    "id": len(sample_data) + 1,
                    "method": method,
                    "currency": currency,
                    "paytype": paytype,
                    "customer": customer,
                    "total_advance_amount": 0,
                    "total_urikake_amount": detail["urikake_amount"],
                    "deposit_amount": deposit_amount,
                    "fee_amount": int(fee_amount),
                    "profit_margin": profit_margin,
                    "invoice_number": None if currency == "JPY" else detail.get("invoice_number"),
                    "plan_number": detail.get("plan_number") if currency == "JPY" else None,
                    "urikake_date": detail["urikake_date"]
                }
                sample_data.append(entry)
        
        # 結果を表示
        st.success("データを追加しました！")
        df = pd.DataFrame([entry])
        st.subheader("追加したデータ")
        st.dataframe(df)

if menu == "データ覧":
    st.header("登録データ一覧")

    # サンプルデータを表示
    if sample_data:
        df = pd.DataFrame(sample_data)
        st.dataframe(df)

        st.subheader("データを削除")
        if sample_data:
            selected_id = st.selectbox("削除するデータのID", [d["id"] for d in sample_data])
            
            if st.button("削除"):
                # インメモリーデータから削除
                for i, data in enumerate(sample_data):
                    if data["id"] == selected_id:
                        del sample_data[i]
                        break
                
                st.success("データを削除しました。")
                st.rerun()
    else:
        st.write("データがありません")