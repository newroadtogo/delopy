from .db import db, lm, Category, Item, User

from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, login_required, current_user

import simplejson as json

import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


def create_app():
    app = Flask(__name__, template_folder='templates')

    app.secret_key = b'_2#y5L"FXQ8z\n\xec]/'

    db_uri = 'sqlite:///%s/flask.db' % os.path.dirname(
        os.path.abspath(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # init db
    init_db(app)

    # init login manager
    init_loginmanager(app)

    @app.route('/')
    def index():
        return render_template('index.html',
                               categories=Category.query.all(),
                               latest_items=Item.query.order_by(
                                   Item.id.desc()).all()
                               )

    @app.route('/<string:category_name>/items')
    def category_items(category_name):
        category = Category.query.filter_by(name=category_name).first()
        return render_template('category_items.html',
                               categories=Category.query.all(),
                               current_category=category.name,
                               current_category_items=Item.query.filter_by(
                                   category=category).order_by(
                                   Item.id.desc()).all()
                               )

    @app.route('/<string:category_name>/<string:item_name>')
    def item(category_name, item_name):
        category = Category.query.filter_by(name=category_name).first()
        item = Item.query.filter_by(name=item_name).first()
        return render_template('item.html',
                               item=item
                               )

    """Add user items."""
    @app.route('/additem', methods=('GET', 'POST'))
    @login_required
    def add_item():
        if request.method == 'POST':
            category = Category.query.filter_by(
                name=request.form['category_name']).first()
            item = Item(name=request.form['name'],
                        info=request.form['info'],
                        category_id=category.id,
                        user_id=current_user.id)
            with app.app_context():
                db.session.add(item)
                db.session.commit()
            item = Item.query.filter_by(name=request.form['name']).first()
            return redirect(
                url_for('item', category_name=request.form['category_name'],
                        item_name=request.form['name']))
        else:
            return render_template('add_edit_item.html',
                                   item=None,
                                   categories=Category.query.all(),
                                   item_category_name=None
                                   )

    """Edit user items."""
    @app.route('/catalog/<string:item_name>/edit', methods=('GET', 'POST'))
    @login_required
    def edit_item(item_name):
        item = Item.query.filter_by(name=item_name).first()
        if item.user_id != current_user.id:
            return redirect(url_for('index'))

        if request.method == 'POST':
            item.name = request.form['name']
            item.info = request.form['info']

            category = Category.query.filter_by(
                name=request.form['category_name']).first()
            item.category_id = category.id
            with app.app_context():
                db.session.commit()

            item = Item.query.filter_by(name=request.form['name']).first()
            return redirect(
                url_for('item', category_name=request.form['category_name'],
                        item_name=request.form['name']))
        else:
            category = Category.query.get(item.category_id)
            return render_template('add_edit_item.html',
                                   item=item,
                                   categories=Category.query.all(),
                                   item_category_name=category.name
                                   )

    """Delete user items."""
    @app.route('/catalog/<string:item_name>/delete', methods=('GET', 'POST'))
    @login_required
    def delete_item(item_name):
        item = Item.query.filter_by(name=item_name).first()
        if item.user_id != current_user.id:
            return redirect(url_for('index'))

        if request.method == 'POST':
            with app.app_context():
                db.session.delete(item)
                db.session.commit()
            return redirect(url_for('index'))
        else:
            return render_template('delete_item.html',
                                   item=item
                                   )

    @app.route('/catalog.json')
    def catalog_json():
        categories = Category.query.all()
        categories_as_dict = {
            "Categoriy": [category.as_dict() for category in categories]
        }
        return jsonify(categories_as_dict)

    @app.route('/login')
    def login():
        return redirect(google_auth_url())

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/oauth2callback')
    def oauth2_callback():
        import google.oauth2.credentials
        import google_auth_oauthlib.flow
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            '/%s/client_secret.json' % os.path.dirname(
                os.path.abspath(__file__)),
            scopes=['profile']
        )
        flow.redirect_uri = url_for('oauth2_callback', _external=True)

        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials

        from googleapiclient.discovery import build
        people_service = build(serviceName='people', version='v1',
                               credentials=credentials)
        profile = people_service.people().get(resourceName='people/me',
                                              personFields='names').execute()

        resource_name = profile['resourceName']
        display_name = [name for name in profile['names'] if
                        name['metadata']['primary'] is True][0]['displayName']

        user = User.query.filter_by(social_id=resource_name).first()
        if not user:
            user = User(social_id=resource_name, name=display_name)
            with app.app_context():
                db.session.add(user)
                db.session.commit()
        user = User.query.filter_by(social_id=resource_name).first()
        login_user(user)
        return redirect(url_for('index'))

    return app


def google_auth_url():
    import google.oauth2.credentials
    import google_auth_oauthlib.flow
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        '/%s/client_secret.json' % os.path.dirname(os.path.abspath(__file__)),
        scopes=['profile']
    )
    flow.redirect_uri = url_for('oauth2_callback', _external=True)
    authorization_url, _ = flow.authorization_url(
        include_granted_scopes='true')
    return authorization_url


def init_loginmanager(app):
    lm.init_app(app)


"""Database initialization."""
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User(id=0, social_id='Admin', name='Admin')
        db.session.add(user)

        soccer = Category(name='Soccer')
        soccer.items.append(Item(name='Shinguards', user_id=user.id, info='''
            This is a long info about .....................
            '''))
        soccer.items.append(Item(name='Two shinguards', user_id=user.id,
                                 info='''This is a long info about Two
                                 shinguards......'''))
        soccer.items.append(Item(name='Jersey', user_id=user.id, info='''
            This is a long info about .....................
            '''))
        soccer.items.append(Item(name='Soccer Cleats', user_id=user.id,
                                 info='''This is a long info about Soccer
                                 Cleats.............'''))
        db.session.add(soccer)

        basketball = Category(name='Basketball')
        db.session.add(basketball)

        baseball = Category(name='Baseball')
        baseball.items.append(Item(name='Bat', user_id=user.id, info='''
            This is a long info about .....................
            '''))
        db.session.add(baseball)

        frisbee = Category(name='Frisbee')
        frisbee.items.append(Item(name='Frisbee', user_id=user.id, info='''
            This is a long info about .....................
            '''))
        db.session.add(frisbee)

        snowboarding = Category(name='Snowboarding')
        snowboarding.items.append(Item(name='Goggles', user_id=user.id,
                                       info='''This is a long info about
                                       Goggles...........'''))
        snowboarding.items.append(Item(name='Snowboard', user_id=user.id,
                                       info='''This is a long info about
                                       Snowboard...............'''))
        db.session.add(snowboarding)

        rock_climbing = Category(name='Rock Climbing')
        db.session.add(rock_climbing)

        foosball = Category(name='Foosball')
        db.session.add(foosball)

        skating = Category(name='Skating')
        db.session.add(skating)

        hockey = Category(name='Hockey')
        hockey.items.append(Item(name='Stick', user_id=user.id, info='''
            This is a long info about .....................
            '''))
        db.session.add(skating)

        db.session.commit()
