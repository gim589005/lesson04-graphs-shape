import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/happykth/data/main/kobis_movies.csv"

st.set_page_config(page_title="영화 데이터 그래프 도감 2", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL)
    # 장르가 '|'로 여러 개 적힌 경우 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"].fillna("미분류").astype(str).str.split("|").str[0].str.strip()
    )
    # 개봉일: 여덟 자리 숫자 -> 날짜
    df["openDt"] = pd.to_datetime(df["openDt"].astype(str), format="%Y%m%d", errors="coerce")
    return df


def insight_box(key: str) -> None:
    """그래프 아래 '이 그래프로 알 수 있는 것' 한 문장 자리."""
    st.markdown("**💡 이 그래프로 알 수 있는 것**")
    st.info("(여기에 한 문장을 적어 주세요.)")


st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("1년간 박스오피스 10위권에 든 영화 중 이 기간에 개봉한 영화의 요약표를 그래프로 살펴봅니다.")

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()

with st.expander("데이터 미리보기"):
    st.write(f"영화 {len(df):,}편")
    st.dataframe(df.head(20), use_container_width=True)

# ───────────── 구역 1: 장르별 영화 편수 (도넛) ─────────────
with st.container(border=True):
    st.header("① 장르별 영화 편수")

    genre_counts = df["genre"].value_counts().reset_index()
    genre_counts.columns = ["genre", "count"]

    fig = go.Figure(
        go.Pie(
            labels=genre_counts["genre"],
            values=genre_counts["count"],
            hole=0.5,
            sort=False,
            textinfo="label+percent",
            hovertemplate="%{label}<br>%{value}편 (%{percent})<extra></extra>",
        )
    )
    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        height=500,
        annotations=[
            dict(text=f"총 {len(df)}편", x=0.5, y=0.5, font_size=20, showarrow=False)
        ],
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_box("donut_genre")

# ───────────── 구역 2: 장르 안의 영화 트리맵 ─────────────
with st.container(border=True):
    st.header("② 장르별 영화 트리맵 (칸 크기 = 총 관객)")

    tree_df = df.dropna(subset=["total_audi"])
    tree_df = tree_df[tree_df["total_audi"] > 0]

    fig2 = px.treemap(
        tree_df,
        path=[px.Constant("전체"), "genre", "movieNm"],
        values="total_audi",
    )
    fig2.update_traces(
        hovertemplate="%{label}<br>총 관객 %{value:,}명<extra></extra>",
        textinfo="label",
    )
    fig2.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=600)
    st.plotly_chart(fig2, use_container_width=True)

    insight_box("treemap_genre_movie")
