import io
import time

import requests
import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

RAW_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
# raw.githubusercontent.com 이 막혔을 때를 대비한 jsDelivr CDN 미러
MIRROR_URL = "https://cdn.jsdelivr.net/gh/greatsong/modudata@main/data/kobis_movies.csv"


@st.cache_data(show_spinner="데이터를 불러오는 중...")
def load_data() -> pd.DataFrame:
    headers = {"User-Agent": "Mozilla/5.0"}
    last_error = None

    # raw URL과 미러 URL을 각각 최대 3번씩 시도한다.
    for url in (RAW_URL, MIRROR_URL):
        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    df = pd.read_csv(io.StringIO(response.text))

                    # 장르 열에 세로막대(|) 기호로 여러 장르가 적힌 경우 첫 번째 장르만 사용
                    if "genre" in df.columns:
                        df["genre"] = (
                            df["genre"].astype(str).str.split("|").str[0].str.strip()
                        )

                    # 개봉일(여덟 자리 숫자) -> 날짜형으로 변환
                    if "openDt" in df.columns:
                        df["openDt"] = pd.to_datetime(
                            df["openDt"], format="%Y%m%d", errors="coerce"
                        )

                    return df
                else:
                    last_error = f"{url} -> 상태 코드 {response.status_code}"
            except requests.exceptions.RequestException as e:
                last_error = f"{url} -> {e}"
            time.sleep(1.5)

    # 모든 시도가 실패한 경우: 원인을 화면에 그대로 보여주고 앱을 멈춘다.
    st.error(
        "데이터를 불러오지 못했습니다. GitHub 서버가 일시적으로 요청을 막았을 수 있어요 "
        "(예: 요청 과다로 인한 접속 제한). 잠시 후 새로고침하거나 아래 오류 내용을 확인해 주세요."
    )
    st.code(last_error)
    st.stop()


df = load_data()

with st.expander("원본 데이터 미리보기"):
    st.dataframe(df, use_container_width=True)

st.divider()

# ------------------------------------------------------------
# 그래프 1. 장르별 영화 편수 - 도넛 그래프
# ------------------------------------------------------------
st.header("1. 장르별 영화 편수")

genre_counts = (
    df["genre"]
    .value_counts()
    .reset_index()
)
genre_counts.columns = ["genre", "count"]

fig1 = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.5,
)
fig1.update_traces(
    textinfo="none",
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig1.update_layout(
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")

st.divider()

# ------------------------------------------------------------
# 그래프 2. 장르 안 영화 - 트리맵 (크기: 총 관객)
# ------------------------------------------------------------
st.header("2. 장르별 영화 총 관객 트리맵")

treemap_df = df[["genre", "movieNm", "total_audi"]].dropna(subset=["total_audi"])

fig2 = px.treemap(
    treemap_df,
    path=[px.Constant("전체"), "genre", "movieNm"],
    values="total_audi",
)
fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객: %{value:,.0f}명<extra></extra>",
)
fig2.update_layout(
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것:** ")

st.divider()
