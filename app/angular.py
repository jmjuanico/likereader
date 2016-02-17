from flask import send_file, abort, render_template
from flask.ext.login import login_required, current_user
from app import app

@app.route('/angular/<templatename>', methods=['GET'])
#@login_required
def angular(templatename):

    if templatename == 'commentcontroller':
        return send_file('templates/commentcontroller.html')
    # not used yet
    elif templatename == 'editor':
        return send_file('templates/editor.html')
    elif templatename == 'editor_initializer':
        return send_file('templates/editor_initializer.html')
    elif templatename == 'data':
        return send_file('templates/data.json')
    else:
        abort(404)