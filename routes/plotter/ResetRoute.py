from data import Constants
from data.Constants import plotterManager, plotter
from plotter.plotter_move_job import PlotterMoveJob
from flask_restx import Resource, fields

from plotter.xy_plotter import XYPlotter
from routes.namespaces import plotter_namespace

@plotter_namespace.route('/reset')
class PlotterReset(Resource):

    response_model = plotter_namespace.model('MoveResponse', {
        'success': fields.Boolean(description='whether movement completed successfully'),
        'message': fields.String(description='additional information concerning result of request')
    })

    @plotter_namespace.marshal_with(response_model)
    def post(self):
        x = -Constants.display_width
        y = -Constants.display_height

        x_result = False
        y_result = False
        if x != 0:
            x_result = plotterManager.queue_job(PlotterMoveJob(plotter.instance,[(x,0)]))
        if y != 0:
            y_result = plotterManager.queue_job(PlotterMoveJob(plotter.instance,[(0,y)]))
        msg = '' if x_result and y_result else f'Failed to queue movement: x_queued=[{x_result}], y_queued=[{y_result}]'
        data = {
            'success': x_result and y_result,
            'message': msg
        }
        return data