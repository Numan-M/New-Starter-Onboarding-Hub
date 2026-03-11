from app import app

@app.route('/')
@app.route('/index')
def Index():
    return "Hello, World!"

