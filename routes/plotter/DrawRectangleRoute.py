from http import HTTPStatus

from flask import request

from data.Constants import plotterManager, plotter
from plotter.plotter_move_job import PlotterMoveJob
from flask_restx import Resource, fields

from routes.namespaces import plotter_namespace

@plotter_namespace.route('/drawRectangle')
class DrawRectangleRoute(Resource):
    move_model = plotter_namespace.model('DrawRectRequest', {
        'width': fields.Integer(required=True, description='rectangle width in pixels'),
        'height': fields.Integer(required=True, description='rectangle height in pixels'),
    })
    response_model = plotter_namespace.model('DrawRectangleResponse', {
        'message': fields.String(description='additional information concerning result of request')
    })

    @plotter_namespace.expect(move_model)
    @plotter_namespace.marshal_with(response_model)
    def post(self):
        data = request.get_json()
        width, height = data['width'], data['height']

        msg = ''
        status_code = HTTPStatus.BAD_REQUEST
        if width <= 0:
            msg = 'width must be > 0'
        elif height <= 0:
            msg = 'height must be > 0'
        else:
            top_result = plotterManager.queue_job(PlotterMoveJob(plotter.instance, [(width, 0)]))
            right_result = plotterManager.queue_job(PlotterMoveJob(plotter.instance, [(0, height)]))
            bottom_result = plotterManager.queue_job(PlotterMoveJob(plotter.instance, [(-width, 0)]))
            left_result = plotterManager.queue_job(PlotterMoveJob(plotter.instance, [(0, -height)]))
            if top_result and right_result and bottom_result and left_result:
                status_code = HTTPStatus.OK
            else:
                status_code = HTTPStatus.INTERNAL_SERVER_ERROR
                msg = f'failed to queue movement: top=[{top_result}], right=[{right_result}], bottom=[{bottom_result}], left=[{left_result}]'
        data = {
            'message': msg
        }
        return data, status_code