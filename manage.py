from flask import jsonify, request, g, abort, url_for
from app import app, db
from app.models import Post, Permission
from app.decorators import permission_required
from app.errors import forbidden

def get_posts():
    rows = 10 # request.args.get('rows', 10, type=int)
    page = 1 # request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=rows,
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = None # url_for('get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = None # url_for('get_posts', page=page+1, _external=True)
    print posts
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

letse = get_posts()
for l in letse.posts:
    print l
