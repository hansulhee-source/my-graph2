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

# 히스토그램 생성
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

# 그래프 아래 결과 분석 문구
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    f"대부분의 영화가 **100만~300만 명 이하 구간**에 빽빽하게 밀집해 있는 오른쪽으로 긴 꼬리를 가진 분포 형태를 나타냅니다. "
    f"이 중 가장 많은 관객을 기록한 작품은 **'{top_movie_name}'**(총 {top_movie_audi:,.0f}명)입니다."
)

st.markdown("---")
