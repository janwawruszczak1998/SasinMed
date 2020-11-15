from sasinmed import app

@app.route('/android/hello')
def mobile_hello_world():
    return 'Hello, World!'