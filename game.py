import cv2
import mediapipe as mp
import time
import random

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mphands = mp.solutions.hands

cap = cv2.VideoCapture(0)
hands = mphands.Hands(static_image_mode=False, max_num_hands=2)

start_time = None
draw_timer = None
time_left_now = None
timer_started = False
hold_for_play = False
game_over_text = ""
player_move, computer_move = "", ""
success = False
played = False

def is_left_hand(hands_module, hand_landmarks):
    return hand_landmarks.landmark[hands_module.HandLandmark.WRIST].x < hand_landmarks.landmark[hands_module.HandLandmark.MIDDLE_FINGER_TIP].x

def get_finger_status(hand_landmarks, finger_name):
    finger_id_map = {
        "index": 8,
        "middle": 12,
        "ring": 16,
        "pinky": 20
        }
    
    finger_tip_y = hand_landmarks.landmark[finger_id_map[finger_name]].y
    finger_mcp_y = hand_landmarks.landmark[finger_id_map[finger_name] - 2].y

    return finger_tip_y < finger_mcp_y

def get_thumb_status(hands_module, hand_landmarks):
    thumb_tip_x = hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP].x
    thumb_mcp_x = hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP - 2].x
    thumb_ip_x = hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP - 1].x
    is_left = is_left_hand(hands_module, hand_landmarks)

    return thumb_tip_x > thumb_ip_x > thumb_mcp_x if is_left else thumb_tip_x < thumb_ip_x < thumb_mcp_x

def get_move(hands_module, hand_landmarks):
        current_state = ""
        thumb_status = get_thumb_status(hands_module, hand_landmarks)
        current_state += "1" if thumb_status else "0"

        index_status = get_finger_status(hand_landmarks, 'index')
        current_state += "1" if index_status else "0"

        middle_status = get_finger_status(hand_landmarks, 'middle')
        current_state += "1" if middle_status else "0"

        ring_status = get_finger_status(hand_landmarks, 'ring')
        current_state += "1" if ring_status else "0"

        pinky_status = get_finger_status(hand_landmarks, 'pinky')
        current_state += "1" if pinky_status else "0"

        if current_state == "00000":
            return "Rock"
        elif current_state == "11111":
            return "Paper"
        elif current_state == "01100":
            return "Scissors"
        else:
            return "UNKNOWN"

def display_text_bottom(text):
    # text settings:
    color = (0, 0, 0)
    thickness = 1
    font_scale = 0.5
    cv2.putText(image, text, (10, 450), cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                color, thickness, cv2.LINE_4)

def display_text_top(text):
    color = (0, 255, 255)
    thickness = 2
    font_scale = 0.75
    cv2.putText(image, text, (150, 50), cv2.FONT_HERSHEY_COMPLEX, font_scale,
                color, thickness, cv2.LINE_4)

def calculate_game_state(player_move, computer_move):
    winning_move = {"Rock": "Scissors", "Paper": "Rock", "Scissors": "Paper"}

    if player_move == computer_move:
        return 0    # draw
    elif winning_move[player_move] == computer_move:
        return 1    # player win
    else:
        return -1   # player loss

def get_computer_move(player_move):
    """
        Add your code here
    """
    moves = ["Rock", "Paper", "Scissors"]
    return moves[random.randint(0, 2)]

while True:
    if timer_started:
        now_time = time.time()
        time_elapsed = now_time - start_time
        if time_elapsed >= 1:
            time_left_now -= 1
            start_time = now_time
            if time_left_now <= 0:
                hold_for_play = True
                timer_started = False

    data, image = cap.read()
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mphands.HAND_CONNECTIONS)
            p_move = get_move(mphands, hand_landmarks)

            if hold_for_play and p_move != "UNKNOWN":
                hold_for_play = False
                success = True
                draw_timer = time.time()

                player_move = p_move
                computer_move = get_computer_move(player_move)
                won = calculate_game_state(player_move, computer_move)
                computer_played = "You: " + player_move + " | Computer: " + computer_move

                if won == 1:
                    game_over_text = "You've won!"
                elif won == -1:
                    game_over_text = "You've lost!"
                else:
                    game_over_text = "It's a draw!"

            elif hold_for_play and p_move == "UNKNOWN":
                hold_for_play = False
                success = False

    if not hold_for_play and not timer_started and played:
        if success:
            display_text_bottom(f"{game_over_text} | You played: {player_move} | Computer played: {computer_move}")
        else:
            display_text_bottom(f"Please try again, unable to determine player move")

    label_text = "PRESS SPACE TO START!"
    if hold_for_play:
        label_text = "PLAY NOW!"
    elif timer_started:
        label_text = "PLAY STARTS IN " + str(time_left_now)
    display_text_top(label_text)
    

    cv2.imshow('Rock Paper Scissors Game', image)

    # Start game with space
    if cv2.waitKey(1) == 32:
        print("pressed space")
        played = True
        start_time = time.time()
        timer_started = True
        time_left_now = 3

    # Exit game with esc
    if cv2.waitKey(1) == 27:
        print("Exited game!")
        break

cv2.destroyAllWindows()
cap.release()