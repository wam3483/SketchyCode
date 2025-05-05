import io

from PIL import Image
from flask import request, send_file
from flask_restx import Resource

from routes.namespaces import image_namespace

upload_parser = image_namespace.parser()
upload_parser.add_argument('file', location='files', type='File', required=True, help='file to process')

@image_namespace.route('/process-image')
class ProcessImage(Resource):
    @image_namespace.expect(upload_parser)  # Expect the file input
    def post(self):
        """Accept a picture to process for etch a sketch"""

        if 'file' not in request.files:
            return {'error': 'No file uploaded'}, 400

        uploaded_file = request.files['file']

        if uploaded_file.filename == '':
            return {'error': 'Empty filename'}, 400

        try:
            img = Image.open(uploaded_file.stream)

            # 🔧 Do your processing here
            processed_img = img

            output = io.BytesIO()
            processed_img.save(output, format='PNG')
            output.seek(0)

            return send_file(output, mimetype='image/png')

        except Exception as e:
            return {'error': str(e)}, 500