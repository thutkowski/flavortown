import os

from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        UPLOAD_FOLDER = 'uploads',
        DATABASE=os.path.join(app.instance_path, 'flavortown.db'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import database
    database.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)

    from . import home
    app.register_blueprint(home.bp)
    app.add_url_rule('/', endpoint='index')

    from . import recipes
    app.register_blueprint(recipes.bp)

    from . import friends
    app.register_blueprint(friends.bp)

    from . import upload
    app.register_blueprint(upload.bp)

    from . import budget
    app.register_blueprint(budget.bp)
    
    return app

