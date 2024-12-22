from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_pymongo import PyMongo
import gridfs
from bson import ObjectId
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
import flask_login
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

# Set up configurations
app.config["MONGO_URI"] = "mongodb://localhost:27017/social_media_db"
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SECRET_KEY'] = 'mysecretkey'  # Required for sessions

mongo = PyMongo(app)
fs = gridfs.GridFS(mongo.db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"  # Redirect to login page if not logged in

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get(user_id):
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return User(str(user["_id"]), user["username"])
        return None

# Load user
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route to register a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user already exists
        if mongo.db.users.find_one({"username": username}):
            flash("Username already exists!", "danger")
            return redirect(url_for('register'))

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Insert user into MongoDB
        mongo.db.users.insert_one({"username": username, "password": hashed_password})
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Route to login an existing user
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find user by username
        user = mongo.db.users.find_one({"username": username})

        if user and bcrypt.check_password_hash(user["password"], password):
            # Create a User object and log the user in
            login_user(User(str(user["_id"]), user["username"]))
            return redirect(url_for('profile'))

        flash("Invalid username or password", "danger")
    
    return render_template('login.html')

# Route to logout the user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route to add posts
@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        post_text = request.form['text']
        multimedia_files = []

        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Store the file in GridFS directly (no need to save in static folder)
                file_id = fs.put(file, filename=filename)
                multimedia_files.append(file_id)

        post = {
            "user_id": current_user.username,  # Use the logged-in user
            "text": post_text,
            "multimedia": multimedia_files,
            "likes": 0,
            "comments": []
        }

        mongo.db.posts.insert_one(post)
        flash("Post added successfully!", "success")
        return redirect(url_for('index'))

    return render_template('add_post.html')

# Route to edit posts
@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})

    # Check if the current user is the post creator
    if post['user_id'] != current_user.username:
        flash("You are not authorized to edit this post", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        post_text = request.form['text']
        multimedia_files = []

        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_id = fs.put(file, filename=filename)
                multimedia_files.append(file_id)

        mongo.db.posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {"text": post_text, "multimedia": multimedia_files}}
        )

        flash("Post updated successfully!", "success")
        return redirect(url_for('profile'))

    return render_template('edit_post.html', post=post)

# Route to delete post
@app.route('/delete_post/<post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})

    # Check if the current user is the post creator
    if post['user_id'] != current_user.username:
        flash("You are not authorized to delete this post", "danger")
        return redirect(url_for('index'))

    if post:
        for file_id in post['multimedia']:
            fs.delete(file_id)

        mongo.db.posts.delete_one({"_id": ObjectId(post_id)})

    flash("Post deleted successfully!", "success")
    return redirect(url_for('profile'))
@app.route('/')
def landing_page():
    return render_template('landing_page.html')

@app.route('/home')
def index():
    posts = mongo.db.posts.find()
    return render_template('index.html', posts=posts)

# Route to fetch multimedia files
@app.route('/file/<file_id>')
def get_file(file_id):
    file = fs.get(ObjectId(file_id))
    return Response(file.read(), mimetype='image/jpeg')

# Route to view user profile
@app.route('/profile')
@login_required
def profile():
    user_posts = mongo.db.posts.find({"user_id": current_user.username})
    return render_template('profile.html', user=current_user, posts=user_posts)

# Route to add comment to post
@app.route('/add_comment/<post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    comment_text = request.form['comment']
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})

    comment = {
        "user_id": current_user.username,
        "text": comment_text
    }

    mongo.db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": comment}}
    )

    flash("Comment added successfully!", "success")
    return redirect(url_for('index'))

@app.route('/like_post/<post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    # Find the post from the database
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})

    if post:
        # Ensure 'likes' is a list, if it's not, initialize it as an empty list
        likes = post.get('likes', [])
        
        if isinstance(likes, int):
            # If likes is an integer, reset it to an empty list or list of users
            likes = []
            mongo.db.posts.update_one(
                {"_id": ObjectId(post_id)},
                {"$set": {"likes": likes}}
            )

        # Check if the user has already liked the post
        if current_user.username not in likes:
            # If not, add the username to the 'likes' array
            mongo.db.posts.update_one(
                {"_id": ObjectId(post_id)},
                {"$push": {"likes": current_user.username}}
            )
            flash("You liked this post!", "success")
        else:
            flash("You have already liked this post.", "warning")
    else:
        flash("Post not found.", "danger")

    # Redirect to the same page or a specific page
    return redirect(url_for('index'))  # or any other route you want





if __name__ == '__main__':
    app.run(debug=True)
