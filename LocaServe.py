import os
import mimetypes
import random
import requests
import threading
from flask import Flask, send_from_directory, render_template_string
from flask_compress import Compress
from werkzeug.utils import secure_filename, safe_join

app = Flask(__name__)
Compress(app)
FILES_DIRECTORY = r"."

def list_files(startpath):
    media_files = {}
    other_files = {}

    for root, dirs, files in os.walk(startpath):
        path = root.split(os.sep)
        rel_path = os.path.relpath(root, startpath)
        for file in files:
            file_path = os.path.join(rel_path, file) if rel_path != '.' else file
            mime, _ = mimetypes.guess_type(file_path)
            file_type = mime.split('/')[0] if mime else 'Other'

            if file_type.startswith('image') or file_type.startswith('audio') or file_type.startswith('video'):
                if file_type not in media_files:
                    media_files[file_type] = []
                media_files[file_type].append(file_path.replace(os.sep, '/'))
            else:
                if file_type not in other_files:
                    other_files[file_type] = []
                other_files[file_type].append(file_path.replace(os.sep, '/'))

    return media_files, other_files


random_port = random.randint(13000, 14000)


def get_public_ip():
    try:
        response = requests.get('https://httpbin.org/ip')
        data = response.json()
        public_ip = data['origin']
        return public_ip
    except Exception as e:
        print(f"Error getting public IP: {e}")
        return "Unknown"


def run_lt_command(random_port):
    try:
        # print(f"Running localtunnel on port {random_port}...")
        os.system(f"lt --port {random_port}") 

    except Exception as e:
        print(f"Error running localtunnel: {e}")


lt_thread = threading.Thread(target=run_lt_command, args=(random_port,))
lt_thread.start()


public_ip = get_public_ip()
print(f"Your Tunnel password: {public_ip}")

@app.route('/')
def file_list():
    media_files, other_files = list_files(FILES_DIRECTORY)

    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Loca Serve &#128518;</title>
            <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container">
                <h1>Welcome to Loca Serve &#128518; !</h1>
                                  <br/>
                <h2>Available Media Files</h2>
                {% for file_type, files in media_files.items() %}
                <div class="accordion" id="accordion-media">
                    <div class="card">
                        <div class="card-header" id="heading-media-{{ loop.index }}">
                            <h2 class="mb-0">
                                <button class="btn btn-link" type="button" data-toggle="collapse" data-target="#collapse-media-{{ loop.index }}" aria-expanded="true" aria-controls="collapse-media-{{ loop.index }}">
                                    {{ file_type }}
                                </button>
                            </h2>
                        </div>
                        <div id="collapse-media-{{ loop.index }}" class="collapse" aria-labelledby="heading-media-{{ loop.index }}" data-parent="#accordion-media">
                            <div class="card-body">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>File Name</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                    {% for file in files %}
                                        <tr>
                                            <td>{{ file }}</td>
                                            <td>
                                                <a href="/stream/{{ file }}" target="_blank" class="btn btn-primary">Stream</a>
                                                <a href="/download/{{ file }}" class="btn btn-success">Download</a>
                                            </td>
                                        </tr>
                                    {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}

                <h2>Other Files</h2>
                {% for file_type, files in other_files.items() %}
                <div class="accordion" id="accordion-other">
                    <div class="card">
                        <div class="card-header" id="heading-other-{{ loop.index }}">
                            <h2 class="mb-0">
                                <button class="btn btn-link" type="button" data-toggle="collapse" data-target="#collapse-other-{{ loop.index }}" aria-expanded="true" aria-controls="collapse-other-{{ loop.index }}">
                                    {{ file_type }}
                                </button>
                            </h2>
                        </div>
                        <div id="collapse-other-{{ loop.index }}" class="collapse" aria-labelledby="heading-other-{{ loop.index }}" data-parent="#accordion-other">
                            <div class="card-body">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>File Name</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                    {% for file in files %}
                                        <tr>
                                            <td>{{ file }}</td>
                                            <td>
                                                <a href="/download/{{ file }}" class="btn btn-success">Download</a>
                                            </td>
                                        </tr>
                                    {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>

            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
            <div class="footer">
        Get in touch: Email us at <a href="mailto:kckckrishnachaitanya7@.gmailcom">Krishnac7</a>
    </div>
            </body>
        </html>
    ''', media_files=media_files, other_files=other_files)


@app.route('/stream/<path:filename>')
def stream_file(filename):
    try:
        full_path = safe_join(FILES_DIRECTORY, filename)
        if not os.path.exists(full_path):
            return "File not found", 404

        mime, _ = mimetypes.guess_type(full_path)
        if mime:
            if mime.startswith('video') or mime.startswith('image') or mime.startswith('text'):
                return send_from_directory(FILES_DIRECTORY, filename, mimetype=mime)

        return "Invalid file type for streaming", 400
    except Exception as e:
        return str(e), 500


@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        if '..' in filename or filename.startswith('/'):
            return "Invalid file path", 400

        secure_filename(filename)

        full_path = safe_join(FILES_DIRECTORY, filename)
        if not os.path.exists(full_path):
            return "File not found", 404

        return send_from_directory(FILES_DIRECTORY, filename, as_attachment=True)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    print(f"Running on port {random_port}")
    app.run(port=random_port, host='0.0.0.0', debug=False)