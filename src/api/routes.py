# src/api/routes.py
from flask import Blueprint, request, jsonify, render_template, session
from src.models.detector import SpermDetector
from src.models.classifier import SpermClassifier
from src.utils.image_processing import process_image, save_cropped_image
from src.api.errors import bad_request
import os
from datetime import datetime
import logging

bp = Blueprint('main', __name__)

def init_routes(app):
    detector = SpermDetector(app.config['models']['detection'])
    classifier = SpermClassifier(app.config['models']['classification'])
    
    app.logger.info("Models loaded successfully")
    
    @bp.route('/')
    def index():
        return render_template('index.html')
    
    @bp.route('/report')
    def report():
        results = session.get('analysis_results', {
            'stats': {'Live': 0, 'Dead': 0, 'Immature': 0},
            'classification': {'Normal': 0, 'Abnormal': 0, 'Other': 0},
            'total_cells': 0
        })
        app.logger.info(f"Report accessed with results: {results}")
        return render_template('report.html',
                             stats=results['classification'],
                             total_cells=results['total_cells'],
                             current_date=datetime.now().strftime('%d.%m.%Y'),
                             current_time=datetime.now().strftime('%H:%M'))
    
    @bp.route('/analyze', methods=['POST'])
    def analyze_image():
        if 'file' not in request.files:
            return bad_request('No file uploaded')
        
        file = request.files['file']
        if file.filename == '':
            return bad_request('No file selected')
        
        allowed_extensions = {'jpg', 'jpeg', 'png', 'tiff'}
        if not '.' in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return bad_request('Unsupported file format. Please upload JPG, PNG, or TIFF.')

        upload_folder = app.config['paths']['upload_folder']
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, file.filename)
        file.save(image_path)
        
        try:
            # Detection
            detections = detector.detect(image_path)
            app.logger.info(f"Total detections: {len(detections)}")
            
            # Initialize counters
            stats = {'Live': 0, 'Dead': 0, 'Immature': 0}
            classification_results = {'Normal': 0, 'Abnormal': 0, 'Other': 0}
            cropped_images = []
            
            # Process each detection
            for i, det in enumerate(detections):
                class_name = det['class_name']
                stats[class_name] = stats.get(class_name, 0) + 1
                
                app.logger.info(f"Processing detection {i+1}: {class_name}")
                
                # Crop and classify
                crop = process_image(image_path, det['bbox'])
                cls_result = classifier.classify(crop)
                
                classified_as = cls_result['class_name']
                classification_results[classified_as] = classification_results.get(classified_as, 0) + 1
                
                app.logger.info(f"Detection {i+1} classified as: {classified_as}")
                
                # Save cropped image
                base64_img = save_cropped_image(crop)
                cropped_images.append({
                    'class_name': classified_as,
                    'image': base64_img,
                    'label': f"{classified_as} #{classification_results[classified_as]}"
                })
            
            # Debug logging
            app.logger.info(f"Final stats: {stats}")
            app.logger.info(f"Final classification: {classification_results}")
            
            response = {
                'stats': stats,
                'classification': classification_results,
                'cropped_images': cropped_images,
                'total_cells': sum(stats.values())
            }
            
            # Store results in session
            session['analysis_results'] = {
                'stats': stats,
                'classification': classification_results,
                'total_cells': sum(stats.values())
            }
            
            app.logger.info(f"Analysis completed for {file.filename}: {response}")
            return jsonify(response)
        
        except Exception as e:
            app.logger.error(f"Error processing image: {str(e)}")
            return bad_request(f"Error processing image: {str(e)}")
        finally:
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    app.logger.warning(f"Failed to delete uploaded file {image_path}: {str(e)}")
    
    app.register_blueprint(bp)