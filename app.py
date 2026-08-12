import os
import time
import base64
from flask import Flask, render_template, request, jsonify
from upscaler import FontImageUpscaler

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload limit

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upscale', methods=['POST'])
def upscale_endpoint():
    if 'image' not in request.files:
        return jsonify({'error': 'Tidak ada file gambar yang diunggah.'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Nama file tidak boleh kosong.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Format file tidak didukung. Gunakan PNG, JPG, WEBP, atau BMP.'}), 400

    try:
        start_time = time.time()
        image_bytes = file.read()

        # Parse form parameters
        scale_factor = float(request.form.get('scale_factor', 2.0))
        preset = request.form.get('preset', 'text_focus')
        sharpness = float(request.form.get('sharpness', 1.8))
        contrast = float(request.form.get('contrast', 1.2))
        denoise = float(request.form.get('denoise', 1.0))
        edge_boost = float(request.form.get('edge_boost', 1.5))
        binarize = request.form.get('binarize', 'false').lower() == 'true'

        # Process image using upscaler engine
        output_bytes = FontImageUpscaler.process_image(
            image_bytes=image_bytes,
            scale_factor=scale_factor,
            preset=preset,
            sharpness=sharpness,
            contrast=contrast,
            denoise=denoise,
            edge_boost=edge_boost,
            binarize=binarize
        )

        processing_time = round(time.time() - start_time, 2)

        # Convert original and processed images to base64 for fast UI rendering
        orig_b64 = base64.b64encode(image_bytes).decode('utf-8')
        proc_b64 = base64.b64encode(output_bytes).decode('utf-8')

        return jsonify({
            'success': True,
            'original_image': f"data:image/png;base64,{orig_b64}",
            'processed_image': f"data:image/png;base64,{proc_b64}",
            'processing_time': f"{processing_time} detik",
            'filename': file.filename
        })

    except Exception as e:
        return jsonify({'error': f"Gagal memproses gambar: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Upscaler Web App running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
