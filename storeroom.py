import os

import flask


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
        files.append(f)

    return f'files: {", ".join(files)}\n'
