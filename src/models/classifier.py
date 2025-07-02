# src/models/classifier.py
from ultralytics import YOLO
import cv2
import numpy as np
import logging

class SpermClassifier:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.classes = ['Normal', 'Abnormal', 'Other']
        # Modelingizdagi real klasslar bilan to'g'ri mapping
        self.class_map = {
            'Normal_Sperm': 'Normal',
            'Abnormal_Sperm': 'Abnormal', 
            'Non-Sperm': 'Other'
        }
        logging.info(f"Classifier initialized with model: {model_path}")
        logging.info(f"Model classes: {list(self.model.names.values())}")
    
    def classify(self, image):
        try:
            image_resized = cv2.resize(image, (224, 224))
            results = self.model(image_resized)
            class_id = int(results[0].probs.top1)
            model_class_name = self.model.names[class_id]
            app_class_name = self.class_map.get(model_class_name, 'Other')
            
            # Debug uchun
            logging.info(f"Model class: {model_class_name} -> App class: {app_class_name}")
            
            if app_class_name not in self.classes:
                logging.warning(f"Unknown class {app_class_name}, defaulting to 'Other'")
                app_class_name = 'Other'
            
            result = {
                'class_name': app_class_name,
                'confidence': results[0].probs.top1conf.item()
            }
            
            return result
        except Exception as e:
            logging.error(f"Error in classification: {str(e)}")
            raise