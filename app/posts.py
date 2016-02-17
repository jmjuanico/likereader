from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from app import app, db
from models import Post, Permission
from decorators import permission_required
from errors import forbidden
from guess_language import guessLanguage
from flask.ext.babel import gettext
from flask import flash
from datetime import datetime

@app.route('/get_posts/')
def get_posts():
    rows = request.args.get('rows', 10, type=int)
    page = request.args.get('page', 1, type=int)

    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=rows,
        error_out=False)

    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('get_posts', page=page+1, _external=True)

    postarray = []
    for post in posts:
        postdict = {}
        postdict['post'] = post.to_json()
        postdict['user'] = post.author.to_json()
        postarray.append(postdict)

    return jsonify({
        'posts': postarray,
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

@app.route('/get_post/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    postdict = {}
    postdict['post'] = post.to_json()
    postdict['user'] = post.author.to_json()
    return jsonify(
            {'posts': postdict}
    )

@app.route('/new_post/', methods=['POST'])
#@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    postdata = request.json
    title = postdata['params']['title']
    body = postdata['params']['body']
    timestamp = datetime.utcnow()
    timestamp.strftime("%Y-%m-%dT%H:%M:%S Z")
    language = guessLanguage(body)
    if title and body:

        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        flash('Your post is now live!')
        post = Post(title=title,
                    body=body,
                    timestamp=timestamp,
                    author=g.user,
                    language=language)
        db.session.add(post)

        # flush and get the id
        db.session.flush()
        newid = post.id
        db.session.commit()
        flash(gettext('Your post is now live!'))
        return redirect(url_for('get_post', id=newid))
    return redirect(url_for('get_posts'))

@app.route('/edit_post/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
            not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    return jsonify(post.to_json())
