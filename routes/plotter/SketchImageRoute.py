import logging
import warnings

from PIL import Image
from flask import request
from flask_restx import Resource

from data.Constants import plotterManager, plotter
from plotter.path.flood_fill_region_finder import FloodFillRegionFinder
from plotter.path.plotter_path_calc import vectorize_path_processor_func, trace_with_backtracking, get_translation_vectors
from plotter.plotter_move_job import PlotterMoveJob
from routes.namespaces import plotter_namespace
from services.PlotterInstructionService import PlotterInstructionService

upload_parser = plotter_namespace.parser()
upload_parser.add_argument('file', location='files', type='File', required=True, help='file to process')

@plotter_namespace.route('/sketch-image')
class SketchImageRoute(Resource):
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
        except Exception as e:
            warnings.warn(f"Failed to generate path for image: \n{e}")
            return {'error': str(e)}, 500

        plotter_instructions_svc = PlotterInstructionService()
        plotter_instructions = plotter_instructions_svc.get_plotter_instructions(img)

        plotterManager.queue_job(PlotterMoveJob(plotter.instance, plotter_instructions.plotter_path))