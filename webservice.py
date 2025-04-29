import platform

from flask import Flask, request, send_file, render_template
from PIL import Image
import io
from flask_restx import Api, Resource, fields, Namespace

from plotter_manager import PlotterManager
from plotter_move_job import PlotterMoveJob
from plotter.xy_plotter import XYPlotter
import logging
import pigpio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

image_ns = Namespace('image', description='Image processing endpoints')
sketch_ns = Namespace("sketch", description="Draw things on a physical etch a sketch")
test_ns = Namespace("test", description="operations to test auto etch a sketch")

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="Auto Etch A Sketch API",
    description="API for controlling an Etch A Sketch",
    doc="/docs"  # Swagger UI path
)
_on_raspberry = platform.system() == 'Linux'
pigpio_singleton : None | pigpio.pi
if _on_raspberry:
    pigpio_singleton = pigpio.pi()
plotter = XYPlotter(pigpio_singleton, 3200,.01,1,
                    17, 27,22,
                    0, 0, 0)
plotterManager = PlotterManager(plotter)


# Home route to render HTML page
@app.route('/')
def home():
    return render_template('index.html')

@test_ns.route('/controlPin')
class ControlPin(Resource):
    set_pin_model = api.model('SetPinRequest', {
        'pin': fields.Integer(required=True, description='Which GPIO pin to control'),
        'state': fields.Boolean(required=True, description='1 = HIGH, 0 = LOW'),
    })

    response_model = api.model('SetPinResponse', {
        'success': fields.Boolean(description='whether movement completed successfully'),
        'message': fields.String(description='additional information concerning result of request')
    })
    @api.expect(set_pin_model)
    @api.marshal_with(response_model)
    def post(self):
        data = api.payload
        pin, state = data['pin'], data['state']
        config_result = pigpio_singleton.set_mode(pin, pigpio.OUTPUT)
        if config_result == 0:
            state_int = 1 if state else 0
            result = pigpio_singleton.write(pin, state_int)
            success = result == 0
            msg = ''
            logging.info(f'set pin[{pin}] = [{state_int}]')
            if success:
                msg = f'error code was [{result}]. -2 = Invalid GPIO number, -3 = Invalid level (should be 0 or 1)'
            data = {
                'success': success,
                'message': msg
            }
            return data
        else:
            config_fail_data = {
                'success': False,
                'message': f'Config ping error code = {config_result}'
            }
            return config_fail_data

    @api.marshal_with(response_model)
    def get(self):
        pin_str = request.args.get('pin')
        if pin_str is None:
            return {
                'success': False,
                'message': 'Missing required query parameter: pin'
            }

        try:
            pin = int(pin_str)
        except ValueError:
            return {
                'success': False,
                'message': 'Invalid pin value provided'
            }

        try:
            result = pigpio_singleton.read(pin)
            if result in [0, 1]:
                return {
                    'success': True,
                    'message': f'Pin {pin} is currently {"HIGH" if result == 1 else "LOW"}'
                }
            else:
                return {
                    'success': False,
                    'message': f'Error reading pin. Return code: {result}'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Exception while reading pin: {str(e)}'
            }



@test_ns.route('/move')
class Test(Resource):
    move_model = api.model('MoveCommand', {
        'x': fields.Integer(required=True, description='Target X coordinate'),
        'y': fields.Integer(required=True, description='Target Y coordinate'),
    })

    response_model = api.model('MoveResponse', {
        'success': fields.Boolean(description='whether movement completed successfully'),
        'message': fields.String(description='additional information concerning result of request')
    })

    @api.expect(move_model)
    @api.marshal_with(response_model)
    def post(self):
        data = api.payload
        x, y = data['x'], data['y']
        result = False
        if x != 0:
            result = plotterManager.start_job(PlotterMoveJob(plotter,[(x,0)], 1))
        if y != 0:
            result = plotterManager.start_job(PlotterMoveJob(plotter,[(0,y)], 1))
        data = {
            'success': result,
            'message': ''
        }
        return data


# Define a file upload field using Flask-RESTX fields
upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type='File', required=True, help='file to sketch')

@sketch_ns.route('/sketch-image')
class SketchBitmap(Resource):
    @api.expect(upload_parser)  # Expect the file input
    def post(self):
        """Accept a picture of only black or white pixels to reproduce on an etch-a-sketch."""

        if 'file' not in request.files:
            return {'error': 'No file uploaded'}, 400

        uploaded_file = request.files['file']

        if uploaded_file.filename == '':
            return {'error': 'Empty filename'}, 400

        if not uploaded_file.filename.lower().endswith('.png'):
            return {'error': 'Only PNG files are supported'}, 400

        try:
            img = Image.open(uploaded_file.stream)

            # 🔧 Do your processing here
            processed_img = img  # placeholder

            output = io.BytesIO()
            processed_img.save(output, format='PNG')
            output.seek(0)

            return send_file(output, mimetype='image/png')

        except Exception as e:
            return {'error': str(e)}, 500

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

api.add_namespace(image_ns)
api.add_namespace(test_ns)
api.add_namespace(sketch_ns)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)