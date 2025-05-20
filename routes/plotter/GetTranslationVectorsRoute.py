import json
import logging
import warnings

import numpy
from PIL import Image
from flask import request, Response
from flask_restx import Resource

from data.Utils import get_image_metadata
from data.Vector import Vector
from data.graph import Graph
from plotter.path.flood_fill_region_finder import FloodFillRegionFinder
from plotter.path.path_datatype import Region
from plotter.path.plotter_path_calc import trace_with_backtracking, vectorize_path_processor_func, \
    get_translation_vectors
from routes.namespaces import plotter_namespace
from services.PlotterInstructionService import PlotterInstructionService

upload_parser = plotter_namespace.parser()
upload_parser.add_argument('file', location='files', type='File', required=True, help='file to process')

@plotter_namespace.route('/getTranslationVectors')
class GetTranslationVectorsRoute(Resource):

    @plotter_namespace.expect(upload_parser)  # Expect the file input
    def post(self):
        """Accept an image to reproduce on an etch a sketch"""

        if 'file' not in request.files:
            return {'error': 'No file uploaded'}, 400

        uploaded_file = request.files['file']

        if uploaded_file.filename == '':
            return {'error': 'Empty filename'}, 400

        img : Image
        try:
            img = Image.open(uploaded_file.stream).convert("RGB")
            metadata = get_image_metadata(img)
            logging.info(f"Image metadata:\t\n{metadata}")
        except Exception as e:
            warnings.warn(f"Failed to generate path for image: \n{e}")
            return {'error': str(e)}, 500

        service = PlotterInstructionService()
        instructions = service.get_plotter_instructions(img)
        all_translation_vectors = instructions.plotter_path

        result = [(v.x,v.y) for v in all_translation_vectors]
        return {"vectors":result}, 200