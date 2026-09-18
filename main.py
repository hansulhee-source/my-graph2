import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide"
)

# 데이터 불러오기 함수 (캐싱 적용)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 개봉일(openDt)을 datetime 형태로 변환
    df["openDt"] = pd.to_datetime(df["openDt"].astype(str), format="%Y%m%d")

    # genre: 세로막대 기호(|)로 구분된 여러 장르 중 첫 번째 장르만 추출
    df["genre"] = df["genre"].fillna("미상").astype(str)
    df["genre"] = df["genre"].apply(lambda x: x.split("|")[0].strip())

    return df


# 데이터 로드
df = load_data()

# 메인 타이틀
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("---")

# Section 1: 장르별 영화 편수 분석 (도넛 그래프)
st.header("1. 장르별 영화 분포")

genre_counts = (
    df["genre"].value_counts().reset_index(name="count").rename(columns={"index": "genre"})
)

fig_genre = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.4,
    title="장르별 영화 편수 비율",
)

fig_genre.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="<b>장르: %{label}</b><br>편수: %{value}편<br>비율: %{percent}",
)

st.plotly_chart(fig_genre, use_container_width=True)

st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "박스오피스 상위권 영화 중 특정 주요 장르(예: 드라마, 액션 등)가 과반수 이상을 차지하며 높은 쏠림 현상을 보이는 것을 확인할 수 있습니다."
)

st.markdown("---")

# Section 2: 장르 및 영화별 총 관객 수 분석 (트리맵)
st.header("2. 장르 및 영화별 관객 수 점유율")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체 장르"), "genre", "movieNm"],
    values="total_audi",
    title="장르 및 영화별 총 관객 수 트리맵",
    color="genre",
)

fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객 수: %{value:,.0f}명",
    texttemplate="<b>%{label}</b><br>%{value:,.0f}명",
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "같은 장르 내에서도 특정 대형 흥행작이 장르 전체 관객 수의 대부분을 견인하고 있음을 사각형의 면적으로 직관적으로 비교할 수 있습니다."
)

st.markdown("---")

# Section 3: 총 관객 수 분포 분석 (히스토그램)
st.header("3. 총 관객 수 분포")

fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=20,
    title="총 관객 수 분포 히스토그램",
    color_discrete_sequence=["#636EFA"],
)

fig_hist.update_traces(
    hovertemplate="관객 수 구간: %{x}<br>영화 수: %{y}편"
)

fig_hist.update_layout(
    xaxis_title="총 관객 수(명)",
    yaxis_title="영화 수(편)",
)

st.plotly_chart(fig_hist, use_container_width=True)

# 최다 관객 영화 정보 데이터 자동 추출
top_movie = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie["movieNm"]
top_movie_audi = top_movie["total_audi"]

st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    f"대부분의 영화가 **100만~300만 명 이하 구간**에 빽빽하게 밀집해 있는 오른쪽으로 긴 꼬리를 가진 분포 형태를 나타냅니다. "
    f"이 중 가장 많은 관객을 기록한 작품은 **'{top_movie_name}'**(총 {top_movie_audi:,.0f}명)입니다."
)

st.markdown("---")

# Section 4: 개봉일 스크린수 vs 총 관객 수 분석 (산점도)
st.header("4. 개봉일 스크린수와 총 관객 수의 관계")

fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린수 vs 총 관객 수 산점도",
    labels={
        "first_scrn": "개봉일 스크린수(개)",
        "total_audi": "총 관객 수(명)",
        "genre": "장르",
    },
)

fig_scatter.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,.0f}개<br>총 관객 수: %{y:,.0f}명"
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "개봉일 스크린수가 많을수록 대체로 총 관객 수도 증가하는 양(+)의 상관관계를 보이지만, 스크린수가 적음에도 입소문이나 장기 상영을 통해 높은 관객 수를 달성한 흥행작(이상치)도 존재함을 알 수 있습니다."
)

st.markdown("---")

# Section 5: 주요 장르별 총 관객 수 상자 그림 (박스플롯)
st.header("5. 주요 장르별 관객 수 분포")

genre_counts_series = df["genre"].value_counts()
major_genres = genre_counts_series[genre_counts_series >= 10].index
df_box = df[df["genre"].isin(major_genres)]

fig_box = px.box(
    df_box,
    x="genre",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    points="outliers",
    title="주요 장르별 총 관객 수 상자 그림 (영화 10편 이상 장르)",
    labels={"genre": "장르", "total_audi": "총 관객 수(명)"},
)

fig_box.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>총 관객 수: %{y:,.0f}명"
)

st.plotly_chart(fig_box, use_container_width=True)

st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "주요 장르별 중간값 비교를 통해 장르 전반의 흥행 기준선을 확인하고, 상자 밖 이상치(Outlier) 점을 가리켜 각 장르의 압도적 대흥행 대표작을 구별해낼 수 있습니다."
)

st.markdown("---")

# Section 6: 스크린수 vs 총 관객 수 vs 개봉 첫 주 관객 (버블 차트)
st.header("6. 개봉 첫 주 관객을 가미한 버블 그래프")

fig_bubble = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    hover_data={
        "genre": True,
        "first_scrn": ":,.0f",
        "total_audi": ":,.0f",
        "first_week_audi": ":,.0f",
    },
    size_max=40,
    title="개봉일 스크린수 vs 총 관객 수 (버블: 첫 주 관객)",
    labels={
        "first_scrn": "개봉일 스크린수(개)",
        "total_audi": "총 관객 수(명)",
        "first_week_audi": "개봉 첫 주 관객(명)",
        "genre": "장르",
    },
)

st.plotly_chart(fig_bubble, use_container_width=True)

st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "대다수 흥행작은 개봉 첫 주 관객이 많고 스크린수가 넓게 확보될수록 최종 관객 수도 증가하는 양(+)의 상관관계를 보이나, 일부는 스크린수에 비해 높은 주차 관객이나 입소문으로 독특한 분포를 보이기도 합니다."
)

st.markdown("---")
