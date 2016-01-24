from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import ServiceLoginForm, EditForm, PostForm, SearchForm, EditFormAdmin, CommentForm, ReplyForm\
    , LoginForm, RegisterForm, UpdateForm, ChangePasswordForm
from models import User, Post, Permission, Role, Comment
from datetime import datetime
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, COMMENTS_PER_POST
from emails import follower_notification, reply_notification, update_notification
from guess_language import guessLanguage
from flask.ext.babel import gettext
from app import babel
from config import LANGUAGES, PROVIDERS
from flask import jsonify
from translate import microsoft_translate
from flask.ext.sqlalchemy import get_debug_queries
from config import DATABASE_QUERY_TIMEOUT
from oauth import OAuthSignIn
from decorators import permission_required, admin_required
from app import bcrypt
from token import generate_confirmation_token, confirm_token
import json, os
from urlparse import urlparse, urljoin

# making sure no malicious redirect happens
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

# gets the next or the referrer url
def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

# redirects to the final url
def redirect_back(endpoint, **values):
    target = request.form['next']
    if not target or not is_safe_url(target) or is_auth_page(target):
        target = url_for(endpoint, **values)
    return redirect(target)

def is_auth_page(target):
    if 'login' in target or 'register' in target or 'update' in target:
        return True
    else:
        return False

def retain_before_auth_page(target):
    # initialize to None if does not exist yet
    # using session as global variable reinitializes every view
    try:
        session['before_auth_page']
    except:
        session['before_auth_page'] = None

    if not is_auth_page(target):
        session['before_auth_page'] = target
    else:
        target = session['before_auth_page']
    return target

@app.route('/baselogin', methods=['GET', 'POST'])
def baselogin():
    if g.login_form.validate_on_submit():
        user = User.query.filter_by(username=g.login_form.username.data).first()
        session['remember_me'] = True
        if user is not None:
            if bcrypt.check_password_hash(str(user.password), str(g.login_form.password.data)):
                login_user(user)
                flash('Welcome ' + user.username + '! You are now logged in. ', 'success')
            else:
                flash('Oops! Sorry invalid username or password.', 'danger')
        else:
            flash('Oops! Sorry invalid username or password.', 'danger')
    # return redirect(url_for('index'))
    return redirect (request.referrer)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm()
    next = get_redirect_target()
    next = retain_before_auth_page(next)
    print request.method
    if request.method == 'POST':
        if request.form['submit'] == 'cancel':
            return redirect_back('index')
        else:
            if form.validate_on_submit():
                session['remember_me'] = True
                user = User.query.filter_by(username=form.username.data).first()
                if user:
                    if bcrypt.check_password_hash(str(user.password), str(form.password.data)):
                        login_user(user)
                        flash('You were logged in. ', 'success')
                        return redirect_back('index')
                    else:
                        flash('Invalid email or password.', 'danger')
                        return render_template('login.html', form=form, error=error)
                else:
                    flash('Invalid email or password.', 'danger')
                    return render_template('login.html', form=form, error=error, next=next)
            else:
                flash('Invalid email or password.', 'danger')
                return render_template('login.html', form=form, error=error, next=next)
    else:
        return render_template('login.html', form=form, error=error, next=next)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    form = RegisterForm()
    next = get_redirect_target()
    next = retain_before_auth_page(next)
    if request.method == 'POST':
        if request.form['submit'] == 'cancel':
            return redirect_back('index')
        else:
            if form.validate_on_submit():
                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    password=bcrypt.generate_password_hash(form.password.data)
                )
                db.session.add(user)
                db.session.commit()

                """"
                if not form.email.data:
                    user=User.query.filter_by(username=form.username.data).first()
                    user.email = 'defaultemail_' + str(user.id) + '@gmail.com'
                    db.session.add(user)
                    db.session.commit()
                """""

                login_user(user)
                flash('You were logged in. ', 'success')

                return redirect_back('index')
            else:
                flash('Invalid email or password.', 'danger')
                return render_template('register.html', form=form, error=error, next=next)
    else:
        return render_template('register.html', form=form, error=error, next=next)

@app.route('/update', methods=['GET', 'POST'])   # pragma: no cover
def update():
    error = None
    form = UpdateForm()
    next = get_redirect_target()
    next = retain_before_auth_page(next)
    if request.method == 'POST':
        if request.form['submit'] == 'cancel':
            return redirect_back('index')
        else:
            if form.validate_on_submit():
                user = User.query.filter_by(username=form.username.data).first()
                if user:
                    # creates and sends the token which contains the secret keys
                    token = generate_confirmation_token(user.email)
                    confirm_update_url = url_for('confirm_password', token=token, _external=True)
                    update_notification(user, confirm_update_url)

                    flash('A confirmation email has been sent.', 'success')
                    return redirect_back('index')
                else:
                    flash('Invalid username.', 'danger')
                    return render_template('update.html', form=form, error=error, next=next)
            else:
                flash('Invalid username.', 'danger')
                return render_template('update.html', form=form, error=error, next=next)
    else:
        return render_template('update.html', form=form, error=error, next=next)

# will be called from email
@app.route('/confirm_password/<token>')
def confirm_password(token):
    try:
        # gets and compare the token from the email
        email = confirm_token(token)
    except:
        # flash error message if token does not match
        flash('The confirmation link is invalid or has expired.', 'danger')

    user = User.query.filter_by(email=email).first()
    if user:
        login_user(user)
        # if matches then redirects to profile page
        flash('You can now change your password. Thanks!', 'success')
        return redirect(url_for('edit'))

@app.route('/servicelogin', methods=['GET', 'POST'])
@oid.loginhandler
def servicelogin():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = ServiceLoginForm()
    if form.validate_on_submit():
        # session['remember_me'] = form.remember_me.data
        session['remember_me'] = True
        return oid.try_login(form.openid.data, ask_for=['username', 'email'])
    return render_template('servicelogin.html',
                           title='Sign In',
                           form=form,
                           providers=PROVIDERS)

@app.route('/', methods=['GET', 'POST'])
@app.route('/private', methods=['GET', 'POST'])
@app.route('/private/<int:page>', methods=['GET', 'POST'])
@login_required
def private(page=1):
    form = PostForm()
    if form.validate_on_submit():
        language = guessLanguage(form.body.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(title = form.title.data,
                    body=form.body.data,
                    timestamp=datetime.utcnow(),
                    author=g.user,
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash(gettext('Your post is now live!'))
        return redirect(url_for('private'))
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('private.html',
                           title='Private Lounge',
                           postform=form,
                           posts=posts,
                           pagination=posts)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
# @login_required
def index(page=1):
    form = PostForm()

    if form.validate_on_submit():
        language = guessLanguage(form.body.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(title = form.title.data,
                    body=form.body.data,
                    timestamp=datetime.utcnow(),
                    author=g.user,
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash(gettext('Your post is now live!'))
        return redirect(url_for('index'))
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
    # posts = Post.query.paginate(page, POSTS_PER_PAGE, False)

    return render_template('index.html',
                           title='Public Lounge',
                           postform=form,
                           posts=posts,
                           pagination=posts)

@app.route('/post/<int:id>', methods=['GET', 'POST'])
# @login_required
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          timestamp=datetime.utcnow(),
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('post', id=post.id, page=-1))

    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // COMMENTS_PER_POST + 1
    pagination = post.comments.paginate(
        page, per_page=COMMENTS_PER_POST,
        error_out=False)
    comments = pagination.items
    return render_template('postdetails.html', post=post, commentform=form, replyform = ReplyForm(),
                           comments=comments, pagination=pagination)

@app.route('/comment/<int:id>',methods=['GET', 'POST'])
@login_required
def comment(id):

    comment = Comment.query.get_or_404(id)
    authorid = comment.author_id
    postid = comment.post_id

    post = Post.query.get_or_404(postid)
    user = User.query.get_or_404(authorid)
    page = request.args.get('page', 1, type=int)

    form = ReplyForm()

    if form.validate_on_submit():
        user_url = url_for('user', username=user.username, _external=True)
        reply = Comment(body_html= '<a href="' + user_url + '">@' + user.username + '</a> ' + form.body.data,
                          timestamp=datetime.utcnow(),
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(reply)
        db.session.flush()
        r = comment.reply(reply)
        db.session.add(r)
        db.session.commit()

        flash('Your comment has been published.')
    commenturl = url_for('post', id=post.id, page=page, _external=True)
    if user.email:
        reply_notification(user, g.user, commenturl)
    return redirect(url_for('post', id=post.id, page=page))

# used by the flask loading manager
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

# The resp argument passed to the after_login function contains information returned
# by the OpenID provider.
@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash(gettext('Invalid login. Please try again.'))
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        username = resp.username
        if username is None or username == "":
            username = resp.email.split('@')[0]

        username = User.make_valid_username(username)
        username = User.make_unique_username(username)
        user = User(username=username, email=resp.email)
        db.session.add(user)
        db.session.commit()

        # make the user follow him/herself
        db.session.add(user.follow(user))
        db.session.commit()

    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))

# The current_user global is set by Flask-Login, so we just put a copy in
# the g object to have better access to it. With this, all requests will
# have access to the logged in user, even inside templates.
@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
    g.locale = get_locale()
    g.search_form = SearchForm()
    g.login_form = LoginForm()
    try:
        g.adminflag = g.user.can(Permission.ADMINISTER)
    except:
        pass

# This will record queries that are running too long based on the query timeout config
# result will be added in the logger
@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= DATABASE_QUERY_TIMEOUT:
            app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (query.statement, query.parameters, query.duration, query.context))
    return response

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<username>')
@app.route('/user/<username>/<int:page>')
# @login_required
def user(username, page=1):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(gettext('User %(username)s not found.', username = username))
        return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
                           user=user,
                           posts=posts,
                           pagination=posts)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    editform = EditForm(g.user.username)
    if editform.validate_on_submit():
        g.user.username = editform.username.data
        g.user.about_me = editform.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash(gettext('Your changes have been saved.'))
        return redirect(url_for('edit'))
    else:
        editform.username.data = g.user.username
        editform.about_me.data = g.user.about_me
    return render_template('edit.html', user = g.user, editform=editform, passwordform = ChangePasswordForm())

@app.route('/accessrights', methods=['GET', 'POST'])
@login_required
def accessrights():
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=g.user.email).first()
        if user:
            user.password = bcrypt.generate_password_hash(form.password.data)
            db.session.commit()
            flash('Password successfully changed.', 'success')
            return redirect(url_for('edit'))
        else:
            flash('Password change was unsuccessful.', 'danger')
            return redirect(url_for('edit'))
    return redirect(url_for('edit'))

@app.route('/editadmin/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editadmin(id):
    user = User.query.get_or_404(id)
    form = EditFormAdmin(user=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('user', username=user.username))
    form.username.data = user.username
    form.role.data = user.role_id
    form.about_me.data = user.about_me
    return render_template('editadmin.html', form=form, user=user)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(gettext('User %(username)s not found.', username = username))
        return redirect(url_for('index'))
    if user == g.user:
        flash(gettext('You can\'t follow yourself!'))
        return redirect(url_for('user', username=username))
    u = g.user.follow(user)
    if u is None:
        flash(gettext('Cannot follow %(username)s.', username = username))
        return redirect(url_for('user', username=username))
    db.session.add(u)
    db.session.commit()
    flash(gettext('You are now following %(username)s!', username = username))

    follower_notification(user, g.user)
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(gettext('User %(username)s not found.', username = username))
        return redirect(url_for('index'))
    if user == g.user:
        flash(gettext('You can\'t unfollow yourself!'))
        return redirect(url_for('user', username=username))
    u = g.user.unfollow(user)
    if u is None:
        flash(gettext('Cannot unfollow %(username)s.', username = username))
        return redirect(url_for('user', username=username))
    db.session.add(u)
    db.session.commit()
    flash(gettext('You have stopped following %(username)s.', username = username))
    return redirect(url_for('user', username=username))

@app.route('/search', methods=['POST'])
# @login_required
def search():
    print 'pre' + g.search_form.search.data
    if os.environ.get('HEROKU'):
        flash('Sorry, search is not available just yet')
        return redirect(url_for('index'))
    else:
        if not g.search_form.validate_on_submit():
            return redirect(url_for('index'))
        print g.search_form.search.data
        return redirect(url_for('search_results', query=g.search_form.search.data))

@app.route('/search_results/<query>')
# @login_required
def search_results(query):
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
                           query=query,
                           results=results)

# this is where the app is trying to match the best language that match
# a particular user depending on their web browser setup
@babel.localeselector
def get_locale():
    # return 'es'
    return request.accept_languages.best_match(LANGUAGES.keys())

@app.route('/translate', methods=['POST'])
# @login_required
def translate():
    return jsonify({
        'text': microsoft_translate(
            request.form['text'],
            request.form['sourceLang'],
            request.form['destLang']) })

# WE DONT WANT THIS FUNCTIONALITY THIS IS JUST TO TEST DEBUG
# PLEASE DELETE LATER
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    if post is None:
        flash('Post not found.')
        return redirect(url_for('index'))
    if post.author.id != g.user.id:
        flash('You cannot delete this post.')
        return redirect(url_for('index'))
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.')
    return redirect(url_for('index'))

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('login'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, username=username, email=email)
        db.session.add(user)
        db.session.commit()
        # make the user follow him/herself
        db.session.add(user.follow(user))
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))

@app.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=COMMENTS_PER_POST,
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page, replyform = ReplyForm())

@app.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('moderate',
                            page=request.args.get('page', 1, type=int)))

@app.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('moderate',
                            page=request.args.get('page', 1, type=int)))
