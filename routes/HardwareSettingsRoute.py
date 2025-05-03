from dataclasses import asdict
from http import HTTPStatus

from flask import jsonify, request
from flask_restx import Resource, fields

from data.HardwareSettings import HardwareSettings
from data.Constants import settings_repo, plotter, pigpio_singleton
from plotter.xy_plotter import XYPlotter
from routes.namespaces import diagnostic_namespace

hardware_config_request = diagnostic_namespace.model('HardwareConfigRequest', {
    'xStepPin': fields.Integer(required=True,
                                      description='BCOM gpio pin to pulse for one step on x-axis'),
    'xEnablePin': fields.Integer(required=True,
                                      description='BCOM GPIO pin controlling whether x-axis stepper motor is enabled'),
    'xDirectionPin': fields.Integer(required=True,
                                    description='BCOM GPOI pin controlling direction x-axis stepper motor spins'),
    'yStepPin': fields.Integer(required=True,
                                           description='BCOM GPIO pin to pulse for one step on y-axis'),
    'yEnablePin': fields.Integer(required=True,
                                           description='BCOM GPIO pin controlling whether y-axis stepper motor is enabled'),
    'yDirectionPin': fields.Integer(required=True,
                                           description='BCOM GPIO pin controlling direction y-axis stepper motor spins'),
    'stepsPerCycle': fields.Integer(required=True,
                                           description='how many steps x-axis and y-axis stepper motors take to travel 360 degrees')
})
hardware_settings_response_model = diagnostic_namespace.model('HardwareSettingsResult', {
    'message': fields.String(description='details about the result of hardware settings request')
})
@diagnostic_namespace.route('/getHardwareSettings')
class GetHardwareSettingsRoute(Resource):
    def get(self):
        hardware_settings = settings_repo.get_hardware_settings()
        return jsonify(asdict(hardware_settings))

@diagnostic_namespace.route('/setHardwareSettings')
class SetConfigSettingsRoute(Resource):

    @diagnostic_namespace.doc(id='set_hardware_settings')
    @diagnostic_namespace.expect(hardware_config_request)
    @diagnostic_namespace.marshal_with(hardware_settings_response_model)
    def post(self):

        payload = request.get_json()
        config = HardwareSettings(
            xStepPin=int(payload['xStepPin']),
            xEnablePin=int(payload['xEnablePin']),
            xDirectionPin=int(payload['xDirectionPin']),
            yStepPin=int(payload['yStepPin']),
            yEnablePin=int(payload['yEnablePin']),
            yDirectionPin=int(payload['yDirectionPin']),
            stepsPerCycle=int(payload['stepsPerCycle'])
        )

        msg = ''
        status_code = HTTPStatus.BAD_REQUEST

        if not (0 < config.xStepPin <= 40):
            msg = 'xStepPin must be 0 < value <= 40'
        elif not (0 < config.xEnablePin <= 40):
            msg = 'xEnablePin must be 0 < value <= 40'
        elif not (0 < config.xDirectionPin <= 40):
            msg = 'xDirectionPin must be 0 < value <= 40'
        elif not (0 < config.yStepPin <= 40):
            msg = 'yStepPin must be 0 < value <= 40'
        elif not (0 < config.yEnablePin <= 40):
            msg = 'yEnablePin must be 0 < value <= 40'
        elif not (0 < config.yDirectionPin <= 40):
            msg = 'yDirectionPin must be 0 < value <= 40'

        else:
            status_code = HTTPStatus.OK
            success = settings_repo.set_hardware_settings(config)
            if not success:
                msg = 'failed to save hardware settings'
                status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            else:
                plotter.instance = XYPlotter.init_plotter(pigpio_singleton, settings_repo)
        data = {
            'message': msg
        }
        return data, status_code