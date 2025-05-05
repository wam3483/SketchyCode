import logging

from flask import request
from flask_restx import fields, Resource, api

from data.Constants import pigpio_singleton
from routes.namespaces import diagnostic_namespace

@diagnostic_namespace.route('/setPin')
class SetPinRoute(Resource):
    set_pin_model = diagnostic_namespace.model('SetPinRequest', {
        'pin': fields.Integer(required=True, description='Which GPIO pin to control'),
        'state': fields.Boolean(required=True, description='1 = HIGH, 0 = LOW'),
    })

    response_model = diagnostic_namespace.model('SetPinResponse', {
        'success': fields.Boolean(description='whether movement completed successfully'),
        'message': fields.String(description='additional information concerning result of request')
    })
    @diagnostic_namespace.expect(set_pin_model)
    @diagnostic_namespace.marshal_with(response_model)
    def post(self):
        data = request.get_json()
        pin, state = data['pin'], data['state']
        config_result = pigpio_singleton.set_mode(pin, 1)

        if config_result == 0:
            state_int = 1 if state else 0
            result = pigpio_singleton.write(pin, state_int)
            success = result == 0
            msg = ''
            logging.info(f'set pin[{pin}] = [{state_int}]')
            if success:
                msg = f'error code was [{result}]. -2 = Invalid GPIO number, -3 = Invalid level (should be 0 or 1)'
            data = {
                'success': success,
                'message': msg
            }
            return data
        else:
            config_fail_data = {
                'success': False,
                'message': f'Config ping error code = {config_result}'
            }
            return config_fail_data

@diagnostic_namespace.route('/getPin')
class GetPinRoute(Resource):
    get_pin_model = diagnostic_namespace.model('SetPinRequest', {
        'pin': fields.Integer(required=True, description='Which GPIO pin to control')
    })
    get_pin_response_model = diagnostic_namespace.model('SetPinResponse', {
        'success': fields.Boolean(description='whether movement completed successfully'),
        'message': fields.String(description='additional information concerning result of request')
    })

    @diagnostic_namespace.expect(get_pin_model)
    @diagnostic_namespace.marshal_with(get_pin_response_model)
    def post(self):
        data = request.get_json()
        pin_str = data['pin']

        if pin_str is None:
            return {
                'success': False,
                'message': 'Missing required query parameter: pin'
            }

        try:
            pin = int(pin_str)
        except ValueError:
            return {
                'success': False,
                'message': 'Invalid pin value provided'
            }

        logging.info(f"pin = {pin}")
        try:
            result = pigpio_singleton.read(pin)
            if result in [0, 1]:
                return {
                    'success': True,
                    'message': f'Pin {pin} is currently {"HIGH" if result == 1 else "LOW"}'
                }
            else:
                return {
                    'success': False,
                    'message': f'Error reading pin. Return code: {result}'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Exception while reading pin: {str(e)}'
            }