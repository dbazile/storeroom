import datetime
import os
import textwrap

import flask
import werkzeug.utils


SIZE_KB = 2 ** 10
SIZE_MB = 2 ** 20
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
    items = []

    for name in os.listdir(PUBLIC_DIR):
        url = flask.url_for('static', filename=name)
        stats = os.stat(PUBLIC_DIR + '/' + name)
        mtime = datetime.datetime.fromtimestamp(stats.st_mtime).isoformat()

        if stats.st_size < SIZE_KB:
            size = f'{round(stats.st_size)}B'
        elif stats.st_size < SIZE_MB:
            size = f'{round(stats.st_size / SIZE_KB)}KB'
        else:
            size = f'{round(stats.st_size / SIZE_MB)}MB'

        item = f'''
            <a class="image" data-mtime="{mtime}" href="{url}" target="_blank">
                <img class="preview" src="{url}" alt="{name}" />
                <span class="label">{name} ({size})</span>
            </a>
        '''

        items.append(textwrap.dedent(item).strip())

    items = '\n\n'.join(reversed(sorted(items)))

    if not items:
        items = 'Empty'

    css = '''
        body {
            margin: 0 auto;
            max-width: 800px;
            font-family: sans-serif;
            background-color: #222;
            box-shadow: 0 0 0 25px rgba(0,0,0,.15),
                        0 0 0 10px rgba(0,0,0,.2);
        }

        header {
            margin: 15px 0;
            font-size: 1.5em;
            font-weight: bold;
            text-align: center;
        }

        form {
            padding: 50px 30px;
            background-color: hsl(200, 100%, 95%);
            color: hsl(200, 60%, 50%);
            text-align: center;
        }

        .instructions {
            margin: 30px;
            text-align: center;
            font-size: 2em;
        }

        button {
            margin-top: 30px;
            padding: 20px;
            width: 70%;
            border: 0;
            background-color: hsl(90, 73%, 48%);
            cursor: pointer;
            border-radius: 3px;
            color: white;
            font-weight: bold;
            font-size: 1.5em;
        }

        button:hover {
            background-color: hsl(90, 73%, 53%);
        }

        button:disabled {
            display: none;
        }

        #images {
            display: flex;
            flex-direction: column;
        }

        .image {
            display: flex;
            flex: 1 25%;
            flex-direction: column;
            background-color: black;
            color: white;
            text-decoration: none;
        }

        .image:hover {
            background-color: #f06;
        }

        .image:hover .preview {
            opacity: .9;
        }

        .image:hover .label {
            box-shadow: inset 0 1px rgba(255,255,255,.7);
        }

        .preview {
            width: 100%;
        }

        .label {
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            padding: 15px;
        }
    '''

    js = '''
        const PICKER = document.querySelector('input[type="file"]')
        const BUTTON = document.querySelector('button')

        function test() {
            BUTTON.disabled = !PICKER.files.length
        }

        // Main operation
        PICKER.addEventListener('change', test)
        test()
    '''

    content = f'''\
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0"/>
            <title>storeroom</title>
        </head>
        <body>
            <form action="/files" method="POST" enctype="multipart/form-data">
                <label>
                    <div class="instructions">Tap here to choose a picture to add to the storeroom</div>
                    <input type="file" name="file" />
                </label>
                <button disabled>add this picture!</button>
            </form>

            <div id="images">
                {textwrap.indent(items, ' ' * 16).strip()}
            </div>

            <style>
                {textwrap.indent(css, ' ' * 8).strip()}
            </style>

            <script>
                {textwrap.indent(js, ' ' * 8).strip()}
            </script>
        </body>
        </html>
    '''

    return textwrap.dedent(content).lstrip()


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

    return flask.redirect('/')
