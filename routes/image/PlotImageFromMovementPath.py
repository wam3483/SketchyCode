from typing import Tuple, List

from PIL import ImageDraw, Image
from flask import send_file, request
from flask_restx import Resource, fields

from data import Vector
from routes.namespaces import image_namespace

@image_namespace.route('/plotFromMovementPath')
class PlotImageFromMovementPath(Resource):
    vector_model = image_namespace.model('Vector',
    {
        'x': fields.Integer,
        'y': fields.Integer
    })
    vectors_payload_model = image_namespace.model(
        'VectorsPayload',
        {
            'vectors': fields.List(fields.Nested(vector_model))
        }
    )

    @image_namespace.expect(vectors_payload_model)
    def post(self):
        """Create image from plotter movement data"""
        data = request.get_json()
        if not data or 'vectors' not in data:
            return {'error': 'Missing "vectors" in request body'}, 400

        vectors = data['vectors']  # list of [dx, dy] pairs

        if not all(isinstance(v, list) and len(v) == 2 for v in vectors):
            return {'error': 'Each vector must be 2 tuple int'}, 400

        bounding_rect = self.get_bounding_rect_from_translation_vectors(vectors)

        width, height = bounding_rect[2]+2, bounding_rect[3]+2
        image = Image.new("RGBA", (width, height), (255,255,255,255))

        draw = ImageDraw.Draw(image)

        self.draw_translation_vectors(draw, vectors)
        self.draw_translation_cursor_points(draw, vectors)

        # If you want to save or show it:
        # image.save("output.png")
        # image.show()

        # Or keep it in-memory
        import io
        output = io.BytesIO()
        image.save(output, format='PNG')
        output.seek(0)

        return send_file(
            output,
            mimetype='image/png',
            download_name='output.png',
            as_attachment=True,
            conditional=False
        )

    def draw_translation_cursor_points(self, draw: ImageDraw, vectors: List[Vector]):
        cursor = (0, 0)
        direction_change_color = (0, 0, 0, 255)
        for vector in vectors:
            x, y = cursor
            dx, dy = vector
            new_x = cursor[0] + vector[0]
            new_y = cursor[1] + vector[1]

            if dx != 0 and dy != 0:
                draw.point((new_x, y), fill=direction_change_color)
                draw.point((new_x, new_y), fill=direction_change_color)
            else:
                draw.point((new_x, new_y), fill=direction_change_color)
            cursor = x + dx, y + dy

    def draw_translation_vectors(self, draw : ImageDraw, vectors : List[Vector]):
        cursor = (0, 0)
        color = (0, 0, 0, 255)
        for vector in vectors:
            x, y = cursor
            dx, dy = vector
            new_x = cursor[0] + vector[0]
            new_y = cursor[1] + vector[1]

            if dx != 0 and dy != 0:
                draw.line([x, y, new_x, y], fill=color, width=1)
                draw.line([new_x, y, new_x, new_y], fill=color, width=1)
            else:
                draw.line([x, y, new_x, new_y], fill=color, width=1)
            cursor = x + dx, y + dy

    def get_bounding_rect_from_translation_vectors(self, vectors : List[Vector]) -> Tuple[int, int, int, int]:
        max_width = 0
        max_height = 0
        cursor_pos = (0,0)
        for vector in vectors:
            cursor_pos = vector[0]+cursor_pos[0], vector[1]+cursor_pos[1]
            max_width = max(cursor_pos[0], max_width)
            max_height = max(cursor_pos[1], max_height)

        return 0, 0, max_width, max_height