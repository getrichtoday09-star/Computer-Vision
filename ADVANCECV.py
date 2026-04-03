"""
Advanced Sci-Fi Eye & Hand Tracking Control System v3.0
Features:
- Ultra-accurate eye tracking with iris/pupil detection
- Enhanced blink detection with high sensitivity
- Hand gesture recognition for scrolling
- Pinch gesture for volume control
- Full sci-fi visualization with detailed mesh

Controls:
- Eye Movement: Cursor control
- Double Blink: Left Click
- Right Eye Blink: Right Click
- Triple Blink: Exit
- Hand Up/Down: Scroll
- Thumb-Index Pinch: Volume Control
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    packages = [
        'opencv-python',
        'mediapipe',
        'pyautogui',
        'numpy',
        'pycaw',
        'comtypes'
    ]
    
    print("=" * 60)
    print("Installing required packages...")
    print("=" * 60)
    
    for package in packages:
        try:
            print(f"\nInstalling {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--upgrade"], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[OK] {package} installed successfully")
        except:
            print(f"[FAIL] Failed to install {package}")
    
    print("\n" + "=" * 60)
    print("Installation complete!")
    print("=" * 60 + "\n")

# Install and import
try:
    import cv2
    import mediapipe as mp
    import pyautogui
    import numpy as np
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    from ctypes import cast, POINTER
except ImportError:
    install_requirements()
    import cv2
    import mediapipe as mp
    import pyautogui
    import numpy as np
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    from ctypes import cast, POINTER

import time
import math
from collections import deque

class AdvancedEyeHandTracker:
    def __init__(self):
        print("\n" + "=" * 70)
        print("[INIT] INITIALIZING ADVANCED EYE & HAND TRACKING SYSTEM v3.0")
        print("=" * 70)
        
        # Initialize MediaPipe
        self.setup_mediapipe()
        
        # Volume Control Setup
        self.setup_volume_control()
        
        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        pyautogui.FAILSAFE = False
        
        # Camera setup
        self.setup_camera()
        
        # Eye tracking parameters (ENHANCED)
        self.smoothing_frames = 7
        self.eye_positions = deque(maxlen=self.smoothing_frames)
        self.gaze_history = deque(maxlen=10)
        
        # Enhanced blink detection (MORE SENSITIVE)
        self.EYE_AR_THRESH = 0.25  # Increased threshold for better detection
        self.EYE_AR_CONSEC_FRAMES = 2  # Reduced frames needed
        self.blink_counter = 0
        self.blink_times = deque(maxlen=3)
        self.last_blink_time = 0
        self.BLINK_COOLDOWN = 0.25  # Faster cooldown
        
        # Right eye blink
        self.right_blink_counter = 0
        self.last_right_blink = 0
        
        # Hand tracking parameters
        self.scroll_start_y = None
        self.last_scroll_time = 0
        self.SCROLL_COOLDOWN = 0.1
        self.pinch_start = None
        self.last_volume = 0
        
        # Mouse control
        self.mouse_enabled = True
        self.sensitivity = 1.8
        self.dead_zone = 0.02
        
        # Landmark indices
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        self.LEFT_IRIS = [474, 475, 476, 477]
        self.RIGHT_IRIS = [469, 470, 471, 472]
        
        # Enhanced iris tracking points
        self.LEFT_EYE_INNER = [133]
        self.LEFT_EYE_OUTER = [33]
        self.RIGHT_EYE_INNER = [362]
        self.RIGHT_EYE_OUTER = [263]
        
        # Colors (Enhanced Sci-fi theme)
        self.CYAN = (255, 255, 0)
        self.MAGENTA = (255, 0, 255)
        self.GREEN = (0, 255, 0)
        self.BLUE = (255, 200, 0)
        self.RED = (0, 0, 255)
        self.YELLOW = (0, 255, 255)
        self.ORANGE = (0, 165, 255)
        self.PURPLE = (255, 0, 128)
        
        self.print_controls()
    
    def setup_mediapipe(self):
        """Initialize MediaPipe models"""
        try:
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            
            # Face Landmarker
            base_options = python.BaseOptions(model_asset_path=self.download_model('face'))
            face_options = vision.FaceLandmarkerOptions(
                base_options=base_options,
                output_face_blendshapes=False,
                output_facial_transformation_matrixes=False,
                num_faces=1,
                min_face_detection_confidence=0.6,
                min_face_presence_confidence=0.6,
                min_tracking_confidence=0.6
            )
            self.face_detector = vision.FaceLandmarker.create_from_options(face_options)
            
            # Hand Landmarker
            hand_base_options = python.BaseOptions(model_asset_path=self.download_model('hand'))
            hand_options = vision.HandLandmarkerOptions(
                base_options=hand_base_options,
                num_hands=2,
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.hand_detector = vision.HandLandmarker.create_from_options(hand_options)
            
            self.use_new_api = True
            print("[OK] MediaPipe Tasks API initialized (Face + Hands)")
            
        except Exception as e:
            print(f"New API failed: {e}")
            print("Using legacy API...")
            self.mp_face_mesh = mp.solutions.face_mesh
            self.mp_hands = mp.solutions.hands
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.6,
                min_tracking_confidence=0.6
            )
            self.hands = self.mp_hands.Hands(
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.use_new_api = False
            print("[OK] MediaPipe Solutions API initialized (Legacy)")
    
    def setup_volume_control(self):
        """Setup Windows volume control"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
            self.vol_range = self.volume.GetVolumeRange()
            self.min_vol = self.vol_range[0]
            self.max_vol = self.vol_range[1]
            print("[OK] Volume control initialized")
        except Exception as e:
            print(f"[WARNING] Volume control unavailable: {e}")
            self.volume = None
    
    def setup_camera(self):
        """Initialize camera with multiple attempts"""
        self.cap = None
        for camera_index in [0, 1, 2]:
            print(f"Trying camera index {camera_index}...")
            self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            if self.cap.isOpened():
                print(f"[OK] Camera {camera_index} opened")
                break
            self.cap.release()
        
        if not self.cap or not self.cap.isOpened():
            raise Exception("Cannot open camera")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        ret, test_frame = self.cap.read()
        if not ret:
            raise Exception("Cannot read from camera")
        
        print(f"[OK] Camera initialized - {test_frame.shape}")
    
    def download_model(self, model_type):
        """Download required models"""
        if model_type == 'face':
            model_path = 'face_landmarker.task'
            url = 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task'
        else:
            model_path = 'hand_landmarker.task'
            url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
        
        if not os.path.exists(model_path):
            print(f"Downloading {model_type} model...")
            import urllib.request
            urllib.request.urlretrieve(url, model_path)
            print(f"[OK] {model_type} model downloaded")
        return model_path
    
    def print_controls(self):
        """Print control instructions"""
        print("\n" + "=" * 70)
        print("          ADVANCED EYE & HAND TRACKING CONTROLS")
        print("=" * 70)
        print("  EYE CONTROLS:")
        print("    - Look around -> Move cursor (Ultra-precise)")
        print("    - Double blink -> Left Click")
        print("    - Right eye blink -> Right Click")
        print("    - Triple blink -> Exit")
        print("")
        print("  HAND CONTROLS:")
        print("    - Move hand UP -> Scroll UP")
        print("    - Move hand DOWN -> Scroll DOWN")
        print("    - Pinch (thumb-index) -> Volume Control")
        print("")
        print("  KEYBOARD:")
        print("    - ESC -> Exit program")
        print("=" * 70 + "\n")
    
    def calculate_eye_aspect_ratio(self, eye_points):
        """Enhanced EAR calculation"""
        A = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
        B = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
        C = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
        
        if C == 0:
            return 0
        ear = (A + B) / (2.0 * C)
        return ear
    
    def get_enhanced_gaze_position(self, landmarks, frame_w, frame_h):
        """Ultra-accurate gaze tracking using iris center and eye corners"""
        try:
            # Get iris centers
            left_iris = np.array([(landmarks[i].x * frame_w, landmarks[i].y * frame_h) 
                                 for i in self.LEFT_IRIS])
            right_iris = np.array([(landmarks[i].x * frame_w, landmarks[i].y * frame_h) 
                                  for i in self.RIGHT_IRIS])
            
            left_iris_center = np.mean(left_iris, axis=0)
            right_iris_center = np.mean(right_iris, axis=0)
            
            # Get eye corners for reference
            left_inner = np.array([landmarks[self.LEFT_EYE_INNER[0]].x * frame_w,
                                  landmarks[self.LEFT_EYE_INNER[0]].y * frame_h])
            left_outer = np.array([landmarks[self.LEFT_EYE_OUTER[0]].x * frame_w,
                                  landmarks[self.LEFT_EYE_OUTER[0]].y * frame_h])
            right_inner = np.array([landmarks[self.RIGHT_EYE_INNER[0]].x * frame_w,
                                   landmarks[self.RIGHT_EYE_INNER[0]].y * frame_h])
            right_outer = np.array([landmarks[self.RIGHT_EYE_OUTER[0]].x * frame_w,
                                   landmarks[self.RIGHT_EYE_OUTER[0]].y * frame_h])
            
            # Calculate relative iris position within eye
            left_eye_width = np.linalg.norm(left_outer - left_inner)
            right_eye_width = np.linalg.norm(right_outer - right_inner)
            
            left_ratio = (left_iris_center - left_inner) / left_eye_width if left_eye_width > 0 else np.array([0.5, 0.5])
            right_ratio = (right_iris_center - right_inner) / right_eye_width if right_eye_width > 0 else np.array([0.5, 0.5])
            
            # Average both eyes for accuracy
            avg_ratio = (left_ratio + right_ratio) / 2
            
            # Apply enhanced mapping with dead zone
            if abs(avg_ratio[0] - 0.5) < self.dead_zone:
                avg_ratio[0] = 0.5
            if abs(avg_ratio[1] - 0.5) < self.dead_zone:
                avg_ratio[1] = 0.5
            
            # Map to screen coordinates with non-linear scaling for edges
            gaze_x = self.apply_curve(avg_ratio[0]) * frame_w
            gaze_y = self.apply_curve(avg_ratio[1]) * frame_h
            
            return np.array([gaze_x, gaze_y])
            
        except Exception as e:
            return np.array([frame_w // 2, frame_h // 2])
    
    def apply_curve(self, val):
        """Apply smoothing curve for better control"""
        # Sigmoid-like curve for smoother edge control
        centered = (val - 0.5) * 2  # -1 to 1
        curved = centered ** 3 if abs(centered) > 0.3 else centered
        return (curved / 2) + 0.5
    
    def smooth_gaze(self, pos):
        """Advanced smoothing with prediction"""
        self.gaze_history.append(pos)
        if len(self.gaze_history) < 3:
            return pos
        
        # Weighted average with recent positions having more weight
        weights = np.linspace(0.5, 1.0, len(self.gaze_history))
        weighted_avg = np.average(self.gaze_history, axis=0, weights=weights)
        
        return weighted_avg
    
    def detect_blink(self, left_ear, right_ear, current_time):
        """Enhanced blink detection with higher sensitivity"""
        both_eyes_closed = left_ear < self.EYE_AR_THRESH and right_ear < self.EYE_AR_THRESH
        only_right_closed = right_ear < (self.EYE_AR_THRESH - 0.02) and left_ear >= (self.EYE_AR_THRESH + 0.02)
        
        # Double blink detection
        if both_eyes_closed and (current_time - self.last_blink_time) > self.BLINK_COOLDOWN:
            self.blink_counter += 1
            self.blink_times.append(current_time)
            self.last_blink_time = current_time
            
            # Check for double blink
            if len(self.blink_times) >= 2:
                if self.blink_times[-1] - self.blink_times[-2] < 0.5:
                    try:
                        pyautogui.click()
                        print(">> DOUBLE BLINK -> LEFT CLICK")
                    except:
                        pass
                    self.blink_times.clear()
                    return "double"
            
            # Check for triple blink
            if len(self.blink_times) >= 3:
                if self.blink_times[-1] - self.blink_times[-3] < 1.0:
                    print("\n[EXIT] TRIPLE BLINK -> EXITING...")
                    return "triple"
        
        # Right eye blink
        if only_right_closed and (current_time - self.last_right_blink) > self.BLINK_COOLDOWN:
            self.last_right_blink = current_time
            try:
                pyautogui.rightClick()
                print(">> RIGHT BLINK -> RIGHT CLICK")
            except:
                pass
            return "right"
        
        return None
    
    def process_hand_gestures(self, hand_landmarks, frame_h):
        """Process hand gestures for scrolling and volume"""
        if not hand_landmarks:
            self.scroll_start_y = None
            return
        
        # Get hand center (palm)
        palm_y = hand_landmarks[0].y * frame_h
        
        # Scrolling
        current_time = time.time()
        if self.scroll_start_y is not None:
            delta = palm_y - self.scroll_start_y
            
            if abs(delta) > 30 and (current_time - self.last_scroll_time) > self.SCROLL_COOLDOWN:
                scroll_amount = int(delta / 10)
                try:
                    pyautogui.scroll(-scroll_amount)
                    direction = "UP" if scroll_amount < 0 else "DOWN"
                    print(f">> SCROLL {direction}")
                except:
                    pass
                self.last_scroll_time = current_time
        
        self.scroll_start_y = palm_y
        
        # Volume control (pinch gesture)
        thumb_tip = hand_landmarks[4]
        index_tip = hand_landmarks[8]
        
        distance = math.sqrt(
            (thumb_tip.x - index_tip.x)**2 + 
            (thumb_tip.y - index_tip.y)**2
        )
        
        # Pinch detected
        if distance < 0.05 and self.volume:
            vol_level = np.interp(distance, [0.01, 0.05], [self.min_vol, self.max_vol])
            try:
                self.volume.SetMasterVolumeLevel(vol_level, None)
                vol_percent = int(np.interp(vol_level, [self.min_vol, self.max_vol], [0, 100]))
                if abs(vol_percent - self.last_volume) > 5:
                    print(f"[VOL] VOLUME: {vol_percent}%")
                    self.last_volume = vol_percent
            except:
                pass
    
    def draw_advanced_sci_fi_overlay(self, frame, face_landmarks, hand_landmarks_list, 
                                     frame_w, frame_h, gaze_x, gaze_y, left_ear, right_ear):
        """Enhanced sci-fi visualization with detailed mesh"""
        
        # Draw full face mesh with tessellation
        if face_landmarks:
            # Draw all connections for full mesh
            connections = [
                (10, 338), (338, 297), (297, 332), (332, 284), (284, 251), (251, 389),
                (389, 356), (356, 454), (454, 323), (323, 361), (361, 288), (288, 397),
                (397, 365), (365, 379), (379, 378), (378, 400), (400, 377), (377, 152),
                (152, 148), (148, 176), (176, 149), (149, 150), (150, 136), (136, 172),
                (172, 58), (58, 132), (132, 93), (93, 234), (234, 127), (127, 162),
                (162, 21), (21, 54), (54, 103), (103, 67), (67, 109), (109, 10),
                # Additional grid lines
                (33, 246), (246, 161), (161, 160), (160, 159), (159, 158), (158, 157),
                (157, 173), (173, 133), (263, 466), (466, 388), (388, 387), (387, 386),
                (386, 385), (385, 384), (384, 398), (398, 362)
            ]
            
            for connection in connections:
                start = face_landmarks[connection[0]]
                end = face_landmarks[connection[1]]
                
                start_point = (int(start.x * frame_w), int(start.y * frame_h))
                end_point = (int(end.x * frame_w), int(end.y * frame_h))
                
                cv2.line(frame, start_point, end_point, self.CYAN, 1, cv2.LINE_AA)
            
            # Draw eyes with multiple layers
            for eye_indices in [self.LEFT_EYE, self.RIGHT_EYE]:
                eye_points = [(int(face_landmarks[i].x * frame_w), 
                              int(face_landmarks[i].y * frame_h)) for i in eye_indices]
                
                # Outer glow
                for i in range(len(eye_points)):
                    cv2.line(frame, eye_points[i], eye_points[(i+1) % len(eye_points)], 
                            self.MAGENTA, 3, cv2.LINE_AA)
                # Inner line
                for i in range(len(eye_points)):
                    cv2.line(frame, eye_points[i], eye_points[(i+1) % len(eye_points)], 
                            self.GREEN, 1, cv2.LINE_AA)
            
            # Draw iris with multiple circles
            for iris_indices in [self.LEFT_IRIS, self.RIGHT_IRIS]:
                iris_points = [(int(face_landmarks[i].x * frame_w), 
                               int(face_landmarks[i].y * frame_h)) for i in iris_indices]
                center = tuple(np.mean(iris_points, axis=0).astype(int))
                
                cv2.circle(frame, center, 12, self.PURPLE, 2)
                cv2.circle(frame, center, 8, self.MAGENTA, 2)
                cv2.circle(frame, center, 4, self.GREEN, -1)
                cv2.circle(frame, center, 2, self.CYAN, -1)
        
        # Draw hand tracking
        if hand_landmarks_list:
            for hand_landmarks in hand_landmarks_list:
                # Draw hand skeleton
                connections = [
                    (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
                    (0, 5), (5, 6), (6, 7), (7, 8),  # Index
                    (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
                    (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
                    (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
                    (5, 9), (9, 13), (13, 17)  # Palm
                ]
                
                for connection in connections:
                    start = hand_landmarks[connection[0]]
                    end = hand_landmarks[connection[1]]
                    
                    start_point = (int(start.x * frame_w), int(start.y * frame_h))
                    end_point = (int(end.x * frame_w), int(end.y * frame_h))
                    
                    cv2.line(frame, start_point, end_point, self.YELLOW, 2, cv2.LINE_AA)
                
                # Draw finger tips
                fingertips = [4, 8, 12, 16, 20]
                for tip in fingertips:
                    point = hand_landmarks[tip]
                    center = (int(point.x * frame_w), int(point.y * frame_h))
                    cv2.circle(frame, center, 8, self.ORANGE, -1)
                    cv2.circle(frame, center, 10, self.YELLOW, 2)
        
        # Enhanced HUD panel
        panel_h = 180
        cv2.rectangle(frame, (10, 10), (frame_w - 10, panel_h), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (frame_w - 10, panel_h), self.CYAN, 3)
        
        # Title
        cv2.putText(frame, "╔══ NEURAL TRACKING INTERFACE ══╗", (20, 35), 
                   cv2.FONT_HERSHEY_COMPLEX, 0.7, self.CYAN, 2)
        
        # Eye tracking data
        cv2.putText(frame, f"GAZE X: {int(gaze_x):4d} px", (20, 65), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.BLUE, 2)
        cv2.putText(frame, f"GAZE Y: {int(gaze_y):4d} px", (250, 65), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.BLUE, 2)
        
        # Eye status
        left_status = "█ CLOSED" if left_ear < self.EYE_AR_THRESH else "○ OPEN"
        right_status = "█ CLOSED" if right_ear < self.EYE_AR_THRESH else "○ OPEN"
        left_color = self.RED if left_ear < self.EYE_AR_THRESH else self.GREEN
        right_color = self.RED if right_ear < self.EYE_AR_THRESH else self.GREEN
        
        cv2.putText(frame, f"L-EYE: {left_status}", (20, 95), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, left_color, 1)
        cv2.putText(frame, f"EAR: {left_ear:.3f}", (200, 95), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, left_color, 1)
        
        cv2.putText(frame, f"R-EYE: {right_status}", (20, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, right_color, 1)
        cv2.putText(frame, f"EAR: {right_ear:.3f}", (200, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, right_color, 1)
        
        # Hand gesture status
        hand_status = f"HANDS: {len(hand_landmarks_list)} DETECTED" if hand_landmarks_list else "HANDS: NONE"
        hand_color = self.GREEN if hand_landmarks_list else self.RED
        cv2.putText(frame, hand_status, (20, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, hand_color, 2)
        
        # Crosshair
        gaze_point = (int(gaze_x), int(gaze_y))
        if 0 <= gaze_point[0] < frame_w and 0 <= gaze_point[1] < frame_h:
            cv2.drawMarker(frame, gaze_point, self.GREEN, cv2.MARKER_CROSS, 30, 3)
            cv2.circle(frame, gaze_point, 20, self.GREEN, 2)
        
        # Status indicators
        cv2.putText(frame, "● TRACKING", (frame_w - 150, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.GREEN, 2)
        
        return frame
    
    def run(self):
        """Main execution loop"""
        print("\n" + "=" * 70)
        print("[START] STARTING NEURAL TRACKING SYSTEM...")
        print("=" * 70 + "\n")
        
        cv2.namedWindow('Neural Tracking Interface', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Neural Tracking Interface', 1280, 720)
        
        frame_count = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue
            
            frame = cv2.flip(frame, 1)
            frame_h, frame_w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            face_landmarks = None
            hand_landmarks_list = []
            
            # Process face
            try:
                if self.use_new_api:
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                    face_result = self.face_detector.detect(mp_image)
                    if face_result.face_landmarks:
                        face_landmarks = face_result.face_landmarks[0]
                    
                    hand_result = self.hand_detector.detect(mp_image)
                    if hand_result.hand_landmarks:
                        hand_landmarks_list = hand_result.hand_landmarks
                else:
                    face_results = self.face_mesh.process(rgb_frame)
                    if face_results.multi_face_landmarks:
                        face_landmarks = face_results.multi_face_landmarks[0].landmark
                    
                    hand_results = self.hands.process(rgb_frame)
                    if hand_results.multi_hand_landmarks:
                        hand_landmarks_list = [hand.landmark for hand in hand_results.multi_hand_landmarks]
                
                # Process face landmarks
                if face_landmarks:
                    # Get eye points
                    left_eye_points = [(face_landmarks[i].x * frame_w, face_landmarks[i].y * frame_h) 
                                      for i in self.LEFT_EYE]
                    right_eye_points = [(face_landmarks[i].x * frame_w, face_landmarks[i].y * frame_h) 
                                       for i in self.RIGHT_EYE]
                    
                    left_ear = self.calculate_eye_aspect_ratio(left_eye_points)
                    right_ear = self.calculate_eye_aspect_ratio(right_eye_points)
                    
                    # Enhanced gaze tracking
                    gaze_pos = self.get_enhanced_gaze_position(face_landmarks, frame_w, frame_h)
                    smoothed_pos = self.smooth_gaze(gaze_pos)
                    
                    # Map to screen with enhanced precision
                    screen_x = np.interp(smoothed_pos[0], [0, frame_w], [0, self.screen_w]) * self.sensitivity
                    screen_y = np.interp(smoothed_pos[1], [0, frame_h], [0, self.screen_h]) * self.sensitivity
                    
                    screen_x = np.clip(screen_x, 0, self.screen_w - 1)
                    screen_y = np.clip(screen_y, 0, self.screen_h - 1)
                    
                    # Move mouse
                    if self.mouse_enabled:
                        try:
                            pyautogui.moveTo(int(screen_x), int(screen_y), _pause=False)
                        except:
                            pass
                    
                    # Blink detection
                    current_time = time.time()
                    blink_type = self.detect_blink(left_ear, right_ear, current_time)
                    
                    if blink_type == "triple":
                        break
                    
                    # Process hand gestures
                    if hand_landmarks_list:
                        for hand_landmarks in hand_landmarks_list:
                            self.process_hand_gestures(hand_landmarks, frame_h)
                    
                    # Draw visualization
                    frame = self.draw_advanced_sci_fi_overlay(
                        frame, face_landmarks, hand_landmarks_list,
                        frame_w, frame_h, smoothed_pos[0], smoothed_pos[1],
                        left_ear, right_ear
                    )
                else:
                    cv2.putText(frame, "NO FACE DETECTED", (frame_w // 2 - 150, frame_h // 2), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.0, self.RED, 3)
                
            except Exception as e:
                print(f"[WARNING] Processing error: {e}")
            
            cv2.imshow('Neural Tracking Interface', frame)
            
            if cv2.waitKey(1) & 0xFF == 27:
                break
            
            frame_count += 1
        
        self.cleanup()
    
    def cleanup(self):
        """Release resources"""
        print("\n[EXIT] Shutting down...")
        self.cap.release()
        cv2.destroyAllWindows()
        print("[OK] Neural Tracking System terminated\n")

if __name__ == "__main__":
    try:
        tracker = AdvancedEyeHandTracker()
        tracker.run()
    except KeyboardInterrupt:
        print("\n[WARNING] Interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()