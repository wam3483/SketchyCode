# namespaces.py
from flask_restx import Namespace

diagnostic_namespace = Namespace('diagnostic', description='Test and configuration endpoints')
plotter_namespace = Namespace('plotter', description='commands for moving plotter')
image_namespace = Namespace("image", description="process image for reproduction on physical etch a sketch")
sketch_ns = Namespace("sketch", description="Draw things on a physical etch a sketch")