import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 한글, 음수 표시 깨짐 현상 처리
plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False



# Load data
file_path = "https://drive.google.com/uc?id=<1NY3cD6Y-Lwxs7CcxG1V17G3QZeEp-PSj>"
df = pd.read_csv(file_path, encoding='utf-8-sig')

file_path = "https://drive.google.com/uc?id=<13kWljWVIsXocFxQxc2_rWHbQkXThBjmJ>"
df_basis = pd.read_csv(file_path, encoding='utf-8-sig')

# 연월을 날짜 형식으로 변환
df_basis['연월'] = pd.to_datetime(df_basis['연월'])

# '자료구분'이 '실적'인 데이터 중에서 가장 최근 연월 찾기
last_month = df_basis[df_basis['자료구분'] == '실적']['연월'].max()

# 페이지 설정
st.set_page_config(layout="wide")

# 사이드바 구성
st.sidebar.title("그룹실적")
company_names = [
    "피치밸리", "미디어윌", "더블유쇼핑", "한석", "네트웍스", "스테이션3", 
    "아이피디", "딘타이펑", "모스버거", "나무_본사", "나무_일본", "인자인", 
    "스포츠", "홀딩스"
]
corp_codes = [
    "pv", "mw", "w", "hansuk", "alba", "st3", 
    "ipd", "dtf", "mos", "namu", "namuj", "injain", 
    "sports", "holdings"
]
company_mapping = dict(zip(company_names, corp_codes))

group_selection = st.sidebar.radio("계열사 선택", ["그룹실적"] + company_names)

# 탭 구성
tab_labels = ["MOM", "YOY", "vsBP", "vsYTDBP", "vsYTDYOY", "Yearly"]
selected_tab = st.radio("선택 탭", tab_labels)

# 데이터 필터링
if group_selection != "그룹실적":
    selected_code = company_mapping[group_selection]
    filtered_df = df[(df["회사코드"] == selected_code) & (df["비교구분"] == selected_tab.lower())]
else:
    selected_code = 'total'  # 그룹실적 선택 시 total
    filtered_df = df[df["비교구분"] == selected_tab.lower()]

# 데이터가 비어있는 경우 처리
if filtered_df.empty:
    st.write("No data available for the selected options.")
else:
    # KPI Card Section
    st.write("### 주요 실적 요약")
    kpi_columns = st.columns(3)  # 3 KPI cards for Revenue, Opex, and EBITDA

    for i, metric in enumerate(["revenue", "opex", "ebitda"]):
        # 특정 계정의 데이터 필터링
        metric_data = filtered_df[filtered_df["계정"] == metric]
        if not metric_data.empty:
            # 값 가져오기
            value = metric_data["금액 차액"].values[0]
            delta = metric_data["퍼센트 차이"].values[0]
            kpi_columns[i].metric(label=metric, value=value, delta=delta)
        else:
            kpi_columns[i].metric(label=metric, value="N/A", delta="N/A")

    # (MOM, BP, YTDBP) rev 그래프 데이터 필터링
    if selected_code:
        rev_actual_mom = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '실적') &
            (df_basis['1'] == '매출') &
            (df_basis['연월'] >= str(last_month.year) + '-01')
        ][['금액', '연월']].groupby('연월').sum()

        rev_bp_mom = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '계획') &
            (df_basis['1'] == '매출') &
            (df_basis['연월'] >= str(last_month.year) + '-01')
        ][['금액', '연월']].groupby('연월').sum()


    # (MOM, BP, YTDBP) opex 그래프 데이터 필터링
    if selected_code:
        opex_actual_mom = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '실적') &
            (df_basis['1'] == 'OPEX w/o D&A') &
            (df_basis['연월'] >= str(last_month.year) + '-01')
        ][['금액', '연월']].groupby('연월').sum()

        opex_bp_mom = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '계획') &
            (df_basis['1'] == 'OPEX w/o D&A') &
            (df_basis['연월'] >= str(last_month.year) + '-01')
        ][['금액', '연월']].groupby('연월').sum()


    # (MOM, BP, YTDBP) ebitda 그래프 데이터 필터링
    if selected_code:
        ebitda_actual_mom = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '실적') &
            (df_basis['1'] == 'EBITDA') &
            (df_basis['연월'] >= str(last_month.year) + '-01')
        ][['금액', '연월']].groupby('연월').sum()

        ebitda_bp_mom = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '계획') &
            (df_basis['1'] == 'EBITDA') &
            (df_basis['연월'] >= str(last_month.year) + '-01')
        ][['금액', '연월']].groupby('연월').sum()        



    # (yoy, YTDyoy) rev 그래프 데이터 필터링
    if selected_code:
        rev_actual_yoy1 = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '실적') &
            (df_basis['1'] == '매출') &
            (df_basis['연월'] >= str(last_month.year) + '-01')
        ][['금액', '연월']].groupby('연월').sum()

        rev_actual_yoy2 = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '실적') &
            (df_basis['1'] == '매출') &
            (df_basis['연월'].between(str(last_month.year - 1)+'-01', str(last_month.year - 1)+'-12'))
        ][['금액', '연월']].groupby('연월').sum()

    # (yoy, YTDyoy) opex 그래프 데이터 필터링
    if selected_code:
        opex_actual_yoy1 = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '실적') &
            (df_basis['1'] == 'OPEX w/o D&A') &
            (df_basis['연월'] >= str(last_month.year) + '-01')
        ][['금액', '연월']].groupby('연월').sum()

        opex_actual_yoy2 = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '실적') &
            (df_basis['1'] == 'OPEX w/o D&A') &
            (df_basis['연월'].between(str(last_month.year - 1)+'-01', str(last_month.year - 1)+'-12'))
        ][['금액', '연월']].groupby('연월').sum()

    # (yoy, YTDyoy) ebitda 그래프 데이터 필터링
    if selected_code:
        ebitda_actual_yoy1 = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '실적') &
            (df_basis['1'] == 'EBITDA') &
            (df_basis['연월'] >= str(last_month.year) + '-01')
        ][['금액', '연월']].groupby('연월').sum()

        ebitda_actual_yoy2 = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '실적') &
            (df_basis['1'] == 'EBITDA') &
            (df_basis['연월'].between(str(last_month.year - 1)+'-01', str(last_month.year - 1)+'-12'))
        ][['금액', '연월']].groupby('연월').sum()


    # (Yearly) rev 그래프 데이터 필터링
    if selected_code:
        rev_actual_yearly = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '실적') &
            (df_basis['1'] == '매출')
        ][['금액', '연도']].groupby('연도').sum()

        rev_bp_yearly = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '계획') &
            (df_basis['1'] == '매출')
        ][['금액', '연도']].groupby('연도').sum()


    # (Yearly) opex 그래프 데이터 필터링
    if selected_code:
        opex_actual_yearly = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '실적') &
            (df_basis['1'] == 'OPEX w/o D&A')
        ][['금액', '연도']].groupby('연도').sum()

        opex_bp_yearly = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '계획') &
            (df_basis['1'] == 'OPEX w/o D&A')
        ][['금액', '연도']].groupby('연도').sum()

    # (Yearly) ebitda 그래프 데이터 필터링
    if selected_code:
        ebitda_actual_yearly = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '실적') &
            (df_basis['1'] == 'EBITDA')
        ][['금액', '연도']].groupby('연도').sum()

        ebitda_bp_yearly = df_basis[
            (df_basis['회사구분'] == selected_code) &
            (df_basis['lev'] == 1) &
            (df_basis['자료구분'] == '계획') &
            (df_basis['1'] == 'EBITDA')
        ][['금액', '연도']].groupby('연도').sum()





# rev 그래프 섹션
st.write(f"### {group_selection} - 주요 실적 그래프 ({selected_tab})")
graph_columns = st.columns(3)

month_labels = [f"{i}월" for i in range(1, 13)]  # x축 레이블: "1월, 2월, ..."

# MOM, vsBP, vsYTDBP 탭일 경우
if selected_tab in ["MOM", "vsBP", "vsYTDBP"]:
    with graph_columns[0]:  # Revenue 그래프
        st.write("Revenue Graph")

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(rev_actual_mom.index.month, rev_actual_mom['금액'] / 1e8, color='green', marker='o', linestyle='solid', label='Actual')
        ax.plot(rev_bp_mom.index.month, rev_bp_mom['금액'] / 1e8, color='blue', marker='*', linestyle=':', label='BP')

        # x축 레이블 설정
        ax.set_xticks(range(1, 13))  # 1부터 12까지 설정
        ax.set_xticklabels(month_labels)  # "1월, 2월, ..." 레이블 설정

        # 기타 설정
        ax.set_ylabel('금액(억)')
        ax.set_title(f'{selected_code.upper()} Actual Revenue vs BP')
        ax.legend(loc='upper left', prop={'size': 8})
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(alpha=0.5)

        st.pyplot(fig)

    with graph_columns[1]:  # Opex 그래프
        st.write("Opex Graph")

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(opex_actual_mom.index.month, opex_actual_mom['금액'] / 1e8, color='green', marker='o', linestyle='solid', label='Actual')
        ax.plot(opex_bp_mom.index.month, opex_bp_mom['금액'] / 1e8, color='blue', marker='*', linestyle=':', label='BP')

        # x축 레이블 설정
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(month_labels)

        # 기타 설정
        ax.set_ylabel('금액(억)')
        ax.set_title(f'{selected_code.upper()} Actual Opex vs BP')
        ax.legend(loc='upper left', prop={'size': 8})
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(alpha=0.5)

        st.pyplot(fig)

    with graph_columns[2]:  # EBITDA 그래프
        st.write("EBITDA Graph")

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(ebitda_actual_mom.index.month, ebitda_actual_mom['금액'] / 1e8, color='green', marker='o', linestyle='solid', label='Actual')
        ax.plot(ebitda_bp_mom.index.month, ebitda_bp_mom['금액'] / 1e8, color='blue', marker='*', linestyle=':', label='BP')

        # x축 레이블 설정
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(month_labels)

        # 기타 설정
        ax.set_ylabel('금액(억)')
        ax.set_title(f'{selected_code.upper()} Actual EBITDA vs BP')
        ax.legend(loc='upper left', prop={'size': 8})
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(alpha=0.5)

        st.pyplot(fig)

# YOY, vsYTDBP 탭일 경우
elif selected_tab in ["YOY", "vsYTDYOY"]:
    with graph_columns[0]:  # YOY Revenue 그래프
        st.write("Revenue Graph")

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(rev_actual_yoy1.index.month, rev_actual_yoy1['금액'] / 1e8, color='green', marker='o', linestyle='solid', label='올해')
        ax.plot(rev_actual_yoy2.index.month, rev_actual_yoy2['금액'] / 1e8, color='brown', marker='*', linestyle=':', label='전년')

        # x축 레이블 설정
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(month_labels)

        # 기타 설정
        ax.set_ylabel('금액(억)')
        ax.set_title(f'{selected_code.upper()} YOY Revenue')
        ax.legend(loc='upper left', prop={'size': 8})
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(alpha=0.5)

        st.pyplot(fig)

    with graph_columns[1]:  # YOY Opex 그래프
        st.write("Opex Graph")

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(opex_actual_yoy1.index.month, opex_actual_yoy1['금액'] / 1e8, color='green', marker='o', linestyle='solid', label='올해')
        ax.plot(opex_actual_yoy2.index.month, opex_actual_yoy2['금액'] / 1e8, color='brown', marker='*', linestyle=':', label='전년')

        # x축 레이블 설정
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(month_labels)

        # 기타 설정
        ax.set_ylabel('금액(억)')
        ax.set_title(f'{selected_code.upper()} YOY Opex')
        ax.legend(loc='upper left', prop={'size': 8})
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(alpha=0.5)

        st.pyplot(fig)

    with graph_columns[2]:  # YOY EBITDA 그래프
        st.write("EBITDA Graph")

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(ebitda_actual_yoy1.index.month, ebitda_actual_yoy1['금액'] / 1e8, color='green', marker='o', linestyle='solid', label='올해')
        ax.plot(ebitda_actual_yoy2.index.month, ebitda_actual_yoy2['금액'] / 1e8, color='brown', marker='*', linestyle=':', label='전년')

        # x축 레이블 설정
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(month_labels)

        # 기타 설정
        ax.set_ylabel('금액(억)')
        ax.set_title(f'{selected_code.upper()} YOY EBITDA')
        ax.legend(loc='upper left', prop={'size': 8})
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(alpha=0.5)

        st.pyplot(fig)
        


#Yearly 탭일 경우
elif selected_tab in ["Yearly"]:
    with graph_columns[0]:  # Revenue 그래프
        st.write("Revenue Graph")

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(rev_actual_yearly.index, rev_actual_yearly['금액'] / 1e8, color='green', marker='o', linestyle='solid', label='실적')
        ax.plot(rev_bp_yearly.index, rev_bp_yearly['금액'] / 1e8, color='blue', marker='*', linestyle=':', label='계획')

        # x축 레이블 설정
        ax.set_xticks(rev_actual_yearly.index)
        ax.set_xticklabels(rev_actual_yearly.index.astype(str))

        # 기타 설정
        ax.set_ylabel('금액(억)')
        ax.set_title(f'{selected_code.upper()} Yearly Revenue')
        ax.legend(loc='upper left', prop={'size': 8})
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(alpha=0.5)

        st.pyplot(fig)


    with graph_columns[1]:  # Opex 그래프
        st.write("Opex Graph")

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(opex_actual_yearly.index.month, opex_actual_yearly['금액'] / 1e8, color='green', marker='o', linestyle='solid', label='올해')
        ax.plot(opex_bp_yearly.index.month, opex_bp_yearly['금액'] / 1e8, color='brown', marker='*', linestyle=':', label='전년')

        # x축 레이블 설정
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(month_labels)

        # 기타 설정
        ax.set_ylabel('금액(억)')
        ax.set_title(f'{selected_code.upper()} YOY Opex')
        ax.legend(loc='upper left', prop={'size': 8})
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(alpha=0.5)

        st.pyplot(fig)

    with graph_columns[2]:  # EBITDA 그래프
        st.write("EBITDA Graph")

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(ebitda_actual_yearly.index.month, ebitda_actual_yearly['금액'] / 1e8, color='green', marker='o', linestyle='solid', label='올해')
        ax.plot(ebitda_bp_yearly.index.month, ebitda_bp_yearly['금액'] / 1e8, color='brown', marker='*', linestyle=':', label='전년')

        # x축 레이블 설정
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(month_labels)

        # 기타 설정
        ax.set_ylabel('금액(억)')
        ax.set_title(f'{selected_code.upper()} YOY EBITDA')
        ax.legend(loc='upper left', prop={'size': 8})
        ax.tick_params(axis='x', labelsize=8)
        ax.grid(alpha=0.5)

        st.pyplot(fig)




        


