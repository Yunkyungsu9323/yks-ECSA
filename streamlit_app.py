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

    # 서브플롯 설정 (4x4 배열로 그래프 출력)
    fig, axes = plt.subplots(nrows=4, ncols=4, figsize=(20, 20))
    axes = axes.flatten()  # 2D 배열을 1D로 변환

    # 시트별 분석 수행
    for i, sheet_name in enumerate(sheets):
        # 시트 읽기
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

        # 데이터 필터링
        filtered_data = df[(df['Ewe/V vs. SCE'] >= 0) & (df['Ewe/V vs. SCE'] <= x_ideal) & (df['<I>/mA'] > 0)]

        # x_ideal에 가장 가까운 x 값 찾기
        if not filtered_data.empty:  # 데이터가 있을 때만 계산
            # x_target은 x_ideal 값에 가장 가까운 Ewe/V vs. SCE 값의 인덱스
            x_target = (np.abs(filtered_data['Ewe/V vs. SCE'] - x_ideal)).idxmin()

            # y_target 값을 설정 (x_ideal과 가장 가까운 x의 y값)
            y_target = filtered_data.loc[x_target, '<I>/mA']

            # y 값을 y_target을 기준으로 조정 (y_target을 뺀다)
            adjusted_y = filtered_data['<I>/mA'] - y_target

            # adjusted_y 값이 0보다 작은 경우 0으로 클리핑
            adjusted_y = np.clip(adjusted_y, 0, None)

            # x와 조정된 y 데이터를 추출
            x = filtered_data['Ewe/V vs. SCE']

            # 넓이 계산 (Simpson's rule 사용)
            area = simpson(y=adjusted_y, x=x)
            areas.append(area)  # 넓이를 리스트에 추가

            # 서브플롯에 그래프 그리기
            ax = axes[i]
            ax.plot(x, adjusted_y + y_target, label=sheet_name, color='blue')
            ax.fill_between(x, adjusted_y + y_target, y_target, color='lightblue', alpha=0.5)
            ax.axhline(y=y_target, color='red', linestyle='--', label='y_target (Baseline)')
            ax.set_title(f'Sheet: {sheet_name}, Area: {area}')
            ax.set_xlabel('Ewe/V vs. SCE')
            ax.set_ylabel('<I>/mA - y_min')
            ax.legend(loc='upper right', fontsize=9)
            ax.grid(True)
        else:
            st.warning(f"No data found for x_ideal = {x_ideal} in sheet: {sheet_name}")

    # 남은 빈 서브플롯은 숨김
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    # 4x4 서브플롯 출력
    st.pyplot(fig)

    # 전체 넓이 변화 라인플롯 그리기
    if areas:  # 넓이 데이터가 존재할 때만 플롯 생성
        st.subheader("Area change across sheets")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(sheets[:len(areas)], areas, marker='o', linestyle='-', color='green')
        ax.set_title('Area change')
        ax.set_xlabel('Test')
        ax.set_ylabel('Area')
        ax.grid(True)

        # Streamlit에서 라인플롯 표시
        st.pyplot(fig)
