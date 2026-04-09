import argparse
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

import requests
from bs4 import BeautifulSoup

NEWS_MAIN_URL = "https://finance.yahoo.com/"


@dataclass
class Article:
    title: str
    url: str


@dataclass
class StockCandidate:
    name: str
    code: str
    why: str


THEMES: Dict[str, Dict[str, object]] = {
    "AI/반도체": {
        "keywords": [
            "ai",
            "인공지능",
            "반도체",
            "칩",
            "gpu",
            "데이터센터",
            "고대역폭메모리",
            "hbm",
            "서버",
        ],
        "stocks": [
            StockCandidate("SK하이닉스", "000660", "HBM·고성능 메모리 수요의 직접 수혜 가능성이 큼"),
            StockCandidate("삼성전자", "005930", "메모리·파운드리·AI 인프라 투자 확대의 핵심 축"),
            StockCandidate("한미반도체", "042700", "후공정 장비 수요 확대 시 실적 레버리지 기대"),
        ],
    },
    "2차전지/전기차": {
        "keywords": [
            "2차전지",
            "배터리",
            "전기차",
            "ev",
            "양극재",
            "음극재",
            "리튬",
            "니켈",
            "ira",
        ],
        "stocks": [
            StockCandidate("LG에너지솔루션", "373220", "완성차향 배터리 공급 확대와 증설 모멘텀"),
            StockCandidate("에코프로비엠", "247540", "양극재 수요 회복 시 이익 민감도 높음"),
            StockCandidate("포스코퓨처엠", "003670", "소재 밸류체인 다변화와 장기 공급 계약 주목"),
        ],
    },
    "바이오/헬스케어": {
        "keywords": [
            "바이오",
            "신약",
            "임상",
            "헬스케어",
            "의약품",
            "치료제",
            "백신",
            "의료기기",
        ],
        "stocks": [
            StockCandidate("삼성바이오로직스", "207940", "CDMO 수주 확대와 생산능력 증설이 핵심"),
            StockCandidate("셀트리온", "068270", "바이오시밀러 판매 확대와 파이프라인 가치 부각"),
            StockCandidate("유한양행", "000100", "신약 파이프라인 이벤트에 따른 재평가 가능성"),
        ],
    },
    "방산/우주": {
        "keywords": [
            "방산",
            "국방",
            "수출",
            "미사일",
            "전투기",
            "우주",
            "위성",
            "안보",
        ],
        "stocks": [
            StockCandidate("한화에어로스페이스", "012450", "방산 수출 확대 시 수주 잔고의 실적화 기대"),
            StockCandidate("한국항공우주", "047810", "항공·우주 프로젝트 및 완제기 수출 모멘텀"),
            StockCandidate("LIG넥스원", "079550", "유도무기 체계 수요 증가의 수혜 가능"),
        ],
    },
    "원전/전력인프라": {
        "keywords": [
            "원전",
            "원자력",
            "전력망",
            "송배전",
            "전력수요",
            "변압기",
            "SMR",
            "전기요금",
        ],
        "stocks": [
            StockCandidate("두산에너빌리티", "034020", "원전·에너지 설비 수주 회복의 핵심 종목"),
            StockCandidate("LS ELECTRIC", "010120", "전력 인프라 투자 확대로 수주 모멘텀 기대"),
            StockCandidate("HD현대일렉트릭", "267260", "글로벌 변압기·전력기기 수요 강세 수혜"),
        ],
    },
}


def fetch_main_articles(limit: int = 40) -> List[Article]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(NEWS_MAIN_URL, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    seen = set()
    articles: List[Article] = []

    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        title = " ".join(a.get_text(" ", strip=True).split())
        if not title:
            continue
        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            href = "https://finance.yahoo.com" + href
        if not href.startswith("https://finance.yahoo.com/"):
            continue
        if "/news/" not in href:
            continue
        key = (title, href)
        if key in seen:
            continue
        seen.add(key)
        articles.append(Article(title=title, url=href))
        if len(articles) >= limit:
            break
    return articles


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def score_themes(articles: List[Article]) -> Tuple[str, List[Article], List[str]]:
    theme_scores: Dict[str, int] = {name: 0 for name in THEMES.keys()}
    theme_hits: Dict[str, List[Article]] = {name: [] for name in THEMES.keys()}
    theme_hit_keywords: Dict[str, List[str]] = {name: [] for name in THEMES.keys()}

    for article in articles:
        t = normalize(article.title)
        for theme_name, meta in THEMES.items():
            keywords = meta["keywords"]
            for kw in keywords:
                kw_norm = kw.lower()
                if kw_norm in t:
                    theme_scores[theme_name] += 1
                    theme_hits[theme_name].append(article)
                    theme_hit_keywords[theme_name].append(kw)
                    break

    best_theme = max(theme_scores.items(), key=lambda x: x[1])[0]
    return best_theme, theme_hits[best_theme], theme_hit_keywords[best_theme]


def pick_stock(theme_name: str) -> StockCandidate:
    stocks: List[StockCandidate] = THEMES[theme_name]["stocks"]
    return stocks[0]


def build_reason(
    theme_name: str, stock: StockCandidate, matched_articles: List[Article], hit_keywords: List[str]
) -> str:
    uniq_keywords = []
    for kw in hit_keywords:
        if kw not in uniq_keywords:
            uniq_keywords.append(kw)
    top_keywords = ", ".join(uniq_keywords[:5]) if uniq_keywords else "관련 키워드"
    link_count = min(len(matched_articles), 3)

    reason = (
        f"Yahoo Finance 메인 뉴스에서 '{theme_name}' 관련 신호가 다수 포착되었습니다. "
        f"주요 키워드는 {top_keywords}이며, 관련 기사 {link_count}건을 근거로 "
        f"{stock.name}({stock.code})를 추천합니다. {stock.why} "
        "단기 이슈 기반 추천이므로 실제 투자 전 실적·밸류에이션·리스크를 함께 점검하세요."
    )
    return reason[:500]


def recommend(limit: int = 40, link_limit: int = 3) -> Dict[str, object]:
    articles = fetch_main_articles(limit=limit)
    if not articles:
        raise RuntimeError("메인 페이지에서 분석 가능한 기사를 찾지 못했습니다.")

    theme_name, matched_articles, hit_keywords = score_themes(articles)
    if not matched_articles:
        fallback_theme = "AI/반도체"
        stock = pick_stock(fallback_theme)
        reason = (
            "기사 키워드 신호가 약해 기본 테마(AI/반도체)로 보수 추천했습니다. "
            f"{stock.name}({stock.code})는 {stock.why} 투자 판단 전 추가 확인이 필요합니다."
        )[:500]
        return {
            "recommended_stock": {"name": stock.name, "code": stock.code},
            "reason": reason,
            "related_articles": [{"title": a.title, "url": a.url} for a in articles[:link_limit]],
        }

    stock = pick_stock(theme_name)
    reason = build_reason(theme_name, stock, matched_articles, hit_keywords)

    dedup = []
    seen = set()
    for a in matched_articles:
        if a.url in seen:
            continue
        seen.add(a.url)
        dedup.append(a)
        if len(dedup) >= link_limit:
            break

    return {
        "theme": theme_name,
        "recommended_stock": {"name": stock.name, "code": stock.code},
        "reason": reason,
        "related_articles": [{"title": a.title, "url": a.url} for a in dedup],
    }


def print_result(result: Dict[str, object]) -> None:
    stock = result["recommended_stock"]
    print("=== 뉴스 기반 추천 결과 ===")
    if "theme" in result:
        print(f"테마: {result['theme']}")
    print(f"추천 종목: {stock['name']} ({stock['code']})")
    print(f"추천 사유(500자 이내): {result['reason']}")
    print("관련 기사 링크:")
    for i, art in enumerate(result["related_articles"], start=1):
        print(f"{i}. {art['title']}")
        print(f"   {art['url']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Yahoo Finance 메인 페이지를 분석해 국내 주식 종목을 추천합니다."
    )
    parser.add_argument("--article-limit", type=int, default=40, help="분석할 최대 기사 수")
    parser.add_argument("--link-limit", type=int, default=3, help="출력할 관련 기사 링크 수")
    args = parser.parse_args()

    result = recommend(limit=args.article_limit, link_limit=args.link_limit)
    print_result(result)


if __name__ == "__main__":
    main()
