import pandas as pd
import yfinance as yf
import time
import io

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__)

def _fetch_recent_ndays_df(ticker: str, n_days: int) -> pd.DataFrame:
    """
    최근 n_days '거래일' 기준의 일봉 데이터를 반환합니다.
    - yfinance의 period는 달력일 기준이라 거래일 부족 가능 → 버퍼(×1.6) 적용 후 tail(n_days).
    """
    max_retries = 3
    delay_sec = 2

    # 거래일 부족 대비 버퍼: 예) 20거래일 ≈ 달력 32일 정도 → 넉넉히 1.6배
    period_days = max(int(n_days * 1.6), n_days)
    period_str = f"{period_days}d"

    for attempt in range(1, max_retries + 1):
        try:
            df = yf.download(
                tickers=ticker,
                period=period_str,
                interval="1d",
                auto_adjust=False,
                progress=False,
                threads=True,
            )

            if df is not None and not df.empty:
                # 컬럼 정리 및 필요한 컬럼만 선택
                cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
                exist_cols = [c for c in cols if c in df.columns]
                df = df[exist_cols].copy()

                # 인덱스(DateTimeIndex)를 'Date' 컬럼으로
                df = df.reset_index()
                if "Date" in df.columns and pd.api.types.is_datetime64_any_dtype(df["Date"]):
                    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

                # 최근 n_days 거래일만
                df = df.tail(n_days).reset_index(drop=True)

                if not df.empty:
                    return df
                else:
                     mylogger.warning(
                        "[%d/%d] '%s' 최근 %d거래일 데이터가 비어 있음(기간: %s). %ds 후 재시도...",
                        attempt, max_retries, ticker, n_days, period_str, delay_sec
                    )
            else:
                mylogger.warning(
                    "[%d/%d] '%s' 다운로드 결과가 비어 있음(기간: %s). %ds 후 재시도...",
                    attempt, max_retries, ticker, period_str, delay_sec
                )

        except Exception as e:
            mylogger.exception(
                "[%d/%d] '%s' 다운로드 중 오류: %s. %ds 후 재시도...",
                attempt, max_retries, ticker, repr(e), delay_sec
            )

        time.sleep(delay_sec)

    mylogger.error("'%s' 주가 데이터를 최대 %d회 시도했지만 실패했습니다.", ticker, max_retries)
    return pd.DataFrame()


def _build_chatgpt_prompt_from_df(
    ticker: str,
    df: pd.DataFrame,
    n_days: int
) -> str:
    """
    DataFrame을 CSV 문자열로 직렬화하고, ChatGPT가 해석하기 쉬운 지시문을 포함한 프롬프트로 구성합니다.
    """
    if df.empty:
        return f"[데이터 없음] 티커 '{ticker}'의 최근 {n_days} 거래일 데이터를 가져오지 못했습니다."

    # CSV 직렬화 (너무 큰 수치가 들어오면 SI 단위가 더 낫지만, 그대로 두는 편이 후처리에 유리)
    buf = io.StringIO()
    # 컬럼 순서 정렬(있을 때만)
    preferred = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
    cols = [c for c in preferred if c in df.columns]
    df[cols].to_csv(buf, index=False)
    csv_block = buf.getvalue().strip()

    # 분석 지시문(한국어)
    hint_ko = (
        "다음 일봉 데이터(CSV)를 기반으로 아래 항목에 대해 분석해 주세요:"
        "1. 최근 추세 (상승 / 하락 / 횡보)"
        "2. 변동성 지표 (일중 고저폭, 표준편차 등)"
        "3. 거래량 변화"
        "4. 5일 / 20일 단순이동평균(SMA) 분석"
        "5. 의미 있는 지지선 및 저항선"
        "6. 갭 발생 여부 및 이상치 존재"
        "가능하다면, 최근 5일 평균 거래량 vs 이전 5일처럼 **수치를 근거로 간단한 비교 요약**을 추가해 주세요."
        "마지막으로, **1~2주 단기 관찰 포인트 및 주요 리스크 요인**도 간략히 정리해 주세요."
    )
    hint_eng = (
        "Based on the following daily candle (CSV) data, please analyze:"
        "1. Recent trend(uptrend / downtrend / sideways)"
        "2. Volatility indicators(daily high - low range, standard deviation, etc.)"
        "3. Volume change"
        "4. 5 - day / 20 - day simple moving average(SMA) perspective"
        "5. Meaningful support / resistance zones"
        "6. Gaps or anomalies"
        "If possible, include simple numeric comparisons(e.g., average volume over the last 5 days vs the previous 5 days)."
        "Finally, summarize key risks and observation points for the next 1–2 weeks."
    )

    prompt = (
        f"아래는 티커 '{ticker}'의 최근 {n_days} 거래일 일봉 데이터임.\n"
        f"분석 지시:\n- {hint_eng}\n\n"
        f"데이터 설명:\n- Date: YYYY-MM-DD\n- 가격: Open/High/Low/Close, 보정가: Adj Close, 거래량: Volume(주)\n\n"
        f"CSV 데이터 시작\n{csv_block}\nCSV 데이터 끝"
    )
    return prompt

# 권장 데이터 일수 120일
def get_prompt(ticker: str, n_days: int = 120) -> list[dict]:
    """
    외부에서 호출하는 메인 함수:
    - 최근 n_days 거래일의 일봉 데이터를 yfinance로 가져와
    - ChatGPT 분석에 바로 사용할 수 있는 '한국어 프롬프트 문자열'을 반환.
    """
    df = _fetch_recent_ndays_df(ticker=ticker, n_days=n_days)
    content = _build_chatgpt_prompt_from_df(ticker=ticker, df=df, n_days=n_days)
    return [
        {"role": "system",
         "content": "당신은 한국어 사용 금융 애널리스트임. 주식 초보에게 하듯 쉽게 설명할 것."},
        {"role": "user",
         "content": content},
    ]