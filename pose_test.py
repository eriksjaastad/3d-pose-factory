import sys

import cv2
import mediapipe as mp


def main() -> None:
  print(f"OpenCV version: {cv2.__version__}")
  print(f"MediaPipe version: {mp.__version__}")

  pose = mp.solutions.pose.Pose()

  if len(sys.argv) < 2:
    print("No image path provided, but imports and Pose() creation worked.")
    return

  image_path = sys.argv[1]
  img = cv2.imread(image_path)
  if img is None:
    print(f"Could not read image: {image_path}")
    return

  results = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

  if results.pose_landmarks:
    print("Pose detected!")
  else:
    print("No pose found.")


if __name__ == "__main__":
  main()



