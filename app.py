import streamlit as st
import mediapipe as mp
import numpy as np
from io import BytesIO
import tempfile
import os
from PIL import Image, ImageDraw

# Initialize mediapipe pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

# Initialize session state
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp()

# -----------------------------------
# Function 1: Detect Key Landmarks
# -----------------------------------
def detect_keypoints(image_path):
    image = Image.open(image_path).convert('RGB')
    image_array = np.array(image)
    results = pose.process(image_array)
    landmarks = {}
    if results.pose_landmarks:
        h, w = image.size[1], image.size[0]
        for id, lm in enumerate(results.pose_landmarks.landmark):
            landmarks[id] = (int(lm.x * w), int(lm.y * h))
    return image, landmarks

# -----------------------------------
# Function 2: Draw Plumb Line & Measure Deviations
# -----------------------------------
def plumb_line_analysis(image, landmarks):
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)
    ankle_x = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value][0]
    h, w = image.size[1], image.size[0]
    
    # Draw plumb line (vertical green line)
    draw.line([(ankle_x, 0), (ankle_x, h)], fill=(0, 255, 0), width=2)

    key_points = {
        "Ear": landmarks[mp_pose.PoseLandmark.LEFT_EAR.value],
        "Shoulder": landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
        "Hip": landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
        "Knee": landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    }

    deviations = {}
    for part, (x, y) in key_points.items():
        deviation = x - ankle_x
        deviations[part] = deviation
        # Draw circle at landmark
        draw.ellipse([(x-6, y-6), (x+6, y+6)], fill=(0, 0, 255))
        # Draw horizontal line to plumb line
        draw.line([(x, y), (ankle_x, y)], fill=(255, 0, 0), width=1)

    return annotated, deviations

# -----------------------------------
# Function 3: Interpret Posture Based on Deviations
# -----------------------------------
def interpret_posture(deviations, side):
    def classify(value, name):
        abs_val = abs(value)
        if abs_val < 10:
            level = "Neutral"
            score = 100
        elif abs_val < 40:
            level = "Mild"
            score = 85
        elif abs_val < 80:
            level = "Moderate"
            score = 65
        else:
            level = "Severe"
            score = 40
        direction = "Forward" if value > 0 else ("Backward" if value < 0 else "Neutral")
        return f"{name}: {level} {direction} deviation", score

    summary_lines = []
    total_score = 0

    for name, val in deviations.items():
        line, score = classify(val, name)
        summary_lines.append(line)
        total_score += score

    avg_score = total_score / len(deviations)

    # Interpret side-specific posture
    if side.lower() == "left":
        if deviations["Shoulder"] > 80 or deviations["Hip"] > 80:
            suggestion = "Forward-leaning posture detected (Rounded shoulders, anterior pelvic tilt)."
        else:
            suggestion = "Posture on left side appears balanced."
    else:
        if deviations["Ear"] > 60:
            suggestion = "Mild forward head posture detected."
        else:
            suggestion = "Right side posture appears mostly neutral."

    overall_condition = (
        "Excellent" if avg_score > 90 else
        "Good" if avg_score > 75 else
        "Fair" if avg_score > 60 else
        "Poor"
    )

    summary = "\n".join(summary_lines)
    full_report = f"{summary}\n\nSummary: {suggestion}\n\nPosture Score: {avg_score:.1f}/100 ({overall_condition})"
    return full_report, avg_score, overall_condition

# -----------------------------------
# Function 4: Convert CV2 Image for Display
# -----------------------------------
def convert_to_bytes(image):
    buf = BytesIO()
    image.save(buf, format='PNG')
    buf.seek(0)
    return buf

# -----------------------------------
# Streamlit UI
# -----------------------------------
st.set_page_config(page_title="AI Plumb Line Posture Analysis", layout="centered")
st.title("🧍‍♂️ AI-based Plumb Line Posture Analysis")
st.write("Upload your **Left Side** and **Right Side** full-body images for automatic posture assessment.")

col1, col2 = st.columns(2)
with col1:
    left_img = st.file_uploader("Upload LEFT Side View", type=['jpg', 'jpeg', 'png'])
with col2:
    right_img = st.file_uploader("Upload RIGHT Side View", type=['jpg', 'jpeg', 'png'])

if left_img and right_img:
    st.divider()
    for label, file in [("Left", left_img), ("Right", right_img)]:
        # Save uploaded file to temporary directory
        temp_file_path = os.path.join(st.session_state.temp_dir, f"temp_{label}.jpg")
        with open(temp_file_path, "wb") as f:
            f.write(file.getbuffer())

        try:
            image, landmarks = detect_keypoints(temp_file_path)
            
            # Check if landmarks were detected
            if not landmarks:
                st.error(f"❌ No body landmarks detected in {label} side image. Please ensure the full body is visible.")
                continue
            
            annotated, deviations = plumb_line_analysis(image, landmarks)
            report, score, condition = interpret_posture(deviations, label)

            st.subheader(f"📸 {label} Side View Analysis")
            st.image(convert_to_bytes(annotated), caption=f"{label} Side Annotated Image", use_column_width=True)

            st.text_area(f"{label} Side Report", report, height=200, disabled=True)

            # Add visual score bar
            st.progress(score / 100)
            st.markdown(f"**Posture Condition:** {condition}")
        
        except Exception as e:
            st.error(f"❌ Error processing {label} side image: {str(e)}")
            continue

    st.success("✅ Posture analysis complete! Review both sides for asymmetry or tilt patterns.")
else:
    st.info("📤 Please upload both Left and Right side images to begin the analysis.")
