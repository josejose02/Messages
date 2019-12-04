from flask import Flask, flash, render_template, request, redirect, url_for
from main import API
from werkzeug.utils import secure_filename
import pickle
import random
import os

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PICKLE_SAVE = 'data.pkl'
TOP = 5


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if request.method == 'POST':
            f = request.files['file']
            f.save(secure_filename('file.txt'))
            return redirect(url_for('.upload_file', file='file.txt'))
    return render_template('input.html', params=None)


@app.route('/results/', methods=['GET', 'POST'])
def upload_file():
    file = request.args.get('file')
    cache = request.args.get('cache')
    json = request.args.get('json')
    if not file:
        return 'File missing!'
    if cache:
        with open(PICKLE_SAVE, 'rb') as input:
            data = pickle.load(input)
    else:
        data = API(file)
    if json:
        return data.getJson()
    params = {
        'meta': data.getMeta(),
        'users': data.getUsers(),
        'most_emojis': data.getTopEmojis(TOP),
        'most_words': data.getTopWords(TOP),
        'most_active': data.getTopActiveUsers(TOP),
        'rest_emojis': data.getEmojis(),
        'enumerate': enumerate,
        'round': round,
        'file': file,
        'main': True,
        'random': random.randint(0, 100000)
    }
    if cache:
        params['graph'] = True
        params['cache'] = cache
    else:
        params['cache'] = 1
        params['graph'] = data.generateGraph(data.getFirstTwoNames())
    params['extra'] = data.getExtra()
    with open(PICKLE_SAVE, 'wb') as output:
        pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)
    return render_template('results.html', params=params)


@app.route('/results/<user>', methods=['GET', 'POST'])
def user_details(user):
    file = request.args.get('file')
    cache = request.args.get('cache')
    if not file:
        return 'File missing!'
    if cache:
        with open(PICKLE_SAVE, 'rb') as input:
            data = pickle.load(input)
    else:
        data = API(file)
    if data.user_exists(user):
        number_users = len(data.getMeta()['users']['names'])
        dual = False
        if number_users > 2:
            dual = True
        params = {
            'meta': data.getMeta(),
            'user': user,
            'users': data.getUsers(),
            'user_data': data.getUser(user),
            'most_emojis': data.getTopEmojisUser(user, TOP),
            'most_words': data.getTopWordsUser(user, TOP),
            'enumerate': enumerate,
            'number_users': number_users,
            'dual': dual,
            'file': file,
            'random': random.randint(0, 100000),
            'cache': user,
        }
        if cache == user:
            params['user_graph'] = True
        else:
            params['user_graph'] = data.generateSingleGraph(user)
        return render_template('results.html', params=params)
    return 'User does not exist'


@app.route('/results/detail/', methods=['GET', 'POST'])
def detail():

    file = request.args.get('file')
    cache = request.args.get('cache')
    type = request.args.get('type')
    user = request.args.get('user')

    if not file:
        return 'File missing!'
    with open(PICKLE_SAVE, 'rb') as input:
        data = pickle.load(input)
    params = {
        'meta': data.getMeta(),
        'users': data.getUsers(),
        'enumerate': enumerate,
        'round': round,
        'file': file,
    }
    if user:
        params['user'] = user
        if type == 'emojis':
            params['list'] = data.getEmojisUser(user)
            params['name'] = 'Emoji'
            params['title'] = 'Most used emojis by {}'.format(user)
            params['description'] = 'Times Used'
            params['global'] = data.getMeta()['emojis']['count']
        elif type == 'words':
            params['list'] = data.getWordsUser(user)
            params['name'] = 'Word'
            params['title'] = 'Most used words by {}'.format(user)
            params['description'] = 'Times Used'
            params['global'] = data.getMeta()['words']['count']
    else:
        params['back'] = True
        if type == 'emojis':
            params['list'] = data.getEmojis()
            params['name'] = 'Emoji'
            params['title'] = 'Most used emojis'
            params['description'] = 'Times Used'
            params['global'] = data.getMeta()['emojis']['count']
        elif type == 'words':
            params['list'] = data.getWords()
            params['name'] = 'Emoji'
            params['title'] = 'Most used words'
            params['description'] = 'Times Used'
            params['global'] = data.getMeta()['words']['count']
        elif type == 'users':
            params['list'] = data.getUsers()
            params['name'] = 'Person'
            params['title'] = 'Most active users'
            params['description'] = 'Number of messages sent'
            params['global'] = data.getMeta()['messages']['count']

    if cache:
        params['graph'] = True
        params['cache'] = cache
    else:
        params['cache'] = 1
    params['extra'] = data.getExtra()
    with open(PICKLE_SAVE, 'wb') as output:
        pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)
    return render_template('list.html', params=params)


if __name__ == '__main__':
    app.run(debug=True)
