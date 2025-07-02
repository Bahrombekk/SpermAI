# src/utils/image_processing.py
import cv2
import base64
from io import BytesIO
from PIL import Image

def process_image(image_path, bbox):
    image = cv2.imread(image_path)
    x1, y1, x2, y2 = map(int, bbox)
    crop = image[y1:y2, x1:x2]
    return crop

def save_cropped_image(image):
    _, buffer = cv2.imencode('.jpg', image)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_str}"