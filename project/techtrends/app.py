import sqlite3
import logging
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
db_con_cnt = 0


def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global db_con_cnt
    db_con_cnt += 1
    return connection

# Function to get a post using its ID


def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application


@app.route('/healthz')
def status():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    # log line
    app.logger.info('healthz request successfull')
    return response


@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_cnt = connection.execute('SELECT COUNT(*) FROM posts').fetchone()
    response = app.response_class(
        response=json.dumps({"status": "success", "code": 0, "data": {
                            "db_connection_count": db_con_cnt, "post_count": post_cnt[0]}}),
        status=200,
        mimetype='application/json'
    )
    # log line
    app.logger.info('metrics request successfull')
    return response


@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    app.logger.info('main request successfull')
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        # log line
        app.logger.info("404 : article doesn't exist!")
        return render_template('404.html'), 404
    else:
        # log line
        app.logger.info("article "+post["title"]+" retrieved!")
        return render_template('post.html', post=post)

# Define the About Us page


@app.route('/about')
def about():
    # long line
    app.logger.info("about request successfull")
    return render_template('about.html')

# Define the post creation functionality


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()
            app.logger.info("new article "+title+" created")
            return redirect(url_for('index'))

    return render_template('create.html')


# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    app.run(host='127.0.0.1', port='3111')
