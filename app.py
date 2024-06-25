from flask import Flask, request, send_file, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import zipfile
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'

# Ensure the upload and processed directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def remove_bin_files(zip_path, output_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        with zipfile.ZipFile(output_path, 'w') as zip_out:
            for item in zip_ref.infolist():
                if not item.filename.lower().endswith('.bin'):
                    data = zip_ref.read(item.filename)
                    zip_out.writestr(item, data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(url_for('index'))
    
    if file and file.filename.endswith('.zip'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the zip file
        output_filename = 'processed_' + filename
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
        remove_bin_files(file_path, output_path)

        return render_template('download.html', output_filename=output_filename)

    return 'Invalid file type'

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)