import random
import datetime
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from flask_cors import CORS, cross_origin
from flask import Flask, render_template, request, jsonify

matplotlib.use('Agg')

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


class Context:
    sentiment = 0


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route('/endpoint', methods=['POST'])
def endpoint():
    sentiment = request.json['sentiment']
    Context.sentiment = sentiment
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    with open('data.csv', 'a') as file:
        file.write(f'\n{current_time},{sentiment}')
        file.close()
    df = pd.read_csv('data.csv')
    col = df['Sentiment']
    plt.clf()
    create_line(col)
    plt.clf()
    create_pie(col)


@app.route('/get_phrase', methods=['GET'])
@cross_origin()
def get_phrase():
    res = jsonify({'phrase': return_phrase(Context.sentiment)})
    # res.headers.add('Access-Control-Allow-Origin', '*')
    return res


def create_line(col):
    plt.title('Sentiment of Discussion Over Time')
    plt.xlabel('Time')
    plt.ylabel('Sentiment')
    plt.ylim(-1, 1)
    plt.plot(col, color='red')
    plt.savefig('./static/graph_line.png')


def create_pie(col):
    plt.title('Percent by Sentiment')
    lst = [0, 0]
    for i in col:
        if i < 0:
            lst[0] += 1
        else:
            lst[1] += 1
    plt.pie(lst, colors=['red', 'green'])
    plt.savefig('./static/graph_pie.png')


def return_phrase(s):
    positive_phrases = [
        'What do you have to eat today?',
        'Where is your dream vacation?',
        'Do you like ice cream?',
        'What is your favorite food item?',
        'What do you want to be when you grow up?',
        'What is your dream job?',
        'What do you want to do today?',
        'How are you feeling?',
    ]
    get_back_phrases = [
        'Back to the main point...',
        'Now what about...',
        "Let's come back to the discussion",
        'Are you ready to talk about...',
    ]
    phrase = ''
    if float(s) < 0:
        phrase = random.choice(positive_phrases)
    else:
        phrase = random.choice(get_back_phrases)
    return phrase


if __name__ == '__main__':
    app.run(debug=True)
