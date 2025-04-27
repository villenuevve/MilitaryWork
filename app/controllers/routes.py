import os
from flask import Blueprint, render_template, request, redirect, url_for
from app.models.detection_model import predict_image

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return render_template('error.html', error_message="Файл не знайдено! Спробуйте ще раз.")

    image = request.files['image']

    if image.filename == '':
        return render_template('error.html', error_message="Файл не обрано! Завантажте зображення.")

    if image:
        try:
            predicted_class, confidence, annotated_image_path = predict_image(image)
            result_image = os.path.basename(annotated_image_path)
            return render_template('results.html',
                        predicted_class=predicted_class,
                        confidence=round(confidence * 100, 2),
                        result_image=os.path.basename(annotated_image_path))
        except Exception as e:
            return render_template('error.html', error_message=f"Помилка обробки зображення: {str(e)}")

    return redirect(url_for('main.index'))

@main.app_errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

