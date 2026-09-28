import math

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

# ───────────── 구역 3: 총 관객 히스토그램 ─────────────
with st.container(border=True):
    st.header("③ 총 관객 히스토그램")

    hist_df = df.dropna(subset=["total_audi"])
    max_audi = hist_df["total_audi"].max()

    # 구간 너비: 대략 20개 구간이 되도록 보기 좋은 숫자로 맞춤
    raw = max_audi / 20
    unit = 10 ** math.floor(math.log10(raw))
    bin_size = math.ceil(raw / unit) * unit
    n_bins = int(max_audi // bin_size) + 1
    edges = [i * bin_size for i in range(n_bins + 1)]

    fig3 = go.Figure(
        go.Histogram(
            x=hist_df["total_audi"],
            xbins=dict(start=0, end=n_bins * bin_size, size=bin_size),
            hovertemplate="구간 시작 %{x:,}명<br>%{y}편<extra></extra>",
        )
    )
    fig3.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        height=450,
        xaxis_title="총 관객(명)",
        yaxis_title="영화 편수",
        bargap=0.05,
    )
    st.plotly_chart(fig3, use_container_width=True)

    # 가장 많은 영화가 몰린 구간 / 관객이 가장 많은 영화
    counts = pd.cut(hist_df["total_audi"], bins=edges, right=False).value_counts().sort_index()
    top_bin = counts.idxmax()
    top_count = int(counts.max())
    top_ratio = top_count / len(hist_df) * 100
    best = hist_df.loc[hist_df["total_audi"].idxmax()]

    st.markdown(
        f"- 가장 많은 영화가 몰린 구간: **{top_bin.left:,.0f}명 이상 {top_bin.right:,.0f}명 미만** "
        f"({top_count}편, 전체의 {top_ratio:.1f}%)\n"
        f"- 관객이 가장 많은 영화: **{best['movieNm']}** ({best['total_audi']:,.0f}명)"
    )

    insight_box("hist_total_audi")

# ───────────── 구역 4: 개봉일 스크린수 vs 총 관객 산점도 ─────────────
with st.container(border=True):
    st.header("④ 개봉일 스크린수와 총 관객의 관계")

    scatter_df = df.dropna(subset=["first_scrn", "total_audi"])

    fig4 = px.scatter(
        scatter_df,
        x="first_scrn",
        y="total_audi",
        color="genre",
        hover_name="movieNm",
        hover_data={"genre": True, "first_scrn": ":,", "total_audi": ":,"},
        labels={
            "first_scrn": "개봉일 스크린수(개)",
            "total_audi": "총 관객(명)",
            "genre": "장르",
        },
    )
    fig4.update_traces(marker=dict(size=9, opacity=0.8))
    fig4.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=550)
    st.plotly_chart(fig4, use_container_width=True)

    insight_box("scatter_scrn_audi")

# ───────────── 구역 5: 장르별 총 관객 상자 그림 (10편 이상 장르) ─────────────
with st.container(border=True):
    st.header("⑤ 장르별 총 관객 분포 (영화 10편 이상인 장르)")

    box_base = df.dropna(subset=["total_audi"])
    genre_n = box_base["genre"].value_counts()
    big_genres = genre_n[genre_n >= 10].index.tolist()  # 편수 많은 순

    if not big_genres:
        st.warning("영화가 10편 이상인 장르가 없어서 그래프를 그리지 못했습니다.")
    else:
        box_df = box_base[box_base["genre"].isin(big_genres)]

        fig5 = px.box(
            box_df,
            x="genre",
            y="total_audi",
            color="genre",
            points="outliers",
            hover_name="movieNm",
            category_orders={"genre": big_genres},
            labels={"genre": "장르", "total_audi": "총 관객(명)"},
        )
        fig5.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            height=550,
            showlegend=False,
        )
        st.plotly_chart(fig5, use_container_width=True)
        st.caption(
            "대상 장르(편수): "
            + ", ".join(f"{g} {genre_n[g]}편" for g in big_genres)
        )

    insight_box("box_genre_audi")

# ───────────── 구역 6: 버블 그래프 (점 크기 = 첫 주 관객) ─────────────
with st.container(border=True):
    st.header("⑥ 스크린수·총 관객 버블 그래프 (점 크기 = 첫 주 관객)")

    bubble_df = df.dropna(subset=["first_scrn", "total_audi", "first_week_audi"])
    # 점 크기는 0보다 커야 그려지므로 첫 주 관객이 0 이하인 영화는 제외
    bubble_df = bubble_df[bubble_df["first_week_audi"] > 0]

    fig6 = px.scatter(
        bubble_df,
        x="first_scrn",
        y="total_audi",
        size="first_week_audi",
        color="genre",
        hover_name="movieNm",
        hover_data={
            "genre": True,
            "first_scrn": ":,",
            "total_audi": ":,",
            "first_week_audi": ":,",
        },
        size_max=40,
        labels={
            "first_scrn": "개봉일 스크린수(개)",
            "total_audi": "총 관객(명)",
            "first_week_audi": "첫 주 관객(명)",
            "genre": "장르",
        },
    )
    fig6.update_traces(marker=dict(opacity=0.6, line=dict(width=0.5, color="white")))
    fig6.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=600)
    st.plotly_chart(fig6, use_container_width=True)

    insight_box("bubble_scrn_audi")

# ───────────── 구역 7: 제작 국가 → 장르 선버스트 (칸 크기 = 영화 편수) ─────────────
with st.container(border=True):
    st.header("⑦ 제작 국가에서 장르로 (칸 크기 = 영화 편수)")

    sun_df = df.copy()
    sun_df["nation"] = sun_df["nation"].fillna("미분류").astype(str).str.strip()
    sun_counts = (
        sun_df.groupby(["nation", "genre"]).size().reset_index(name="count")
    )

    fig7 = px.sunburst(
        sun_counts,
        path=["nation", "genre"],
        values="count",
    )
    fig7.update_traces(
        hovertemplate="%{label}<br>%{value}편<extra></extra>",
        textinfo="label",
    )
    fig7.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=650)
    st.plotly_chart(fig7, use_container_width=True)

    insight_box("sunburst_nation_genre")
