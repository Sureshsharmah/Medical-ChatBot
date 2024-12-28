from flask import Flask, jsonify, render_template, request
import google.generativeai as genai
import nltk
from nltk.stem.lancaster import LancasterStemmer
import pickle
import numpy as np
import json
import random
import sqlite3


# Load Gemini AI model
genai.configure(api_key='AIzaSyAg6UtggTP8rYwWQ-oBhJQf7xDa7SyyhpE')
gemini_model = genai.GenerativeModel('gemini-pro')
chat = gemini_model.start_chat(history=[])

connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

command = """CREATE TABLE IF NOT EXISTS user(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
cursor.execute(command)

app = Flask(__name__)
chat_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('userlog.html')

@app.route('/userlog', methods=['GET', 'POST'])
def userlog():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']

        query = "SELECT name, password FROM user WHERE name = '"+name+"' AND password= '"+password+"'"
        cursor.execute(query)

        result = cursor.fetchall()

        if len(result) == 0:
            return render_template('index.html', msg='Sorry, Incorrect Credentials Provided,  Try Again')
        else:
            return render_template('userlog.html')

    return render_template('index.html')


@app.route('/userreg', methods=['GET', 'POST'])
def userreg():
    if request.method == 'POST':

        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()

        name = request.form['name']
        password = request.form['password']
        mobile = request.form['phone']
        email = request.form['email']
        
        print(name, mobile, email, password)

        command = """CREATE TABLE IF NOT EXISTS user(name TEXT, password TEXT, mobile TEXT, email TEXT)"""
        cursor.execute(command)

        cursor.execute("INSERT INTO user VALUES ('"+name+"', '"+password+"', '"+mobile+"', '"+email+"')")
        connection.commit()

        return render_template('index.html', msg='Successfully Registered')
    
    return render_template('index.html')

@app.route('/analyse', methods=['GET', 'POST'])
def analyse():
    if request.method == 'POST':
        user_input = request.form['query']
        # Get response from Gemini AI model
        gemini_response = chat.send_message(user_input)

        data = gemini_response.text
        print(data)
        result = []
        for row in data.split('*'):
            if row.strip() != '':
                result.append(row)
        print(result)

        import csv
        f = open('HOSPITAL.csv', 'r')
        data = csv.reader(f)
        header = next(data)
        # Update chat history with both responses
        chat_history.append([user_input, result])
        try:
            for row in data:
                if row[1] in user_input:
                    name = row[0]
                    Link = row[2]
                    break
            return render_template('userlog.html', status="Sever", chat_history=chat_history, name=name, Link=Link)
        except:
            return render_template('userlog.html', chat_history=chat_history)
    return render_template('userlog.html')

@app.route('/logout')
def logout():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
