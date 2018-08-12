from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr_mongo.auth import login_required
from flaskr_mongo.db import get_db

import json
import pprint
from bson.objectid import ObjectId

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    #posts = db.blog.find()
    #posts = json.loads({"_id": "00001", "title": "test", "body": "test" , "created": "2018/08/10 09:00:00", "author_id": "001", "username": "fujita" })

    '''
    NG　posts配下が出ない。。
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
    {"$project":
        {
            "id":{"$toString" :"$_id"},
            "title":"$title",
            "body": "$body",
            #"created": "$created",
            "author_id": {"$toString": "$author_id"},
            "username":"$userInfos.username",
        }
    }
    ])
    '''

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
    {"$project":
        {
            "id": "$id",
            "title":"$title",
            "body": "$body",
            #"created": "$created",
            "author_id": "$author_id",
            "username":"$userInfos.username",
        }
    }
    ])

    for post in posts:
        pprint.pprint(post)

    print(type(posts))

    return render_template('blog/index.html', posts=posts)


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
            post_id = db.post.insert({'title': title, 'body': body, 'author_id': g.user['_id']})
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    # 修正対象のpost_idのauthor_idがログインユーザと同じであるかチェック
    # postを検索
    db = get_db()
    post = db.post.fine_one({"_id": id})

    if post is None:
        abort(404, "Post id {0} doesn't exist".format(id))

    if post['author_id'] != g.user['id']:
        abort(403)

    return post
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.methods == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            result = db.post.update_one({'_id': id}, {'$set': {'title': title, 'body': body}})
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    result = db.post.delete_one({'_id': id})
    return redirect(url_for('blog.index'))
