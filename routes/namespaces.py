# namespaces.py
from flask_restx import Namespace

diagnostic_namespace = Namespace('diagnostic', description='Test and configuration endpoints')
plotter_namespace = Namespace('plotter', description='commands for moving plotter')