import json
import heapq
from pathlib import Path
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ------------------- 0. 좌표 통합 -------------------
NODE_COORDS = {}
for floor in range(1, 6):
    json_path = Path(f"coords_floor{floor}.json")
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            NODE_COORDS.update(json.load(f))

# ------------------- 1. 복도 및 계단 연결 -------------------
corridors = {
    1: ["1F_계단_왼쪽", "사랑반1", "사랑반2", "교장실", "교육행정실", "중앙현관", "보건실", "1F_계단_중앙", "식당",
        "조리실", "조리원휴게실", "영양사실", "급식창고1", "급식창고2", "창고", "분리수거창고", "분리수거장", "당직실", "특수교육부", "1F_화장실", "1F_계단_오른쪽", "1F_급식실_계단"],
    2: ["2F_계단_왼쪽", "1-9", "1-10", "학생회자치회의실", "wee class", "1-11", "1-12", "중앙라운지", "방송실",
        "통합교무실(교무,연구,과정)", "옥외베란다", "청이룸1(스터디룸)", "청이룸2(스터디룸)", "학교운영회회의실", "평가관리실", "회의실",
        "청명꿈마루", "체육건강예술부", "체력단련실", "실내체육실", "현관", "다빈치실", "운동장", "수리과학부", "물지실", "교무서고",
        "2F_화장실", "2F_계단_중앙", "2F_계단_오른쪽", "2F_급식실_계단"],
    3: ["3F_계단_왼쪽", "1-5", "1-6", "1-7", "1-8", "상담실", "진로진학상담부", "2-4", "2-5", "2-6", "2-7", "2-8", "2-9",
        "2-10", "자판기", "교육정보부", "컴퓨터실1실", "청소도구실", "서창관3-1", "서창관3-2", "해온실", "인문사회교과부", "여직원휴게실",
        "생물준비실", "생물실", "3F_화장실", "3F_계단_중앙", "3F_계단_청명직업마루앞", "3F_계단_오른쪽", "3F_급식실_계단", "2학년_교무실"],
    4: ["4F_계단_왼쪽", "3-9", "3-10", "3-11", "3-12", "1-1", "1-2", "1-3", "1-4", "학생상담실", "생활안전교육부", "음악실",
        "기자재", "음악실_밴드부", "율솔_다목적강당", "2-1", "2-2", "2-3", "도서관", "빛가람라운지", "옹달샘카페", "라미갤러리",
        "미술준비실", "미술실", "기술준비실", "기술실", "밴드부(구)", "4F_화장실", "4F_계단_중앙", "4F_계단_도서관앞",
        "4F_계단_기술실쪽", "4F_급식실_계단"],
    5: ["5F_계단_왼쪽", "3-1", "3-2", "3-3", "3-4", "행정서고", "3-5", "3-6", "3-7", "3-8", "3학년부", "대입전략실",
        "지성관5층남직원휴게실", "준비실", "체육관1(청명관)", "5F_계단_중앙", "5F_계단_오른쪽"]
}

# ------------------- 2. EDGES 생성 -------------------
EDGES = []
for corridor in corridors.values():
    EDGES.extend([(a, b, 1) for a, b in zip(corridor, corridor[1:])])

# 계단 연결
for f in range(5, 1, -1):
    for t in ["왼쪽", "중앙", "오른쪽"]:
        u, d = f"{f}F_계단_{t}", f"{f-1}F_계단_{t}"
        if u in NODE_COORDS and d in NODE_COORDS:
            EDGES.append((u, d, 5))
            EDGES.append((d, u, 5))

for f in range(1, 4):
    u, d = f"{f}F_급식실_계단", f"{f+1}F_급식실_계단"
    if u in NODE_COORDS and d in NODE_COORDS:
        EDGES.append((u, d, 5))
        EDGES.append((d, u, 5))

# 기타 연결
EDGES += [
    ("1F_중앙현관", "1F_급식실", 2),
    ("4F_화장실", "라미갤러리", 2),
    ("보건실", "1F_계단_중앙", 1),
    ("보건실", "중앙현관", 5),
    ("중앙라운지", "청이룸1(스터디룸)", 1),
    ("중앙라운지", "2F_계단_중앙", 0.5),
    ("생물실", "3F_급식실_계단", 0.5),
    ("2학년_교무실", "3F_계단_중앙", 1),
    ("2학년_교무실", "3F_계단_오른쪽", 0.1),
    ("해온실", "2학년_교무실", 1),
    ("1-4", "4F_계단_오른쪽", 1),
    ("5F_계단_중앙", "3-8", 1)
]

# ------------------- 3. 다익스트라 -------------------
def dijkstra(start, end):
    graph = {}
    for a, b, w in EDGES:
        graph.setdefault(a, []).append((b, w))
        graph.setdefault(b, []).append((a, w))

    dist = {node: float("inf") for node in NODE_COORDS}
    prev = {}
    dist[start] = 0
    queue = [(0, start)]

    while queue:
        cost, u = heapq.heappop(queue)
        if u == end:
            break
        for v, weight in graph.get(u, []):
            alt = cost + weight
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(queue, (alt, v))

    path = []
    node = end
    while node in prev:
        path.append(node)
        node = prev[node]
    path.append(start)
    path.reverse()
    return path, dist[end]

# ------------------- 4. 이미지에 경로 그리기 (PIL) -------------------
def draw_path_pil(path, node_coords):
    images = {}
    for f in range(1, 6):
        img_path = Path(f"floor{f}.png")
        if img_path.exists():
            images[f] = Image.open(img_path).convert("RGB")

    for i in range(len(path)-1):
        a, b = path[i], path[i+1]
        f1, x1, y1 = node_coords[a]
        f2, x2, y2 = node_coords[b]
        if f1 == f2 and f1 in images:
            draw = ImageDraw.Draw(images[f1])
            draw.line((x1, y1, x2, y2), fill=(255, 0, 0), width=3)
            draw.ellipse((x1-4, y1-4, x1+4, y1+4), fill=(0, 255, 0))
            draw.text((x1+5, y1-10), a, fill=(255, 255, 255))

    return images

# ------------------- 5. Streamlit UI -------------------
st.set_page_config(page_title="청명고 최단 경로 안내", layout="wide")
st.title("🏫 청명고 최단 경로 안내기")
with st.expander("📋 가능한 공간 목록 보기"):
    st.write(", ".join(sorted(NODE_COORDS.keys())))


start = st.text_input("출발지를 입력하세요 (예: 1-4)")
end = st.text_input("도착지를 입력하세요 (예: 보건실)")

if start not in NODE_COORDS or end not in NODE_COORDS:
    st.error("입력한 출발지 또는 도착지가 유효하지 않습니다.")
else:
    path, cost = dijkstra(start, end)
    st.success(f"총 거리: {cost}")
    st.markdown("➡️ **이동 경로**")
    st.markdown(" → ".join(path))

    images = draw_path_pil(path, NODE_COORDS)
    for floor, img in sorted(images.items()):
        st.subheader(f"{floor}층 경로")
        st.image(img, use_column_width=True)

