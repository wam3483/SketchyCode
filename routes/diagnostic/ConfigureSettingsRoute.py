from dataclasses import asdict
from http import HTTPStatus

from flask import jsonify, request
from flask_restx import Resource, fields

from data.ConfigSettings import ConfigSettings
from data.Constants import settings_repo, plotter, pigpio_singleton
from plotter.xy_plotter import XYPlotter
from routes.namespaces import diagnostic_namespace

config_request = diagnostic_namespace.model('ConfigSettingsRequest', {
    'xBacklashPixels': fields.Float(required=True,
                                      description='x-axis correction in pixels to overturn when changing direction'),
    'yBacklashPixels': fields.Float(required=True,
                                      description='y-axis correction in pixels to overturn when changing direction'),
    'xDegreesPerPixel': fields.Float(required=True,
                                    description='number of degrees turned to travel 1 pixel'),
    'yDegreesPerPixel': fields.Float(required=True,
                                    description='number of degrees turned to travel 1 pixel'),
    'drawSpeed_PixelsPerSec': fields.Float(required=True,
                                           description='how fast the plotter is moved in pixels per second')
})
config_response_model = diagnostic_namespace.model('ConfigSettingsResult', {
    'message': fields.String(description='details about the result of a configuration request')
})
@diagnostic_namespace.route('/getConfigSettings')
class GetConfigSettingsRoute(Resource):
    def get(self):
        config_settings = settings_repo.get_config_settings()
        return jsonify(asdict(config_settings))

@diagnostic_namespace.route('/setConfigSettings')
class SetConfigSettingsRoute(Resource):
    @diagnostic_namespace.doc(id='set_config_settings')
    @diagnostic_namespace.expect(config_request)
    @diagnostic_namespace.marshal_with(config_response_model)
    def post(self):

        payload = request.get_json()
        config = ConfigSettings(
            xBacklashPixels=float(payload['xBacklashPixels']),
            yBacklashPixels=float(payload['yBacklashPixels']),
            xDegreesPerPixel=float(payload['xDegreesPerPixel']),
            yDegreesPerPixel=float(payload['yDegreesPerPixel']),
            drawSpeed_PixelsPerSec=float(payload['drawSpeed_PixelsPerSec'])
        )

        msg = ''
        status_code = HTTPStatus.BAD_REQUEST

        if config.xBacklashPixels < 0:
            msg = 'x backlash must be >= 0'
        elif config.yBacklashPixels < 0:
            msg = 'y backlash must be >= 0'
        elif config.xDegreesPerPixel <= 0:
            msg = 'x degrees per pixel must be > 0'
        elif config.yDegreesPerPixel <= 0:
            msg = 'y degrees per pixel must be > 0'
        elif config.drawSpeed_PixelsPerSec <= 0:
            msg = 'draw speed must be > 0'
        else:
            status_code = HTTPStatus.OK
            success = settings_repo.set_config_settings(config)
            if not success:
                msg = 'failed to save config settings'
                status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            else:
                plotter.instance = XYPlotter.init_plotter(pigpio_singleton, settings_repo)
        data = {
            'message': msg
        }
        return data, status_code