import io

from PIL import Image
from flask import request, send_file
from flask_restx import Resource

from routes.namespaces import diagnostic_namespace
from services.PlotImageService import PlotImageService
from services.PlotterInstructionService import PlotterInstructionService

upload_parser = diagnostic_namespace.parser()
upload_parser.add_argument('file', location='files', type='File', required=True, help='file to process')


@diagnostic_namespace.route('/getPlotterVisualization')
class RenderPlottedImage(Resource):
    @diagnostic_namespace.expect(upload_parser)  # Expect the file input
    def post(self):
        """Accept a picture to process for etch a sketch"""

        if 'file' not in request.files:
            return {'error': 'No file uploaded'}, 400

        uploaded_file = request.files['file']

        if uploaded_file.filename == '':
            return {'error': 'Empty filename'}, 400

        img = Image.open(uploaded_file.stream).convert("RGB")

        plotter_instructions_svc = PlotterInstructionService()
        plotter_instructions = plotter_instructions_svc.get_plotter_instructions(img)

        plot_img_svc = PlotImageService()
        image_dims = plot_img_svc.get_image_dimensions(plotter_instructions)

        animating_img = Image.new("RGBA", image_dims, (255,255,255,255))

        frame_delay_ms = 33
        max_runtime_ms = 5000
        steps_per_ms = len(plotter_instructions.absolute_position_path) / max_runtime_ms
        steps_per_frame = min(int(frame_delay_ms * steps_per_ms), len(plotter_instructions.absolute_position_path))

        animating_frames = plot_img_svc.draw_animated_path(animating_img, steps_per_frame, plotter_instructions)
        animation_delay_ms = [frame_delay_ms] * (len(animating_frames) - 1)

        diagnostic_frame_delay = 1000
        animation_delay_ms.append(diagnostic_frame_delay)

        diagnostic_frames = plot_img_svc.plot_image(original_image=img, plotter_instructions=plotter_instructions)

        animation_delay_ms.extend([diagnostic_frame_delay] * len(diagnostic_frames))
        animating_frames.extend(diagnostic_frames)

        output = plot_img_svc.to_gif(animating_frames, animation_delay_ms)

        return send_file(output, mimetype='image/gif')