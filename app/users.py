from flask import jsonify, request, current_app, url_for
from app import app
from models import User, Post


@app.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    avatar_size = request.args.get('avatar_size', 50, type=int)
    return jsonify(user.to_json(avatar_size))

@app.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    rows = request.args.get('rows', 10, type=int)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=rows,
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('get_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

@app.route('/users/<int:id>/timeline/')
def get_user_followed_posts(id):
    user = User.query.get_or_404(id)
    rows = request.args.get('rows', 10, type=int)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=rows,
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('get_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
