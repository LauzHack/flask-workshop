# Flask code for the web application

from flask import Flask, render_template, request, jsonify

import mysql.connector

from openai import OpenAI

db = mysql.connector.connect(host="XXXXXX", user="YYYYYY", password="******", database="YYYYYY$ZZZZZZ")

cursor = db.cursor()

client = OpenAI(api_key='AAAAAA')


app = Flask(__name__)



@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    try:
        f = request.files['photo']
        f.save(f.filename)
        return jsonify({"success": True}), 200
    except:
        return jsonify({"success": False}), 500


def askGPTToSummarize(notes):
    user_message = ""
    for note in notes:
        user_message += "Title: " + note['title'] + "\nContent: " + note['content'] + "\n======\n"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Please summarize the notes of the user."},
            {"role": "user", "content": user_message}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content


@app.route('/summarize_notes', methods=['POST'])
def summarize_notes():
    username = str(request.args['username'])
    sql_command = "select username, title, content from TodoNote where (username = %s);"
    values = (username,)
    try:
        cursor.execute(sql_command, values)
        results_from_db = cursor.fetchall()
        notes = []
        for item in results_from_db:
            username, title, content = item
            notes.append({"title": title, "content": content})
        response = askGPTToSummarize(notes)
        return jsonify({"success": True, "summary": response}), 200
    except:
        return jsonify({"success": False, "summary": ""}), 500


@app.route('/add_note', methods=['POST'])
def add_note():
    username = str(request.args['username'])
    title = str(request.args['title'])
    content = str(request.args['content'])
    sql_command = "insert into TodoNote (username, title, content) values (%s, %s, %s);"
    values = (username, title, content)
    try:
        cursor.execute(sql_command, values)
        db.commit()
        return jsonify({"success": True}), 201
    except:
        return jsonify({"success": False}), 500


@app.route('/get_notes', methods=['POST'])
def get_notes():
    username = str(request.args['username'])
    sql_command = "select username, title, content from TodoNote where (username = %s);"
    values = (username,)
    try:
        cursor.execute(sql_command, values)
        results_from_db = cursor.fetchall()
        results_to_return = []
        for item in results_from_db:
            username, title, content = item
            results_to_return.append({"title": title, "content": content})
        return jsonify({"success": True, "notes": results_to_return}), 200
    except:
        return jsonify({"success": False, "notes": []}), 500


@app.route('/divideTwoNumbers', methods=['POST'])
def divide_two_numbers():
    number_one = float(request.args['number_one'])
    number_two = float(request.args['number_two'])
    if number_two == 0:
        return jsonify({"success": False, "result": 0}), 500
    else:
        return jsonify({"success": True, "result": number_one / number_two}), 200


@app.route('/sayhello', methods=['POST'])
def say_hello():
    return 'Hello :)'


@app.route('/')
def main_route():
    return render_template('index.html')
