import os

import flask
import werkzeug.utils


PUBLIC_DIR = os.path.dirname(__file__) + '/public'


# Create files directory if needed
if not os.path.exists(PUBLIC_DIR):
    print(f'Creating directory {PUBLIC_DIR}...')
    os.mkdir(PUBLIC_DIR)


app = flask.Flask(
    'storeroom',
    static_folder=PUBLIC_DIR,
    static_url_path='/files')


@app.route('/')
def index():
    files = []
    for f in os.listdir(PUBLIC_DIR):
        url = flask.url_for('static', filename=f)
        size = round(os.path.getsize(PUBLIC_DIR + '/' + f) / 1024, 1)

        files.append(f'<a href="{url}" target="_blank"><img src="{url}" alt="{f}" /><span>{url} ({size} KB)</span></a>')

    files_links = '<br/>\n'.join(files)
    return f'''
        <form action="/files" method="POST"enctype="multipart/form-data">

            Select an image to upload:<br/>

            <input type="file" name="file" /><br/>

            <button>Upload</button>

        </form>
        <hr/>
        {files_links}
    '''


@app.route('/files', methods=['POST'])
def upload():
    f = flask.request.files.get('file')

    if not f:
        return f'Error: Nothing was actually uploaded\n', 400, {'content-type': 'text/plain'}

    if not f.content_type.startswith('image/'):
        return f'Error: Expected an image, got some other craziness: {f.content_type}\n', 400, {'content-type': 'text/plain'}

    file_path = PUBLIC_DIR + '/' + werkzeug.utils.secure_filename(f.filename)
    print(f'Uploaded: {file_path}')
    f.save(file_path)

    return 'YAY IT WORKED\n', 200, {'content-type': 'text/plain'}
