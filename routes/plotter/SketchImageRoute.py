import logging
import warnings

from PIL import Image
from flask import request
from flask_restx import Resource

from data.Constants import plotterManager, plotter
from plotter.path.flood_fill_region_finder import FloodFillRegionFinder
from plotter.path.pathprocessor import create_path
from plotter.plotter_move_job import PlotterMoveJob
from routes.namespaces import plotter_namespace

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
            img = Image.open(uploaded_file.stream)
        except Exception as e:
            warnings.warn(f"Failed to generate path for image: \n{e}")
            return {'error': str(e)}, 500

        # get regions of black pixels using flood fill alg
        region_finder = FloodFillRegionFinder(img, 10)
        regions = region_finder.find_regions()

        flattened_regions: list[tuple[int, int]] = [item for sublist in regions for item in sublist]

        translation_vectors = create_path(flattened_regions)

        plotterManager.queue_job(PlotterMoveJob(plotter.instance, translation_vectors))