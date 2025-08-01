from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
import os, json, datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta'
UPLOAD_FOLDER = 'static/uploads'
POSTS_FILE = 'posts.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_posts():
    if not os.path.exists(POSTS_FILE):
        return []
    with open(POSTS_FILE, 'r') as f:
        return json.load(f)

def save_posts(posts):
    with open(POSTS_FILE, 'w') as f:
        json.dump(posts, f, indent=2)

@app.route('/')
def index():
    posts = load_posts()
    return render_template('index.html', posts=reversed(posts))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        posts = load_posts()
        content_type = request.form['type']
        content = ''
        if content_type == 'image':
            file = request.files['file']
            if file.filename != '':
                filename = secure_filename(file.filename)
                path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(path)
                content = filename
        elif content_type == 'text':
            content = request.form['text']
        posts.append({
            'id': len(posts) + 1,
            'username': session['username'],
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': content_type,
            'content': content,
            'likes': 0,
            'comments': []
        })
        save_posts(posts)
        return redirect('/')
    return render_template('upload.html')

@app.route('/like/<int:post_id>', methods=['POST'])
def like(post_id):
    posts = load_posts()
    for post in posts:
        if post['id'] == post_id:
            post['likes'] += 1
            break
    save_posts(posts)
    return redirect('/')

@app.route('/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    user = session.get('username', 'Anónimo')
    text = request.form['text']
    posts = load_posts()
    for post in posts:
        if post['id'] == post_id:
            post['comments'].append({'user': user, 'text': text})
            break
    save_posts(posts)
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect('/')
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)