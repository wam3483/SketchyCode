import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from routes.namespaces import diagnostic_namespace, sketch_ns, image_namespace
from routes.namespaces import plotter_namespace

from flask import Flask, render_template
from flask_restx import Api, Namespace

from routes.plotter import ResetRoute, MovePlotterRoute, DrawRectangleRoute, SketchImageRoute, GetTranslationVectorsRoute
from routes.diagnostic import ConfigureSettingsRoute, ControlPinRoute, HardwareSettingsRoute
from routes.image import ProcessImageRoute

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="Auto Etch A Sketch API",
    description="API for controlling an Etch A Sketch",
    doc="/docs"  # Swagger UI path
)

# Home route to render HTML page
@app.route('/')
def home():
    return render_template('index.html')

# REST API endpoint
# @app.route('/api/data', methods=['GET'])
# def get_data():
#     data = {
#         'message': 'Hello, World!',
#         'status': 'success'
#     }
#     return jsonify(data)
#
#
# @app.route('/detect-faces-meta', methods=['POST'])
# def detect_faces_meta():
#     if 'image' not in request.files:
#         return 'No image uploaded', 400
#
#     file = request.files['image']
#     img_bytes = np.frombuffer(file.read(), np.uint8)
#     image = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)
#
#     # Convert to grayscale for detection
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#
#     # Load OpenCV's built-in face detector
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
#
#     face_data = []
#     for (x, y, w, h) in faces:
#         face_data.append({
#             'x': int(x),
#             'y': int(y),
#             'width': int(w),
#             'height': int(h)
#         })
#     return jsonify({'faces': face_data})
#
#
# @app.route('/detect-faces', methods=['POST'])
# def detect_faces():
#     if 'image' not in request.files:
#         return 'No image uploaded', 400
#
#     file = request.files['image']
#     img_bytes = np.frombuffer(file.read(), np.uint8)
#     image = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)
#
#     # Convert to grayscale for detection
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#
#     # Load OpenCV's built-in face detector
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
#
#     # Draw rectangles around detected faces
#     for (x, y, w, h) in faces:
#         cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
#
#     # Encode image back to PNG
#     _, buffer = cv2.imencode('.png', image)
#     return send_file(io.BytesIO(buffer.tobytes()), mimetype='image/png')
#
#
# @app.route('/filter-image', methods=['POST'])
# def filter_image():
#     if 'image' not in request.files:
#         return 'No image uploaded', 400
#     file = request.files['image']
#     # convert to grayscale
#     image = Image.open(file.stream).convert('L')
#
#     # apply threshold filter
#     threshold = 128
#     # '1' = 1-bit pixels
#     bw = image.point(lambda x: 0 if x < threshold else 255, '1')
#
#     # save to buffer
#     buf = io.BytesIO()
#     bw.save(buf, format='PNG')
#     buf.seek(0)
#     return send_file(buf, mimetype='images/png')

api.add_namespace(plotter_namespace)
api.add_namespace(image_namespace)
api.add_namespace(diagnostic_namespace)
api.add_namespace(sketch_ns)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)