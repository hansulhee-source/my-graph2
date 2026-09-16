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

# 계층 구조: 장르 -> 영화명, 사각형 크기: total_audi
fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체 장르"), "genre", "movieNm"],
    values="total_audi",
    title="장르 및 영화별 총 관객 수 트리맵",
    color="genre",
)

# 툴팁(마우스 오버) 설정: 영화명과 총 관객 수 표시 (숫자 천 단위 콤마 서식 적용)
fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객 수: %{value:,.0f}명",
    texttemplate="<b>%{label}</b><br>%{value:,.0f}명",
)

# 그래프 출력
st.plotly_chart(fig_treemap, use_container_width=True)

# 그래프 해석 구역
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "같은 장르 내에서도 특정 대형 흥행작이 장르 전체 관객 수의 대부분을 견인하고 있음을 사각형의 면적으로 직관적으로 비교할 수 있습니다."
)

st.markdown("---")
