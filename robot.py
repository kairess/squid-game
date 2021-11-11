import cv2
from dynamikontrol import Module, Timer
from playsound import playsound

MOVE_THRESHOLD = 2000

robot_status = 'blind' # (blind, speaking, looking)
player_status = 'alive' # (alive, dead)

module = Module()
module.motor.angle(85) # 앞 85, 뒤 -85

cap = cv2.VideoCapture(0)

sub = cv2.createBackgroundSubtractorKNN(history=1, dist2Threshold=10000, detectShadows=False)

timer = Timer()

def start_blind():
    global robot_status
    robot_status = 'blind'

    module.motor.angle(-85, period=3, func=start_speaking) # 모터 뒤로 회전

def start_speaking():
    global robot_status
    robot_status = 'speaking'

    playsound('assets/sound.wav')
    start_looking()
    # timer.callback_after(func=start_looking, after=3)

def set_looking():
    global robot_status
    robot_status = 'looking'

def start_looking():
    module.motor.angle(85) # 모터 앞으로 회전

    timer.callback_after(func=set_looking, after=2) # 카메라 포커스 및 노출 조정 고려하여 2초뒤부터 감지 시작

    timer.callback_after(func=start_blind, after=5)

# 시작하면 눈을 가린다
start_blind()

while cap.isOpened():
    ret, img = cap.read()
    if not ret:
        break

    mask = sub.apply(img)

    # https://docs.opencv.org/master/d9/d61/tutorial_py_morphological_ops.html
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    # mask = cv2.dilate(mask, kernel, iterations=2)

    diff = (mask.astype('float') / 255.).sum()

    cv2.putText(mask, text=robot_status, org=(10, 30), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255,255,255), thickness=2)

    if robot_status == 'looking' and diff > MOVE_THRESHOLD:
        player_status = 'dead'

    if player_status != 'alive':
        cv2.putText(mask, text='YOU DIED', org=(180, 500), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=10, color=(127,127,127), thickness=20)
        cv2.putText(img, text='YOU DIED', org=(180, 500), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=10, color=(0,0,255), thickness=20)

    cv2.imshow('img', img)
    cv2.imshow('mask', mask)
    if cv2.waitKey(1) == ord('q'):
        break

timer.stop()
module.motor.angle(85)
module.disconnect()
