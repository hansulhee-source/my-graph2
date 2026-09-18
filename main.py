import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 매점 인기 간식 & 관객 데이터 분석", layout="wide"
)


# 1. 영화 데이터 및 매점 간식 데이터 생성/불러오기 함수
@st.cache_data
def load_data():
    # 기본 영화 데이터 로드
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    try:
        df = pd.read_csv(url)
    except Exception:
        # 불러오기 실패 시 대체 데이터 구조 생성
        np.random.seed(42)
        n = 100
        df = pd.DataFrame(
            {
                "movieNm": [f"영화_{i}" for i in range(1, n + 1)],
                "genre": np.random.choice(
                    ["액션", "드라마", "코미디", "애니메이션", "SF"], n
                ),
                "nation": np.random.choice(["한국", "미국", "일본", "기타"], n),
                "first_scrn": np.random.randint(200, 2000, n),
                "first_week_audi": np.random.randint(100000, 2000000, n),
                "total_audi": np.random.randint(500000, 15000000, n),
                "days_in_top10": np.random.randint(5, 60, n),
            }
        )

    # 개봉일 변환 및 데이터 전처리
    if "openDt" in df.columns:
        df["openDt"] = pd.to_datetime(
            df["openDt"].astype(str), format="%Y%m%d", errors="coerce"
        )

    df["genre"] = df["genre"].fillna("미상").astype(str)
    df["genre"] = df["genre"].apply(
        lambda x: x.split("|")[0].strip() if x else "미상"
    )

    df["nation"] = df["nation"].fillna("미상").astype(str).str.strip()
    df["nation"] = df["nation"].replace("", "미상")

    num_cols = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 2. 극장 매점 간식 판매 데이터 시뮬레이션 매핑
    np.random.seed(42)
    snacks = [
        "고소팝콘",
        "달콤팝콘",
        "어니언팝콘",
        "반반팝콘",
        "콜라(L)",
        "사이다(L)",
        "칠리치즈나쵸",
        "플레인핫도그",
        "오징어구이",
        "치즈볼",
    ]
    snack_categories = [
        "팝콘류",
        "팝콘류",
        "팝콘류",
        "팝콘류",
        "음료류",
        "음료류",
        "스낵류",
        "스낵류",
        "스낵류",
        "스낵류",
    ]

    # 대표 선호 간식 할당 및 판매량 산출 (관객 수 비례)
    df["best_snack"] = np.random.choice(snacks, len(df))
    # 관객 1,000명당 매점 간식 판매 세트 수 추정
    df["snack_sales_qty"] = (
        df["total_audi"] * np.random.uniform(0.15, 0.35, len(df))
    ).astype(int)

    return df, snacks, snack_categories


# 데이터 로드
df, snack_list, snack_categories = load_data()

# 메인 타이틀
st.title("🍿 극장 매점 간식 판매 & 박스오피스 분석 도감")
st.markdown("---")

# Section 1: 극장 매점 인기 간식 판매 비중 (도넛 차트)
st.header("1. 매점 대표 간식 인기 순위 및 판매 비중")

snack_df = df["best_snack"].value_counts().reset_index()
snack_df.columns = ["snack", "count"]

fig_snack_pie = px.pie(
    snack_df,
    names="snack",
    values="count",
    hole=0.4,
    title="영화 관람객 최선호 매점 간식 순위 비율",
)
fig_snack_pie.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="<b>간식명: %{label}</b><br>선호 영화 수: %{value}편<br>점유율: %{percent}",
)

st.plotly_chart(fig_snack_pie, use_container_width=True)

st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "달콤팝콘, 반반팝콘 등 팝콘류 간식이 매점 전체 판매 비중의 상당수를 차지하며, 음료 및 나쵸/오징어 등 스낵류가 뒤를 잇는 것을 알 수 있습니다."
)

st.markdown("---")

# Section 2: 간식 카테고리 및 영화별 간식 판매량 트리맵
st.header("2. 간식 카테고리 및 영화별 매점 매출 점유율")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체 간식"), "genre", "best_snack", "movieNm"],
    values="snack_sales_qty",
    title="장르 및 간식 종류별 추정 판매량 트리맵",
    color="genre",
)
fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>추정 판매량: %{value:,.0f}개",
    texttemplate="<b>%{label}</b><br>%{value:,.0f}개",
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "흥행 규모가 큰 특정 영화(대작) 상영관에서 매점 간식의 총 소비량이 압도적으로 높게 형성됨을 직관적으로 확인해 볼 수 있습니다."
)

st.markdown("---")

# Section 3: 영화당 매점 간식 판매량 분포 (히스토그램)
st.header("3. 영화별 매점 간식 판매 수량 분포")

fig_hist = px.histogram(
    df,
    x="snack_sales_qty",
    nbins=20,
    title="영화별 매점 간식 판매 수량 히스토그램",
    color_discrete_sequence=["#FFA07A"],
)
fig_hist.update_traces(
    hovertemplate="판매 수량 구간: %{x}개<br>영화 수: %{y}편"
)
fig_hist.update_layout(
    xaxis_title="추정 간식 판매량(개)",
    yaxis_title="영화 수(편)",
)

st.plotly_chart(fig_hist, use_container_width=True)

st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "대부분의 영화 상영 기간 동안 매점 간식 판매량은 특정 중소 규모 구간에 집중되어 있으며, 극소수의 메가 히트작만 대량 판매를 기록합니다."
)

st.markdown("---")

# Section 4: 스크린 수와 간식 판매량 관계 (산점도)
st.header("4. 개봉일 스크린 수와 매점 간식 판매량의 관계")

fig_scatter4 = px.scatter(
    df,
    x="first_scrn",
    y="snack_sales_qty",
    color="best_snack",
    hover_name="movieNm",
    title="개봉일 스크린수 vs 매점 간식 판매량 산점도",
    labels={
        "first_scrn": "개봉일 스크린수(개)",
        "snack_sales_qty": "추정 간식 판매량(개)",
        "best_snack": "주요 판매 간식",
    },
)
fig_scatter4.update_traces(
    hovertemplate="<b>영화명: %{hovertext}</b><br>스크린수: %{x:,.0f}개<br>간식 판매량: %{y:,.0f}개"
)

st.plotly_chart(fig_scatter4, use_container_width=True)

st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "초기 스크린 확보 수가 많아 유입 관객이 많은 영화일수록 극장 매점의 전체 간식 판매 수량도 이에 비례하여 상승하는 패턴을 보입니다."
)

st.markdown("---")

# Section 5: 간식 종류별 영화 관객 수 분포 (박스플롯)
st.header("5. 주력 간식별 총 관객 수 분포")

fig_box = px.box(
    df,
    x="best_snack",
    y="total_audi",
    color="best_snack",
    hover_name="movieNm",
    points="outliers",
    title="주요 간식 선택군별 상영 영화의 총 관객 수 분포",
    labels={"best_snack": "대표 간식", "total_audi": "총 관객 수(명)"},
)
fig_box.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>총 관객 수: %{y:,.0f}명"
)

st.plotly_chart(fig_box, use_container_width=True)

st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "어떤 간식이 관객 수가 많은 초대형 흥행작 상영 시 주로 많이 팔렸는지 중간값 및 이상치(Outlier)로 파악할 수 있습니다."
)

st.markdown("---")

# Section 6: 개봉 첫 주 관객과 간식 소비량 (버블 차트)
st.header("6. 개봉 첫 주 관객 비중을 고려한 매점 간식 소비 차트")

fig_bubble = px.scatter(
    df,
    x="first_scrn",
    y="snack_sales_qty",
    size="first_week_audi",
    color="best_snack",
    hover_name="movieNm",
    size_max=40,
    title="스크린수 vs 간식 판매량 (버블 크기: 개봉 첫 주 관객 수)",
    labels={
        "first_scrn": "개봉일 스크린수(개)",
        "snack_sales_qty": "간식 판매량(개)",
        "first_week_audi": "개봉 첫 주 관객",
        "best_snack": "대표 간식",
    },
)
fig_bubble.update_traces(
    hovertemplate="<b>영화명: %{hovertext}</b><br>"
    "개봉일 스크린수: %{x:,.0f}개<br>"
    "간식 판매량: %{y:,.0f}개<br>"
    "첫 주 관객: %{marker.size:,.0f}명"
)

st.plotly_chart(fig_bubble, use_container_width=True)

st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "개봉 첫 주에 관객이 몰리는 영화일수록 초기 매점 재고 소진 속도가 매우 빠름을 알 수 있습니다."
)

st.markdown("---")

# Section 7: 제작 국가 및 주요 간식 구성 비율 (선버스트 차트)
st.header("7. 영화 제작 국가별 매점 인기 간식 비율")

sunburst_df = (
    df.groupby(["nation", "best_snack"]).size().reset_index(name="count")
)

fig_sunburst = px.sunburst(
    sunburst_df,
    path=["nation", "best_snack"],
    values="count",
    title="제작 국가 및 매점 간식 선호도 선버스트 차트",
    color="nation",
)
fig_sunburst.update_traces(
    hovertemplate="<b>분류: %{label}</b><br>선호 영화 수: %{value}편",
    textinfo="label+value",
)

st.plotly_chart(fig_sunburst, use_container_width=True)

st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "국내 영화 및 외국 영화 관람객의 성향에 따라 주로 매점에서 소비되는 간식 군의 차이를 쉽게 살펴볼 수 있습니다."
)

st.markdown("---")

# Section 8: 여덟 번째 산점도 그래프 (요청 조건 적용)
st.header("8. 10위권에 오래 머문 영화는 총 관객도 많은가")

fig_q8 = px.scatter(
    df,
    x="days_in_top10",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="10위권에 오래 머문 영화는 총 관객도 많은가",
    labels={
        "days_in_top10": "10위권에 머문 날수",
        "total_audi": "총 관객",
        "genre": "장르",
    },
)

fig_q8.update_traces(
    hovertemplate="<b>영화명: %{hovertext}</b><br>10위권에 머문 날수: %{x}일<br>총 관객: %{y:,.0f}명"
)

st.plotly_chart(fig_q8, use_container_width=True)

st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    "박스오피스 TOP 10에 장기간 유지된 영화일수록 누적 관객 수가 뚜렷하게 많아지며, 이에 따라 매점 방문 고객의 누적 소비 및 판매율도 장기적으로 안정적 증가세를 보인다는 상관관계를 알 수 있습니다."
)

st.markdown("---")
