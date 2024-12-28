# Ref: https://mulgrew.me/posts/session-timeout-flask.html

# Usage: http://127.0.0.1:5000/secret
# user1 // user1_secret

from flask import Flask, Response, redirect, url_for, request, session, abort, g
from flask_login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user, current_user

from datetime import timedelta

app = Flask(__name__)

# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx'
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


# create some users with ids 1 to 20       
users = [User(id) for id in range(1, 21)]


# some protected url
@app.route('/')
@app.route('/secret')
@login_required
def home():
    return Response("You've entered secret area")

 
# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']        
        if password == username + "_secret":
            id = username
            user = User(id)
            login_user(user)
            return redirect(request.args.get("next"))
        else:
            return abort(401)
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')
    
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)


@app.before_request
def before_request():

    # Implementing Session Timeout
    # ============================

    # from flask import g
    # from datetime import timedelta

    # The flask-login module has a remember=True flag when logging in a user. 
    # Ensure this is set to ‘False’ otherwise the remember variable will 
    # override the session timeout.

    # Let Flask know that you need the session expiring.
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)
    # Let Flask know that you only want the session to expire after 60 minutes
    # of inactivity
    session.modified = True
    # Grab the logged in user from flask_login and sets the global user
    # for Flask
    g.user = current_user


if __name__ == "__main__":
    app.run()
