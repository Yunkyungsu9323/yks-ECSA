import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simpson
import streamlit as st

# Streamlit 설정
st.title("ECSA Area Analysis")

# 엑셀 파일 업로드
uploaded_file = st.file_uploader("Upload an Excel file", type="xlsx")

if uploaded_file is not None:
    # 엑셀 파일에서 시트 이름 가져오기
    sheets = pd.ExcelFile(uploaded_file).sheet_names

    # x_ideal 값 설정 (슬라이더)
    x_ideal = st.slider("Select value (Ewe/V vs. SCE)", 0.0, 1.0, 0.4)

    # 각 시트의 넓이를 저장할 리스트
    areas = []

    # subplot 크기 계산 (최대 4열)
    num_sheets = len(sheets)
    cols = 4
    rows = int(np.ceil(num_sheets / cols))

    # 서브플롯 생성
    fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(5*cols, 5*rows))
    axes = axes.flatten()

    # 시트별 분석 수행
    for i, sheet_name in enumerate(sheets):
        # 시트 읽기
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

        # 데이터 필터링
        filtered_data = df[(df['Ewe/V vs. SCE'] >= 0) & 
                           (df['Ewe/V vs. SCE'] <= x_ideal) & 
                           (df['<I>/mA'] > 0)]

        if not filtered_data.empty:  # 데이터가 있을 때만 계산
            # x_target: x_ideal 값에 가장 가까운 Ewe/V vs. SCE 인덱스
            x_target = (np.abs(filtered_data['Ewe/V vs. SCE'] - x_ideal)).idxmin()

            # y_target: 해당 x의 <I>/mA 값
            y_target = filtered_data.loc[x_target, '<I>/mA']

            # y_target을 기준으로 y값 조정
            adjusted_y = filtered_data['<I>/mA'] - y_target
            adjusted_y = np.clip(adjusted_y, 0, None)

            # x 값 추출
            x = filtered_data['Ewe/V vs. SCE']

            # Simpson’s rule로 면적 계산
            area = simpson(y=adjusted_y, x=x)
            areas.append(area)

            # 서브플롯에 그래프 그리기
            ax = axes[i]
            ax.plot(x, adjusted_y + y_target, label=sheet_name, color='blue')
            ax.fill_between(x, adjusted_y + y_target, y_target, color='lightblue', alpha=0.5)
            ax.axhline(y=y_target, color='red', linestyle='--', label='y_target (Baseline)')
            ax.set_title(f'Sheet: {sheet_name}, Area: {area:.2f}')
            ax.set_xlabel('Ewe/V vs. SCE')
            ax.set_ylabel('<I>/mA - y_min')
            ax.legend(loc='upper right', fontsize=9)
            ax.grid(True)
        else:
            st.warning(f"No data found for x_ideal = {x_ideal} in sheet: {sheet_name}")

    # 남는 subplot 제거
    for j in range(i+1, len(axes)):
        fig.delaxes(axes[j])

    # subplot 출력
    st.pyplot(fig)

    # 전체 넓이 변화 라인플롯
    if areas:  
        st.subheader("Area change across sheets")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(sheets[:len(areas)], areas, marker='o', linestyle='-', color='green')
        ax.set_title('Area change')
        ax.set_xlabel('Test')
        ax.set_ylabel('Area')
        ax.grid(True)

        # Streamlit에서 라인플롯 표시
        st.pyplot(fig)
