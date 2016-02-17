from flask import jsonify, request, g, url_for
from app.models import Post, Permission, Comment, User
from app import app, db
from decorators import permission_required

@app.route('/comments/')
def get_comments():
    rows = request.args.get('rows', 10, type=int)
    page = request.args.get('page', 1, type=int)
    postid = request.args.get('postid', type=int)
    if postid:
        post = Post.query.get_or_404(postid)
        postcomments = post.comments()
    else:
        postcomments = Comment.query.order_by(Comment.timestamp.desc())

    pagination = postcomments.paginate(
        page, per_page=rows,
        error_out=False)

    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('get_comments', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('get_comments', page=page+1, _external=True)

    commentarray = []
    for comment in comments:
        userid = comment.user_id
        user = User.query.get_or_404(userid)
        commentdict = {}
        commentdict['comment'] = comment.to_json()
        commentdict['user'] = user.to_json(40)
        commentarray.append(commentdict)

    return jsonify({
        'posts': commentarray,
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

@app.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())

@app.route('/posts/<int:id>/comments/')
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    rows = request.args.get('rows', 10, type=int)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=rows,
        error_out=False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('get_comments', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('get_comments', page=page+1, _external=True)
    return jsonify({
        'posts': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

@app.route('/posts/<int:id>/comments/', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_post_comment(id):
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, \
        {'Location': url_for('get_comment', id=comment.id,
                             _external=True)}
