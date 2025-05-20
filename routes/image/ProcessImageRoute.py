# import io
# import typing
#
# from PIL import Image, ImageDraw
# from flask import request, send_file
# from flask_restx import Resource
# import numpy as np
# import cv2
#
# from routes.namespaces import image_namespace
#
# upload_parser = image_namespace.parser()
# upload_parser.add_argument('file', location='files', type='File', required=True, help='file to process')
# upload_parser.add_argument('threshold', type=float, required=False, help='Threshold between 0.0 and 1.0 (default: 0.5)')
#
# @image_namespace.route('/process-image')
# class ProcessImage(Resource):
#     @image_namespace.expect(upload_parser)  # Expect the file input
#     def post(self):
#         """Accept a picture to process for etch a sketch"""
#
#         if 'file' not in request.files:
#             return {'error': 'No file uploaded'}, 400
#
#         threshold_str = request.args.get('threshold', '0.5')
#         threshold = 0
#         try:
#             threshold = float(threshold_str)
#             if not (0.0 <= threshold <= 1.0):
#                 return {'error': 'Threshold must be between 0 and 1'}, 400
#         except ValueError:
#             return {'error': 'Invalid threshold value'}, 400
#
#         uploaded_file = request.files['file']
#
#         if uploaded_file.filename == '':
#             return {'error': 'Empty filename'}, 400
#
#         # try:
#         processed_img = self.sketch_image(uploaded_file.stream)
#         # img = Image.open(uploaded_file.stream)
#         #
#         # # 🔧 Do your processing here
#         # processed_img = img.convert('L')#.point(lambda x: 0 if x < (threshold*256) else 255, mode = '1')
#
#         output = io.BytesIO()
#         processed_img.save(output, format='PNG')
#         output.seek(0)
#
#         return send_file(output, mimetype='image/png')
#
#         # except Exception as e:
#         #     return {'error': str(e)}, 500
#
#     def sketch_image(self, stream : typing.IO[bytes]):
#         file_bytes = np.frombuffer(stream.read(), np.uint8)
#         img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
#
#         # Compute gradients
#         grad_x = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3)
#         grad_y = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=3)
#         magnitude = cv2.magnitude(grad_x, grad_y)
#         direction = cv2.phase(grad_x, grad_y, angleInDegrees=False)  # radians
#
#
#         # PIL drawing canvas
#         pil_img = Image.new('L', img.shape[::-1], color=255)
#         draw = ImageDraw.Draw(pil_img)
#
#         dark_color = (0, 0, 0, 255)
#         light_color = (100, 100, 100, 255)
#         normalized = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
#         # for y in range(0, img.shape[0]):
#         #     for x in range(0, img.shape[1]):
#         #         mag = normalized[y, x]
#         #         if mag < 30:
#         #             draw.point((x,y),fill=255)
#         #         else:
#         #             draw.point((x, y), fill=0)
#
#         # Loop through pixels at intervals
#         step = 3
#         length = 2
#         threshold = 20
#         for y in range(0, img.shape[0], step):
#             for x in range(0, img.shape[1], step):
#                 mag = normalized[y, x]
#                 if mag > threshold:
#                     angle = direction[y, x] #+ np.pi / 2  # Perpendicular to gradient
#                     dx = np.cos(angle) * length / 2
#                     dy = np.sin(angle) * length / 2
#                     x1, y1 = x - dx, y - dy
#                     x2, y2 = x + dx, y + dy
#                     draw.line([(x1, y1), (x2, y2)], fill=0, width=1)
#
#         return pil_img