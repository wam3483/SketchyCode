from flask import request

from data.Constants import plotterManager, plotter
from data.Vector import Vector
from plotter.plotter_move_job import PlotterMoveJob
from flask_restx import Resource, fields

from routes.namespaces import plotter_namespace

@plotter_namespace.route('/move')
class Test(Resource):
    move_model = plotter_namespace.model('MoveCommand', {
        'x': fields.Integer(required=True, description='Target X coordinate'),
        'y': fields.Integer(required=True, description='Target Y coordinate'),
    })

    response_model = plotter_namespace.model('MoveResponse', {
        'success': fields.Boolean(description='whether movement completed successfully'),
        'message': fields.String(description='additional information concerning result of request')
    })

    @plotter_namespace.expect(move_model)
    @plotter_namespace.marshal_with(response_model)
    def post(self):
        data = request.get_json()
        x, y = data['x'], data['y']

        x_result = False
        y_result = False
        if x != 0:
            x_result = plotterManager.queue_job(PlotterMoveJob(plotter.instance,[Vector(x,0)]))
        if y != 0:
            y_result = plotterManager.queue_job(PlotterMoveJob(plotter.instance,[Vector(0,y)]))
        success = x_result and y_result
        msg = '' if success else f'failed to queue movement. x_result=[{x_result}], y_result=[{y_result}]'
        data = {
            'success': success,
            'message': msg
        }
        return data