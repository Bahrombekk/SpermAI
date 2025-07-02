# src/models/detector.py
from ultralytics import YOLO
import cv2
import logging

class SpermDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        # Modelingizda faqat "Triks" klassi bor, uni "Live"ga mapping qilamiz
        self.classes = ['Live', 'Dead', 'Immature']
        self.class_map = {
            'Triks': 'Live',
            # Agar boshqa klasslar ham bo'lsa qo'shing:
            # 'Dead_class': 'Dead',
            # 'Immature_class': 'Immature'
        }
        logging.info(f"Detector initialized with model: {model_path}")
        logging.info(f"Model classes: {list(self.model.names.values())}")
    
    def detect(self, image_path):
        try:
            image = cv2.imread(image_path)
            if image is None:
                logging.error(f"Failed to load image: {image_path}")
                raise ValueError("Cannot load image")
            results = self.model(image)
            detections = []
            
            for box in results[0].boxes:
                class_id = int(box.cls)
                model_class_name = self.model.names[class_id]
                app_class_name = self.class_map.get(model_class_name, 'Live')
                
                # Debug uchun
                logging.info(f"Model class: {model_class_name} -> App class: {app_class_name}")
                
                if app_class_name not in self.classes:
                    logging.warning(f"Unknown class {app_class_name}, defaulting to 'Live'")
                    app_class_name = 'Live'
                
                detections.append({
                    'class_name': app_class_name,
                    'bbox': box.xyxy[0].tolist(),
                    'confidence': box.conf.item()
                })
            
            logging.info(f"Detected {len(detections)} objects in {image_path}")
            logging.info(f"Detection summary: {[d['class_name'] for d in detections]}")
            return detections
        except Exception as e:
            logging.error(f"Error in detection: {str(e)}")
            raise
