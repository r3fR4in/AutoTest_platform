import os

from flask import render_template, send_from_directory
from __init__ import create_app
from utils.extensions import db, celery

app = create_app()
db.init_app(app)
# 创建表用的
# with app.app_context():
#     db.create_all()
celery.init_app(app)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    # app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
