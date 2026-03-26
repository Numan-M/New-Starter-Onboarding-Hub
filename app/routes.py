from app import app

@app.route('/')
@app.route('/index')
def Index():
    """This function defines the route for the index page of the Flask application."""
    return "Hello, team!"

