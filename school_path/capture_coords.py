import cv2
import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("사용법: python capture_coords.py [층수]")
        return

    floor = sys.argv[1]
    img_path = Path(f"floor{floor}.png")
    if not img_path.exists():
        print(f"이미지 없음: {img_path}")
        return

    img = cv2.imread(str(img_path))
    clone = img.copy()
    points = {}

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            node = input(f"노드 이름 입력 (예: {floor}F_3-1): ").strip()
            if node:
                cv2.circle(clone, (x, y), 5, (0, 255, 0), -1)
                cv2.putText(clone, node, (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                points[node] = [int(floor), x, y]
                print(f"[✔] {node} 저장됨: ({x}, {y})")

    cv2.imshow(f"{floor}층 좌표입력", clone)
    cv2.setMouseCallback(f"{floor}층 좌표입력", click_event)

    print("좌표 입력 중... (Esc 키로 종료)")
    while True:
        cv2.imshow(f"{floor}층 좌표입력", clone)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break

    cv2.destroyAllWindows()

    out_file = f"coords_floor{floor}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(points, f, indent=2, ensure_ascii=False)
    print(f"저장 완료: {out_file}")

if __name__ == "__main__":
    main()
