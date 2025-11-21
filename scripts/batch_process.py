import os
import sys
import cv2
import mediapipe as mp

input_dir = "/workspace/pose-factory/input"
output_dir = "/workspace/pose-factory/output/poses"
os.makedirs(output_dir, exist_ok=True)

pose = mp.solutions.pose.Pose()
drawing = mp.solutions.drawing_utils

image_files = [f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg'))]
print(f"Found {len(image_files)} images to process")

for filename in image_files:
    print(f"Processing {filename}...")
    img_path = os.path.join(input_dir, filename)
    img = cv2.imread(img_path)
    
    if img is None:
        print(f"  Error: Could not read {filename}")
        continue
    
    results = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    if results.pose_landmarks:
        print(f"  ✓ Pose detected!")
        drawing.draw_landmarks(img, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)
        output_path = os.path.join(output_dir, filename)
        cv2.imwrite(output_path, img)
        print(f"  Saved: {output_path}")
    else:
        print(f"  ✗ No pose found")

print(f"\nProcessing complete! Check {output_dir}")

