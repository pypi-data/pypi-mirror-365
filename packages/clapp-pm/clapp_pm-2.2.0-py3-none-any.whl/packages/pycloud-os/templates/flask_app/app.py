from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', title='{{app_name}}')


@app.route('/api/hello')
def api_hello():
    return {'message': 'Hello from {{app_name}}!'}


if __name__ == '__main__':
    app.run(debug=True)
