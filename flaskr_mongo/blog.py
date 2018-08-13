from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr_mongo.auth import login_required
from flaskr_mongo.db import get_db

from bson.objectid import ObjectId
from datetime import datetime

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()

    posts = db.post.aggregate([
    {"$lookup":
        {
            "from":"user",
            "localField":"author_id",
            "foreignField":"_id",
            "as":"userInfos"
        }
    },
    {"$unwind":"$userInfos"},
    {"$sort": { "updated" : -1 }},
    {"$project":
        {
            "id": "$_id",
            "title":"$title",
            "body": "$body",
            "updated": "$updated",
            "author_id": "$author_id",
            "username":"$userInfos.username",
        }
    }
    ])

    results = []

    for post in posts:
        results.append({"id": str(post["id"]), "title": post["title"], "body": post["body"], "author_id": post["author_id"], "username": post["username"], "updated": post["updated"]})

    return render_template('blog/index.html', posts=results)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            post_id = db.post.insert({'title': title, 'body': body, 'author_id': g.user['_id'], 'updated': datetime.now()})
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    # 修正対象のpost_idのauthor_idがログインユーザと同じであるかチェック
    # postを検索
    db = get_db()
    got_post = db.post.find_one({"_id": ObjectId(id)})

    post = {'id': str(got_post["_id"]),'title': got_post["title"], 'body': got_post["body"], 'author_id': got_post["author_id"]}

    if post is None:
        abort(404, "Post id {0} doesn't exist".format(id))

    if str(post['author_id']) != str(g.user['_id']):
        abort(403)

    return post


@bp.route('/<id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            result = db.post.update_one({"_id": ObjectId(id)}, {'$set': {'title': title, 'body': body, 'updated': datetime.now()}})
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    result = db.post.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('blog.index'))
