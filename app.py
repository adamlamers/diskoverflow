from flask import Flask, render_template, request, abort
import sqlite3
import json
import time


app = Flask(__name__)

query_template2 = """SELECT

                    rowid,
                    title,
                    snippet(stackoverflow_fts, '<b>', '</b>', '...', 1, 40)

                    FROM stackoverflow_fts
                    WHERE title
                    MATCH ? LIMIT 10;"""

query_template = """SELECT

                    stackoverflow_fts.rowid,
                    stackoverflow_fts.title,
                    snippet(stackoverflow_fts.body)

                    FROM stackoverflow_fts JOIN stackoverflow_posts ON
                    stackoverflow_fts.rowid=stackoverflow_posts.rowid WHERE stackoverflow_fts.title
                    MATCH ? LIMIT 10;"""

question_query = """ SELECT id, score, title, body FROM stackoverflow_posts WHERE rowid = ? LIMIT 1; """

answer_query = """ SELECT id, score, ownerdisplayname, body, owneruserid FROM stackoverflow_posts WHERE parentid=? ORDER BY score DESC """

@app.route('/')
def index():
    return render_template('index.html')

#Accepts parameters:
# query: string to query questions for

@app.route('/query', methods=["POST"])
def query():

    start = time.time()
    conn = sqlite3.connect("stackoverflow.sqlite3")
    db = conn.cursor()
    end = time.time()
    print('opening db took {}s'.format(end-start))

    q = request.form.get("query")

    if not q:
        abort(404)

    start = time.time()
    db.execute(query_template2, (q,))
    end = time.time()
    print('query took {}s'.format(end-start))

    return json.dumps(db.fetchall())

@app.route('/question/<qid>')
def question(qid):

    conn = sqlite3.connect("stackoverflow.sqlite3")
    db = conn.cursor()
    db.execute(question_query, (qid,))
    answer = db.fetchone()

    if answer is None:
        abort(404)

    question = { "id" : answer[0],
                 "score" : answer[1],
                 "title" : answer[2],
                 "body" : answer[3] }

    db.execute(answer_query, (question['id'],))
    answers_raw = db.fetchall()
    answers = []
    for answer_i in answers_raw:
        ans = { "id" : answer_i[0],
                "score" : answer_i[1],
                "author" : answer_i[2],
                "body" : answer_i[3] }

        if answer_i[2] == "NULL":
            ans['author'] = "user{}".format(answer_i[4])

        answers.append(ans)

    return json.dumps({'question' : question, 'answers' : answers})

if __name__ == '__main__':
    app.debug = True
    app.run()

