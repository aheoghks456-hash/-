from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List

import streamlit as st

# ---------------------------
# 설정
# ---------------------------
APP_TITLE = "🌳 우리학교 나무 지도"
DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "trees.json")

st.set_page_config(page_title=APP_TITLE, page_icon="🌳", layout="wide")
st.title(APP_TITLE)
st.caption("나무를 기록하고(누적), 가정을 세우고 확인하며, 나무의 구조·기능과 생태계 역할을 배우는 간단한 기록/학습 사이트")

# 데이터 폴더 생성
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------
# 학습 카드(초등 버전)
# ---------------------------
LEARNING_CARDS = [
    {
        "key": "광합성",
        "emoji": "🌿",
        "one_line": "나무는 빛을 이용해 양분을 만들고 산소를 내보내요.",
        "easy": [
            "재료: 빛(햇빛), 물(뿌리에서 올라옴), 이산화탄소(공기)",
            "결과: 양분(나무의 먹이), 산소(사람과 동물이 숨 쉬는 데 도움)"
        ],
        "check": [
            "가정: 햇빛이 잘 드는 곳의 잎이 더 넓거나 푸르지 않을까?",
            "확인: 같은 나무에서 햇빛/그늘 쪽 잎을 사진 찍어 비교해보기"
        ],
        "ecosystem": "산소를 만들고, 나무가 자라면서 탄소를 저장해요(지구에 도움)."
    },
    {
        "key": "증산(물의 이동)",
        "emoji": "💧",
        "one_line": "잎에서 물이 수증기로 빠져나가면, 아래에서 물이 계속 올라와요.",
        "easy": [
            "뿌리 → 줄기(물관) → 잎으로 물이 이동해요.",
            "잎의 기공으로 물이 수증기로 나가요(증산)."
        ],
        "check": [
            "가정: 바람이 불고 더운 날은 잎에서 물이 더 많이 나갈까?",
            "확인: 잎을 비닐봉지로 감싸두고(짧은 시간), 물방울 맺힘 관찰(교사 지도)"
        ],
        "ecosystem": "주변 공기를 시원하게 하고(그늘+수분), 물순환에 도움을 줘요."
    },
    {
        "key": "모세관 현상",
        "emoji": "🧪",
        "one_line": "아주 가는 길에서는 물이 위로 잘 올라가요.",
        "easy": [
            "나무의 물길(물관)은 아주 가늘어요.",
            "가느다란 길(틈)에서 물이 올라가는 힘이 생겨요."
        ],
        "check": [
            "가정: 종이타월도 물이 위로 올라갈까?",
            "확인: 컵에 물을 담고 종이타월 끝을 담가 물이 올라오는 모습 관찰"
        ],
        "ecosystem": "뿌리에서 얻은 물을 잎까지 보내 나무가 살아갈 수 있게 해줘요."
    },
    {
        "key": "삼투(삼투압)",
        "emoji": "🧫",
        "one_line": "물은 ‘진한 쪽’으로 이동하려는 성질이 있어요(막이 있을 때).",
        "easy": [
            "뿌리세포는 ‘막’이 있어요.",
            "뿌리 주변과 세포 안의 농도 차이 때문에 물이 이동해요(설명은 아주 간단히!)."
        ],
        "check": [
            "가정: 소금물과 맹물에서 식물 줄기의 상태가 다를까?",
            "확인: (안전/지도) 같은 채소 줄기를 맹물/연한 소금물에 두고 변화를 관찰"
        ],
        "ecosystem": "뿌리가 물과 양분을 흡수하는 데 도움이 돼요."
    },
    {
        "key": "나이테(성장)",
        "emoji": "🪵",
        "one_line": "나무는 한 해 한 해 자라며 흔적(나이테)을 남겨요.",
        "easy": [
            "해마다 자란 부분이 고리처럼 보여요.",
            "비가 많고 조건이 좋으면 더 잘 자라기도 해요."
        ],
        "check": [
            "가정: 비가 많이 온 해에는 나이테가 더 두꺼울까?",
            "확인: (자료/사진) 나이테 사진을 찾아 두께 차이를 관찰해보기"
        ],
        "ecosystem": "오랫동안 탄소를 저장하고, 많은 생물의 집이 돼요."
    },
    {
        "key": "뿌리의 역할",
        "emoji": "🧩",
        "one_line": "뿌리는 물을 흡수하고, 나무를 단단히 붙잡아요.",
        "easy": [
            "뿌리털이 물을 흡수해요.",
            "흙을 잡아주어 비가 와도 흙이 쉽게 쓸리지 않게 해요."
        ],
        "check": [
            "가정: 나무가 많은 곳은 비가 와도 흙이 덜 쓸릴까?",
            "확인: 흙길/잔디/나무 주변의 흙 상태를 사진으로 비교 관찰"
        ],
        "ecosystem": "토양 유실을 막고, 흙 속 생물들이 살기 좋은 환경을 만들어요."
    },
]

CARD_BY_KEY = {c["key"]: c for c in LEARNING_CARDS}


# ---------------------------
# DB 로드/세이브
# ---------------------------
def load_db() -> Dict[str, Any]:
    if not os.path.exists(DB_PATH):
        return {"trees": []}
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # 파일이 깨졌을 때를 대비해 빈 DB로 시작
        return {"trees": []}


def save_db(db: Dict[str, Any]) -> None:
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def new_tree_id() -> str:
    return str(uuid.uuid4())[:8]


# ---------------------------
# UI: 사이드바
# ---------------------------
st.sidebar.header("메뉴")
page = st.sidebar.radio(
    "이동",
    ["🗺️ 나무 지도", "➕ 나무 추가", "📝 관찰/가정 기록", "📚 기능 학습", "⚙️ 데이터(내보내기/가져오기)"],
    index=0,
)

st.sidebar.divider()
st.sidebar.caption("✅ 팁: 처음엔 '나무 추가' → '관찰/가정 기록' → '기능 학습' 순서가 쉬워요.")


db = load_db()
trees: List[Dict[str, Any]] = db.get("trees", [])

# ---------------------------
# 유틸: 나무 선택 목록 만들기
# ---------------------------
def tree_label(t: Dict[str, Any]) -> str:
    # 지도표시를 위해 번호 느낌
    return f"{t.get('name','(이름없음)')} · {t.get('location','(위치없음)')} · #{t.get('id','')}"


def find_tree(tree_id: str) -> Dict[str, Any] | None:
    for t in trees:
        if t.get("id") == tree_id:
            return t
    return None


# ---------------------------
# 페이지: 나무 지도
# ---------------------------
if page == "🗺️ 나무 지도":
    st.subheader("🗺️ 우리학교 나무 목록(지도용)")
    if not trees:
        st.info("아직 등록된 나무가 없어요. ➕ '나무 추가'에서 먼저 등록해보세요.")
    else:
        # 간단한 검색
        q = st.text_input("검색(이름/위치/특징)", placeholder="예: 운동장, 은행, 그늘")
        filtered = trees
        if q.strip():
            q2 = q.strip().lower()
            def hit(t):
                text = " ".join([
                    str(t.get("name","")),
                    str(t.get("location","")),
                    str(t.get("notes","")),
                    " ".join(t.get("tags", [])),
                ]).lower()
                return q2 in text
            filtered = [t for t in trees if hit(t)]

        st.write(f"등록된 나무: **{len(filtered)} / {len(trees)}**")
        for t in filtered:
            with st.expander(f"🌳 {tree_label(t)}", expanded=False):
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.write(f"**이름**: {t.get('name','')}")
                    st.write(f"**위치**: {t.get('location','')}")
                    st.write(f"**종/분류(선택)**: {t.get('species','')}")
                    if t.get("tags"):
                        st.write("**태그**:", ", ".join(t["tags"]))
                with c2:
                    st.write("**요약 메모**")
                    st.write(t.get("notes", ""))
                # 관찰 기록 요약
                recs = t.get("records", [])
                st.caption(f"기록 {len(recs)}개")
                if recs:
                    last = recs[-1]
                    st.write(f"최근 기록: {last.get('time','')} · {last.get('title','')}")
                    st.write(f"- 가정: {last.get('hypothesis','')}")
                    st.write(f"- 확인: {last.get('evidence','')}")


# ---------------------------
# 페이지: 나무 추가
# ---------------------------
elif page == "➕ 나무 추가":
    st.subheader("➕ 나무 등록")
    st.caption("이름과 위치만 적어도 등록 가능. 사진은 선택(가볍게 하기 위해 파일 저장 X, 기록에만 텍스트로 남김)")

    with st.form("add_tree_form", clear_on_submit=True):
        name = st.text_input("나무 이름(예: 운동장 은행나무)", max_chars=50)
        location = st.text_input("위치(예: 운동장 동쪽, 급식실 옆)", max_chars=80)
        species = st.text_input("종/분류(선택, 예: 은행나무, 느티나무)", max_chars=50)
        tags = st.text_input("태그(쉼표로 구분, 예: 그늘, 열매, 키큼)", max_chars=120)
        notes = st.text_area("요약 메모(선택)", height=100)

        submitted = st.form_submit_button("✅ 등록하기")

    if submitted:
        if not name.strip() or not location.strip():
            st.error("이름과 위치는 꼭 필요해요.")
        else:
            t = {
                "id": new_tree_id(),
                "created": now_str(),
                "name": name.strip(),
                "location": location.strip(),
                "species": species.strip(),
                "tags": [x.strip() for x in tags.split(",") if x.strip()],
                "notes": notes.strip(),
                "records": []  # 관찰/가정 기록이 쌓이는 곳
            }
            trees.append(t)
            db["trees"] = trees
            save_db(db)
            st.success(f"등록 완료! → {tree_label(t)}")


# ---------------------------
# 페이지: 관찰/가정 기록
# ---------------------------
elif page == "📝 관찰/가정 기록":
    st.subheader("📝 관찰 + 가정 + 확인 기록(누적)")

    if not trees:
        st.info("먼저 나무를 등록해야 기록할 수 있어요. ➕ '나무 추가'로 가세요.")
    else:
        options = {tree_label(t): t["id"] for t in trees}
        selected_label = st.selectbox("기록할 나무 선택", list(options.keys()))
        selected_id = options[selected_label]
        t = find_tree(selected_id)

        if not t:
            st.error("선택한 나무를 찾을 수 없어요.")
        else:
            st.write(f"선택: **{t.get('name')}** · {t.get('location')}")

            # 간단 학습 주제 선택(가정과 연결)
            topic_keys = [c["key"] for c in LEARNING_CARDS]
            topic = st.selectbox("이번 기록과 연결할 기능/구조(선택)", ["(선택 안 함)"] + topic_keys)

            if topic != "(선택 안 함)":
                card = CARD_BY_KEY[topic]
                with st.expander(f"{card['emoji']} {card['key']} 빠른 힌트(초등)", expanded=False):
                    st.write("**한 줄 설명**:", card["one_line"])
                    st.write("**가정 아이디어**")
                    for x in card["check"]:
                        st.write("- " + x)

            st.divider()
            st.caption("✅ 기록은 짧게 써도 좋아요. 누적이 힘입니다.")

            with st.form("record_form", clear_on_submit=True):
                title = st.text_input("기록 제목", placeholder="예: 잎 색이 달라요 / 바람 부는 날 잎 느낌", max_chars=80)
                observation = st.text_area("관찰(무엇을 보았나요?)", height=90, placeholder="예: 그늘 쪽 잎이 더 진한 초록색이에요.")
                hypothesis = st.text_area("가정(왜 그럴까요?)", height=70, placeholder="예: 햇빛이 많아야 광합성이 더 잘 돼서 잎이 더 건강할 것 같아요.")
                evidence = st.text_area("확인(어떻게 확인했나요?)", height=70, placeholder="예: 햇빛/그늘 쪽 잎 사진 2장을 찍어서 비교했어요.")
                result = st.text_area("결과/배운 점(한 줄)", height=70, placeholder="예: 햇빛 쪽 잎이 더 두껍고 색이 진했어요.")
                photo_note = st.text_input("사진 메모(선택: 파일 저장 대신 '어떤 사진인지'만)", placeholder="예: 1/16 잎 앞면 확대 사진")

                submitted = st.form_submit_button("✅ 저장(누적)")

            if submitted:
                if not title.strip():
                    st.error("기록 제목은 꼭 적어주세요.")
                else:
                    rec = {
                        "time": now_str(),
                        "title": title.strip(),
                        "topic": "" if topic == "(선택 안 함)" else topic,
                        "observation": observation.strip(),
                        "hypothesis": hypothesis.strip(),
                        "evidence": evidence.strip(),
                        "result": result.strip(),
                        "photo_note": photo_note.strip(),
                    }
                    t.setdefault("records", []).append(rec)
                    save_db(db)
                    st.success("저장 완료! 아래에서 누적 기록을 확인해요.")

            st.divider()
            st.subheader("📚 누적 기록 보기")
            recs = t.get("records", [])
            if not recs:
                st.info("아직 기록이 없어요. 위에서 첫 기록을 남겨보세요.")
            else:
                # 최근 것이 위로 보이게
                for i, rec in enumerate(reversed(recs), start=1):
                    head = f"{i}. {rec.get('title','')} · {rec.get('time','')}"
                    if rec.get("topic"):
                        head += f" · [{rec['topic']}]"
                    with st.expander(head, expanded=False):
                        st.write("**관찰**:", rec.get("observation",""))
                        st.write("**가정**:", rec.get("hypothesis",""))
                        st.write("**확인**:", rec.get("evidence",""))
                        st.write("**결과/배운 점**:", rec.get("result",""))
                        if rec.get("photo_note"):
                            st.write("**사진 메모**:", rec["photo_note"])


# ---------------------------
# 페이지: 기능 학습
# ---------------------------
elif page == "📚 기능 학습":
    st.subheader("📚 나무의 구조·기능을 쉽게 배우기")
    st.caption("학생들이 '가정 → 확인'으로 연결할 수 있게 구성했어요.")

    # 카드 선택
    keys = [c["key"] for c in LEARNING_CARDS]
    pick = st.selectbox("학습할 주제 선택", keys, index=0)
    card = CARD_BY_KEY[pick]

    st.markdown(f"## {card['emoji']} {card['key']}")
    st.info(card["one_line"])

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.markdown("### 🔎 쉬운 설명")
        for x in card["easy"]:
            st.write("- " + x)

    with c2:
        st.markdown("### 🧠 가정 → 확인")
        for x in card["check"]:
            st.write("- " + x)

    with c3:
        st.markdown("### 🌍 생태계에서의 역할")
        st.write(card["ecosystem"])

    st.divider()
    st.subheader("🔗 나무 기록과 연결 팁")
    st.write("• '관찰/가정 기록'에서 주제를 선택하면 힌트가 자동으로 보여요.")
    st.write("• 기록은 짧게, 자주 남기는 게 좋아요.")


# ---------------------------
# 페이지: 데이터(내보내기/가져오기)
# ---------------------------
elif page == "⚙️ 데이터(내보내기/가져오기)":
    st.subheader("⚙️ 데이터 관리")
    st.caption("기록을 파일로 백업(내보내기)하거나 다시 가져올 수 있어요.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📤 내보내기(백업)")
        db_text = json.dumps(db, ensure_ascii=False, indent=2)
        st.download_button(
            label="💾 trees.json 다운로드",
            data=db_text.encode("utf-8"),
            file_name="trees.json",
            mime="application/json",
        )
        st.caption("다운로드한 파일을 잘 보관하면 기록이 안전해요.")

    with col2:
        st.markdown("### 📥 가져오기(복원)")
        up = st.file_uploader("이전에 저장한 trees.json 업로드", type=["json"])
        if up is not None:
            try:
                new_db = json.loads(up.read().decode("utf-8"))
                if "trees" not in new_db or not isinstance(new_db["trees"], list):
                    st.error("파일 형식이 올바르지 않아요(trees 목록이 필요).")
                else:
                    # 덮어쓰기
                    db = new_db
                    trees = db["trees"]
                    save_db(db)
                    st.success("가져오기 완료! 왼쪽 '나무 지도'에서 확인하세요.")
            except Exception as e:
                st.error(f"파일을 읽는 중 오류: {e}")

    st.divider()
    st.markdown("### 🧹 (선택) 전체 초기화")
    st.warning("실수 방지: 초기화는 되돌릴 수 없어요. 정말 필요할 때만.")
    if st.button("⚠️ 모든 기록 삭제(초기화)"):
        save_db({"trees": []})
        st.success("초기화 완료! 새로 시작할 수 있어요.")
