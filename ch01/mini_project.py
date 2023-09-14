import cv2
import numpy as np

# OpenCV를 이용한 카메라 캡처
cap = cv2.VideoCapture(cv2.CAP_DSHOW + 0)

# 게임 화면 크기 설정
screen_width = 470
screen_height = 640

# 공 초기 위치 설정
ball_x = (screen_width - 100) // 2
ball_y = 400
ball_radius = 10
ball_speed = 7  # 상 하 속도
ball_xvalue = 0  # 좌 우 속도

# 두 번째 공 설정
ball2_x = (screen_width - 100) // 2 + 100
ball2_y = 330
ball2_speed = 5
ball2_xvalue = 0

# 색깔
red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)
yellow = (0, 255, 255)
purple = (255, 0, 255)
sky = (255, 255, 0)

# 블록 설정
block_width = 70
block_height = 20
block_position = []
for i in range(6):
    block_position.append({"x": 10 + i * 75, "y": [20, 45, 70, 95, 120, 145]})

# 바구니 초기 위치 설정
basket_width = 100
basket_height = 20
basket_x = (screen_width - basket_width) // 2
basket_y = screen_height - basket_height


# 주먹 감지 분류기 불러오기
fist_cascade = cv2.CascadeClassifier("C:\Python\opencv-4.x/data/haarcascades/hand.xml")

# 손바닥 감지 분류기 불러오기
palm_cascade = cv2.CascadeClassifier("C:\Python\opencv-4.x/data/haarcascades/palm.xml")

# 점수 초기화
score = 0

# 게임 화면과 카메라 화면을 분리하기 위한 창 생성
cv2.namedWindow("Game")
cv2.namedWindow("Camera")

speed = 0
game_start = False
game_over = False


while True:
    ret, frame = cap.read()
    frame2 = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

    # 게임 시작 전
    if not game_start:
        cv2.putText(
            frame2,
            "Space bar click! = Game Start",
            (70, 300),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 150, 100),
            2,
            cv2.LINE_AA,
        )
        cv2.imshow("Game", frame2)
        cv2.imshow("Camera", ~frame)

        key = cv2.waitKey(10)
        if key == 32:  # 스페이스바를 누르면 게임 시작
            game_start = True
        elif key == 27:  # ESC를 누르면 게임 종료
            break
        continue

    # 게임 종료 시
    if game_over:
        frame2.fill(0)
        cv2.putText(
            frame2,
            f"Score: {score}",
            (120, 300),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (255, 0, 0),
            2,
            cv2.LINE_AA,
        )
        cv2.imshow("Game", frame2)
        cv2.imshow("Camera", ~frame)

        key = cv2.waitKey(10)
        if key == 27:  # ESC를 누르면 게임 종료
            break
        continue

    ball_x += ball_xvalue
    ball_y += ball_speed
    ball2_x += ball2_xvalue
    ball2_y += ball2_speed

    # 공이 화면 아래로 벗어나면 다시 위로 이동
    if ball_y > screen_height:
        ball_x = np.random.randint(20, screen_width - 20)
        ball_y = screen_height // 2
        score -= 3
    if ball2_y > screen_height:
        ball2_x = np.random.randint(20, screen_width - 20)
        ball2_y = screen_height // 2
        score -= 3

    # 공이 화면 좌, 우측으로 벗어나면 화면 안으로 이동
    # 공1
    if ball_x < 10:
        if speed >= 0:
            ball_xvalue = 8 + speed
        else:
            ball_xvalue = 8 + speed * (-1)

    if ball_x > screen_width - 10:
        if speed <= 0:
            ball_xvalue = -8 + speed
        else:
            ball_xvalue = -8 + speed * (-1)

    # 공2
    if ball2_x < 10:
        ball2_xvalue = 7
    if ball2_x > screen_width - 10:
        ball2_xvalue = -7

    # 공이 화면 위를 벗어나면 아래로 이동
    if ball_y <= 10:
        ball_speed = 7
    if ball2_y <= 10:
        ball2_speed = 7

    # 주먹 감지
    fist = fist_cascade.detectMultiScale(frame, scaleFactor=1.5, minNeighbors=4)
    # 손바닥 감지
    palm = palm_cascade.detectMultiScale(frame, scaleFactor=1.2, minNeighbors=1)
    if len(fist):
        for x, y, w, h in fist:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    if len(palm):
        for x2, y2, w2, h2 in palm:
            cv2.rectangle(frame, (x2, y2), (x2 + w2, y2 + h2), (0, 0, 255), 2)

    # 주먹이 감지되면 바구니 왼쪽 이동, 손바닥이 감지되면 바구니 오른쪽 이동
    if len(fist) > 0 or len(palm) > 0:
        number = len(palm)
        number2 = len(fist)
        if number > 1:
            number = 1
        if number2 > 1:
            number2 = 1
        if len(fist) > 0:
            cv2.putText(
                frame,
                f"Left Move",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                1,
                cv2.LINE_AA,
            )
        if len(palm) > 0:
            cv2.putText(
                frame,
                f"right Move",
                (450, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                1,
                cv2.LINE_AA,
            )
        basket_x = max(
            0,
            min(
                screen_width - basket_width,
                basket_x + (number - number2) * 20,
            ),
        )

    # 바구니 그리기
    cv2.rectangle(
        frame2,
        (basket_x, basket_y),
        (basket_x + basket_width, basket_y + basket_height),
        (200, 200, 200),
        -1,
    )

    # 공과 바구니 충돌 검사
    if (
        ball_x + ball_radius >= basket_x
        and ball_x - ball_radius <= basket_x + basket_width
        and ball_y + ball_radius >= screen_height - basket_height
    ):
        # 바구니의 좌측 부분과 충돌
        if ball_x - ball_radius < basket_x + (basket_width // 2):
            ball_xvalue = np.random.randint(-9, -7)
            if ball_x - ball_radius < basket_x + (basket_width // 5):
                speed = np.random.randint(3, 5)
            else:
                speed = 0

        # 바구니의 우측 부분과 충돌
        elif (
            ball_x - ball_radius > basket_x + (basket_width // 2)
            and ball_x - ball_radius <= basket_x + basket_width
        ):
            ball_xvalue = np.random.randint(8, 10)
            if ball_x - ball_radius > basket_x + 4 * (basket_width // 5):
                speed = np.random.randint(-4, -2)
            else:
                speed = 0

        # 바구니 가운데 부분에 충돌
        else:
            ball_xvalue = 0

        # 공과 바구니 충돌했을 때
        ball_speed = np.random.randint(-11, -7)

    # 공2와 바구니 충돌
    if (
        ball2_x + ball_radius >= basket_x
        and ball2_x - ball_radius <= basket_x + basket_width
        and ball2_y + ball_radius >= screen_height - basket_height
    ):
        # 바구니의 좌측 부분과 충돌
        if ball2_x - ball_radius < basket_x + (basket_width // 2):
            ball2_xvalue = -7

        # 바구니의 우측 부분과 충돌
        elif (
            ball2_x - ball_radius > basket_x + (basket_width // 2)
            and ball2_x - ball_radius <= basket_x + basket_width
        ):
            ball2_xvalue = 7
        # 바구니 가운데 부분에 충돌
        else:
            ball2_xvalue = 0

        # 공2와 바구니 충돌했을 때
        ball2_speed = -7

    # 공과 벽돌 충돌
    i2 = 0
    ball_xloop = True
    while i2 < len(block_position) and ball_xloop:
        j2 = 0
        while j2 < len(block_position[i2]["y"]):
            if (
                ball_x + ball_radius >= block_position[i2]["x"]
                and ball_x - ball_radius <= block_position[i2]["x"] + block_width
                and ball_y - ball_radius <= block_position[i2]["y"][j2] + block_height
            ):
                # 충돌한 블록 제거
                block_position[i2]["y"].pop(j2)
                score += 5
                if ball_speed < 0:
                    ball_speed = np.random.randint(7, 11)
                elif ball_speed > 0:
                    ball_speed = np.random.randint(-10, -8)
                if (
                    ball_x + ball_radius == block_position[i2]["x"]
                    or ball_x - ball_radius == block_position[i2]["x"] + block_width
                ):
                    ball_xvalue = ball_xvalue * (-1)
                ball_xloop = False
                break
            else:
                j2 += 1
        else:
            i2 += 1

    # 공2와 벽돌 충돌
    i3 = 0
    ball2_xloop = True
    while i3 < len(block_position) and ball2_xloop:
        j3 = 0
        while j3 < len(block_position[i3]["y"]):
            if (
                ball2_x + ball_radius >= block_position[i3]["x"]
                and ball2_x - ball_radius <= block_position[i3]["x"] + block_width
                and ball2_y - ball_radius <= block_position[i3]["y"][j3] + block_height
            ):
                # 충돌한 블록 제거
                block_position[i3]["y"].pop(j3)
                score += 5
                if ball2_speed < 0:
                    ball2_speed = 7
                elif ball2_speed > 0:
                    ball2_speed = -7
                if (
                    ball2_x + ball_radius == block_position[i3]["x"]
                    or ball2_x - ball_radius == block_position[i3]["x"] + block_width
                ):
                    ball2_xvalue = ball2_xvalue * (-1)
                ball2_xloop = False
                break
            else:
                j3 += 1
        else:
            i3 += 1

    # 벽돌 그리기
    for i in range(len(block_position)):
        for j in range(len(block_position[i]["y"])):
            if j == 0:
                cv2.rectangle(
                    frame2,
                    (block_position[i]["x"], block_position[i]["y"][j]),
                    (
                        block_position[i]["x"] + block_width,
                        block_position[i]["y"][j] + block_height,
                    ),
                    green,
                    -1,
                )
            elif j == 1:
                cv2.rectangle(
                    frame2,
                    (block_position[i]["x"], block_position[i]["y"][j]),
                    (
                        block_position[i]["x"] + block_width,
                        block_position[i]["y"][j] + block_height,
                    ),
                    red,
                    -1,
                )
            elif j == 2:
                cv2.rectangle(
                    frame2,
                    (block_position[i]["x"], block_position[i]["y"][j]),
                    (
                        block_position[i]["x"] + block_width,
                        block_position[i]["y"][j] + block_height,
                    ),
                    blue,
                    -1,
                )
            elif j == 3:
                cv2.rectangle(
                    frame2,
                    (block_position[i]["x"], block_position[i]["y"][j]),
                    (
                        block_position[i]["x"] + block_width,
                        block_position[i]["y"][j] + block_height,
                    ),
                    purple,
                    -1,
                )
            elif j == 4:
                cv2.rectangle(
                    frame2,
                    (block_position[i]["x"], block_position[i]["y"][j]),
                    (
                        block_position[i]["x"] + block_width,
                        block_position[i]["y"][j] + block_height,
                    ),
                    yellow,
                    -1,
                )
            elif j == 5:
                cv2.rectangle(
                    frame2,
                    (block_position[i]["x"], block_position[i]["y"][j]),
                    (
                        block_position[i]["x"] + block_width,
                        block_position[i]["y"][j] + block_height,
                    ),
                    sky,
                    -1,
                )

    # 점수 표시
    cv2.putText(
        frame2,
        f"Score: {score}",
        (10, 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )

    # 공 그리기
    cv2.circle(frame2, (ball_x, ball_y), ball_radius, (255, 150, 150), -1)
    cv2.circle(frame2, (ball2_x, ball2_y), ball_radius, (150, 255, 150), -1)

    # 카메라 화면과 게임 화면을 각각의 창에 표시
    cv2.imshow("Game", frame2)
    cv2.imshow("Camera", ~frame)

    # 벽돌을 다 깨면 게임종료
    if all(not block["y"] for block in block_position):
        game_over = True

    # 종료 조건 (ESC 키를 누르면 게임 종료)
    if cv2.waitKey(10) == 27:
        break


# 카메라 캡처 중단 및 창 닫기
cap.release()
cv2.destroyAllWindows()
