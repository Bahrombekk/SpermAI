from flask import Blueprint, request, jsonify, render_template, session
from src.models.detector import SpermDetector
from src.models.classifier import SpermClassifier
from src.utils.image_processing import process_image, save_cropped_image
from src.api.errors import bad_request
import os
from datetime import datetime

bp = Blueprint('main', __name__)

def init_routes(app):
    # Initialize models
    detector = SpermDetector(app.config['models']['detection'])
    classifier = SpermClassifier(app.config['models']['classification'])
    
    app.logger.info("Models loaded successfully")
    
    @bp.route('/')
    def index():
        return render_template('index.html')
    
    @bp.route('/report')
    def report():
        # Retrieve analysis results from session
        results = session.get('analysis_results', {
            'stats': {'Live': 0, 'Dead': 0, 'Immature': 0},
            'classification': {'Normal': 0, 'Abnormal': 0, 'Other': 0},
            'total_cells': 0
        })
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
        
        # Save uploaded image
        image_path = os.path.join(app.config['paths']['upload_folder'], file.filename)
        file.save(image_path)
        
        try:
            # Perform detection
            detections = detector.detect(image_path)
            stats = {'Live': 0, 'Dead': 0, 'Immature': 0}
            cropped_images = []
            classification_results = {'Normal': 0, 'Abnormal': 0, 'Other': 0}
            
            # Process each detection
            for det in detections:
                class_name = det['class_name']
                stats[class_name] += 1
                
                # Crop and classify
                crop = process_image(image_path, det['bbox'])
                cls_result = classifier.classify(crop)
                classification_results[cls_result['class_name']] += 1
                
                # Save cropped image as base64
                base64_img = save_cropped_image(crop)
                cropped_images.append({
                    'class_name': cls_result['class_name'],
                    'image': base64_img,
                    'label': f"{cls_result['class_name']} #{classification_results[cls_result['class_name']]}"
                })
            
            response = {
                'stats': stats,
                'classification': classification_results,
                'cropped_images': cropped_images,
                'total_cells': sum(stats.values())
            }
            
            # Store results in session for report
            session['analysis_results'] = response
            
            app.logger.info(f"Image analysis completed: {file.filename}")
            return jsonify(response)
        
        except Exception as e:
            app.logger.error(f"Error processing image: {str(e)}")
            return bad_request(str(e))
    
    app.register_blueprint(bp)