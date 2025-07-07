import json
import heapq
import cv2
from pathlib import Path
import streamlit as st

# ------------------- 0. 좌표 통합 -------------------
NODE_COORDS = {}
for floor in range(1, 6):
    json_path = Path(f"coords_floor{floor}.json")
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            NODE_COORDS.update(json.load(f))

# ------------------- 1. 복도 및 계단 연결 -------------------
corridor_1 = [
    "1F_계단_왼쪽", "사랑반1", "사랑반2",  "교장실",
    "교육행정실", "중앙현관", "보건실", "1F_계단_중앙", "식당",
    "조리실", "조리원휴게실", "영양사실", "급식창고1", "급식창고2",
    "창고", "분리수거창고", "분리수거장", "당직실", "특수교육부", "1F_화장실", "1F_계단_오른쪽", "1F_급식실_계단"
]

corridor_2 = [
    "2F_계단_왼쪽", "1-9", "1-10", "학생회자치회의실", "wee class",
    "1-11",  "1-12",  "중앙라운지", "방송실",
    "통합교무실(교무,연구,과정)", "옥외베란다", "청이룸1(스터디룸)",
    "청이룸2(스터디룸)", "학교운영회회의실", "평가관리실", "회의실",
    "청명꿈마루", "체육건강예술부", "체력단련실", "실내체육실",
    "현관", "다빈치실", "운동장", "수리과학부", "물지실", "교무서고",
    "2F_화장실", "2F_계단_중앙", "2F_계단_오른쪽", "2F_급식실_계단"
]

corridor_3 = [
    "3F_계단_왼쪽", "1-5", "1-6",  "1-7", "1-8", "상담실",
    "진로진학상담부", "2-4", "2-5", "2-6", "2-7", "2-8", "2-9",
    "2-10", "자판기", "교육정보부", "컴퓨터실1실", "청소도구실",
    "서창관3-1", "서창관3-2", "해온실", "인문사회교과부", "여직원휴게실",
    "생물준비실", "생물실",  "3F_화장실",
    "3F_계단_중앙", "3F_계단_청명직업마루앞", "3F_계단_오른쪽", "3F_급식실_계단", "2학년_교무실"
]

corridor_4 = [
    "4F_계단_왼쪽", "3-9", "3-10", "3-11", "3-12", "1-1", "1-2",
    "1-3", "1-4", "학생상담실", "생활안전교육부", "음악실", "기자재",
    "음악실_밴드부", "율솔_다목적강당", "2-1", "2-2", "2-3", "도서관",
    "빛가람라운지", "옹달샘카페", "라미갤러리", "미술준비실", "미술실", "기술준비실", "기술실", "밴드부(구)",
    "4F_화장실",  "4F_계단_중앙", "4F_계단_도서관앞",  "4F_계단_기술실쪽", "4F_급식실_계단"
]

corridor_5 = [
    "5F_계단_왼쪽", "3-1", "3-2", "3-3", "3-4", "행정서고", "3-5", "3-6",
    "3-7", "3-8", "3학년부", "대입전략실", "지성관5층남직원휴게실",
    "준비실", "체육관1(청명관)",
    "5F_계단_중앙", "5F_계단_오른쪽"
]

# ------------------- 2. EDGES 생성 -------------------
EDGES = []
for corridor in [corridor_5, corridor_4, corridor_3, corridor_2, corridor_1]:
    EDGES.extend([(a, b, 1) for a, b in zip(corridor, corridor[1:])])

# 왼쪽 계단 연결 (5F ~ 1F)
for f in range(5, 1, -1):  # 5 → 4, 4 → 3, ..., 2 → 1
    u = f"{f}F_계단_왼쪽"
    d = f"{f-1}F_계단_왼쪽"
    if u in NODE_COORDS and d in NODE_COORDS:
        EDGES.append((u, d, 5))
        EDGES.append((d, u, 5))  # 양방향 연결

for f in range(5, 1, -1):  # 5 → 4, 4 → 3, ..., 2 → 1
    u = f"{f}F_계단_중앙"
    d = f"{f-1}F_계단_중앙"
    if u in NODE_COORDS and d in NODE_COORDS:
        EDGES.append((u, d, 5))
        EDGES.append((d, u, 5))  # 양방향 연결

for f in range(5, 1, -1):  # 5 → 4, 4 → 3, ..., 2 → 1
    u = f"{f}F_계단_오른쪽"
    d = f"{f-1}F_계단_오른쪽"
    if u in NODE_COORDS and d in NODE_COORDS:
        EDGES.append((u, d, 5))
        EDGES.append((d, u, 5))  # 양방향 연결

# 사용자 정의 계단 연결 (급식실 쪽 계단)
for f in range(1, 4):  # 1F ~ 3F → 2F ~ 4F 연결
    u = f"{f}F_급식실_계단" if f == 1 else f"{f}F_급식실_계단"
    d = f"{f+1}F_급식실_계단"
    if u in NODE_COORDS and d in NODE_COORDS:
        EDGES.append((u, d, 5))
        EDGES.append((d, u, 5))  # 양방향 연결



EDGES.append(("1F_중앙현관", "1F_급식실", 2))
EDGES.append(("4F_화장실", "라미갤러리", 2))
EDGES.append(("보건실", "1F_계단_중앙", 1))  # 중앙 계단도 선택 가능하게
EDGES.append(("보건실", "중앙현관", 5))
EDGES.append(("중앙라운지", "청이룸1(스터디룸)", 1))
EDGES.append(("중앙라운지", "2F_계단_중앙", 0.5))
# 급식실 계단은 더 빠르다고 명시
EDGES.append(("생물실", "3F_급식실_계단", 0.5))
EDGES.append(("2학년_교무실", "3F_계단_중앙", 1))
EDGES.append(("2학년_교무실", "3F_계단_오른쪽", 0.1))
EDGES.append(("해온실", "2학년_교무실", 1))
EDGES.append(("1-4", "4F_계단_오른쪽", 1))




# 5F_계단_중앙 → 3-8 바로 연결 (우회 방지용)
if "5F_계단_중앙" in NODE_COORDS and "3-8" in NODE_COORDS:
    EDGES.append(("5F_계단_중앙", "3-8", 1))  # 거리 1은 복도보다 더 짧게 설정




print(f"[INFO] Generated {len(EDGES)} edges")
print("샘플 10개:", EDGES[:10])
# ------------------- 2. 다익스트라 -------------------
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

# ------------------- 3. 이미지에 경로 그리기 -------------------
def draw_path(path):
    images = {}
    for f in range(1, 6):
        img_path = Path(f"floor{f}.png")
        if img_path.exists():
            images[f] = cv2.imread(str(img_path))

    for i in range(len(path)-1):
        a, b = path[i], path[i+1]
        f1, x1, y1 = NODE_COORDS[a]
        f2, x2, y2 = NODE_COORDS[b]
        if f1 == f2 and f1 in images:
            cv2.line(images[f1], (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.circle(images[f1], (x1, y1), 4, (0, 255, 0), -1)
            cv2.putText(images[f1], a, (x1+5, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
    return images

# ------------------- 4. Streamlit UI -------------------
st.set_page_config(page_title="청명고 최단 경로 안내", layout="wide")
st.title("🏫 청명고 최단 경로 안내기")

start = st.selectbox("출발지", sorted(NODE_COORDS.keys()))
end = st.selectbox("도착지", sorted(NODE_COORDS.keys()))

if st.button("최단 경로 찾기"):
    path, cost = dijkstra(start, end)
    st.success(f"총 거리: {cost}")
    st.write("➡️ 이동 경로:")
    st.markdown(" → ".join(path))

    images = draw_path(path)
    for floor, img in sorted(images.items()):
        st.subheader(f"{floor}층 경로")
        st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), channels="RGB")
