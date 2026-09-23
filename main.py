import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # 장르 열에 세로막대(|) 기호로 여러 장르가 적힌 경우 첫 번째 장르만 사용
    if "genre" in df.columns:
        df["genre"] = df["genre"].astype(str).str.split("|").str[0].str.strip()

    # 개봉일(여덟 자리 숫자) -> 날짜형으로 변환
    if "openDt" in df.columns:
        df["openDt"] = pd.to_datetime(df["openDt"], format="%Y%m%d", errors="coerce")

    return df


df = load_data(DATA_URL)

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
