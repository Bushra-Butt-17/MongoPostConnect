![bush-profile](https://github.com/user-attachments/assets/40d1f14f-7b7c-439e-b832-4780ebf671ff)<img src="https://github.com/user-attachments/assets/b366a10b-3371-4031-8dd6-ce7c4e6691b7"  />


# Social Media Application Using Flask and MongoDB



https://github.com/user-attachments/assets/7fd3aac5-747f-4b6c-bf2f-db43beb4880a



https://github.com/user-attachments/assets/d0851558-a6af-4471-be42-eb6b085328f2









# MongoPostConnect 🚀

## Description 📝

MongoPostConnect is a full-stack web application built with Flask and MongoDB, where users can post multimedia content, like and comment on posts, and manage their personal profiles. The application uses Flask for backend handling, MongoDB as the database, and GridFS to store multimedia files such as images.

## Features 🌟

- User registration and login with secure password hashing 🔐.
- Post creation with the ability to add multimedia content (images) 🖼️.
- Post editing and deletion (only by the creator) ✏️❌.
- Commenting and liking functionality on posts 💬👍.
- Profile page where users can view their posts 👤.
- Full authentication system using Flask-Login 🔒.

## Tech Stack 🛠️

- **Backend**: Flask
- **Database**: MongoDB (with GridFS for multimedia)
- **Authentication**: Flask-Login, Flask-Bcrypt
- **Frontend**: HTML, CSS, Bootstrap
- **Other**: PyMongo, GridFS

---

## What is MongoDB? 🌱

MongoDB is a **NoSQL** document-oriented database that stores data in flexible, JSON-like documents, which makes it easy to store, query, and manipulate complex data. Unlike traditional relational databases, MongoDB does not require predefined schemas and tables, providing more flexibility for developers to store and retrieve data. MongoDB is scalable and designed to handle large volumes of data, making it ideal for applications that need to process high amounts of unstructured data. In this project, MongoDB is used to store user data, posts, and multimedia content, while **GridFS** is used for storing large files such as images.

---

## Video Demonstration 🎥

![Video Demonstration](https://github.com/user-attachments/assets/b366a10b-3371-4031-8dd6-ce7c4e6691b7)

---

## Main Page 🏠

- **Endpoint**: `/`
- **Description**: The main page where users can view posts made by all registered users. Displays posts along with multimedia (images). Users can like, comment, and navigate to their profile from this page.
- **Functionalities**:
  - View all posts 📜.
  - Add a new post (if logged in) ➕.
  - View posts with multimedia files 📸.
  - Like and comment on posts ❤️💬.

---

## Login 🔑

- **Endpoint**: `/login`
- **Description**: The login page where users can authenticate themselves to access their account.
- **Methods**: `GET`, `POST`
- **Functionalities**:
  - **GET**: Displays the login form 📑.
  - **POST**: Takes the username and password, checks credentials, and logs the user in using Flask-Login 🔒.

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Authenticate and log in
```

---

## Register 🆕

- **Endpoint**: `/register`
- **Description**: The registration page where users can create a new account by providing a username and password.
- **Methods**: `GET`, `POST`
- **Functionalities**:
  - **GET**: Displays the registration form 📑.
  - **POST**: Registers the user, stores their username and hashed password, and redirects them to the login page 🛬.

```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Hash password and save user data
```

---

## Profile 👤

- **Endpoint**: `/profile`
- **Description**: The user profile page, where users can view all the posts they have made and manage their content.
- **Methods**: `GET`
- **Functionalities**:
  - Displays the logged-in user’s posts 📸.
  - Option to edit or delete own posts ✏️❌.

```python
@app.route('/profile')
@login_required
def profile():
    user_posts = mongo.db.posts.find({"user_id": current_user.username})
    return render_template('profile.html', user=current_user, posts=user_posts)
```

---

## All Posts 📜

- **Endpoint**: `/home`
- **Description**: Displays all posts from every user on the platform.
- **Methods**: `GET`
- **Functionalities**:
  - Shows all posts, including multimedia content and comments 🖼️💬.
  - Allows users to like or comment on posts ❤️💬.
  - Navigates to individual post details (edit, delete if owner) 🛠️.

```python
@app.route('/home')
def index():
    posts = mongo.db.posts.find()
    return render_template('index.html', posts=posts)
```

---

## Add Post ➕

- **Endpoint**: `/add_post`
- **Description**: Allows users to create and publish a new post, optionally including multimedia content.
- **Methods**: `GET`, `POST`
- **Functionalities**:
  - Users can add text and upload images (via GridFS) 📸.
  - The post is saved to MongoDB, and multimedia is stored using GridFS 📂.

```python
@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    if request.method == 'POST':
        post_text = request.form['text']
        # Handle multimedia file uploads
        post = {
            "user_id": current_user.username,
            "text": post_text,
            "multimedia": multimedia_files,
            "likes": 0,
            "comments": []
        }
        mongo.db.posts.insert_one(post)
```

---

## Edit Post ✏️

- **Endpoint**: `/edit_post/<post_id>`
- **Description**: Allows users to edit their own posts.
- **Methods**: `GET`, `POST`
- **Functionalities**:
  - Users can edit the text and replace multimedia of their own posts ✏️.
  - Only the original poster can edit the post 📝.

```python
@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    # Handle edit functionality
```

---

## Delete Post ❌

- **Endpoint**: `/delete_post/<post_id>`
- **Description**: Allows users to delete their own posts.
- **Methods**: `POST`
- **Functionalities**:
  - Only the post creator can delete the post and associated multimedia from GridFS 🗑️.

```python
@app.route('/delete_post/<post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    # Handle deletion logic
```

---

## Like Post ❤️

- **Endpoint**: `/like_post/<post_id>`
- **Description**: Allows users to like a post. A user can only like a post once.
- **Methods**: `POST`
- **Functionalities**:
  - Updates the "likes" list in the post document ❤️.
  - Prevents a user from liking the same post multiple times 🔒.

```python
@app.route('/like_post/<post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    # Logic to add like
```

---

## Comment on Post 💬

- **Endpoint**: `/add_comment/<post_id>`
- **Description**: Allows users to comment on posts.
- **Methods**: `POST`
- **Functionalities**:
  - Users can add comments to posts, which are stored within the post document 💬.

```python
@app.route('/add_comment/<post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    comment_text = request.form['comment']
    # Add comment to post
```

---

## License 📝

MIT License. See [LICENSE](LICENSE) for more details.

---

## Contributing 🤝

Feel free to fork this repository, make changes, and submit pull requests. All contributions are welcome!

---

## Contact 📧

For any questions or inquiries, feel free to contact me via my GitHub: [Bushra-Butt-17](https://github.com/Bushra-Butt-17).

---

## Screenshots 📸

### Main Page 🏠
![Screenshot 2](https://github.com/user-attachments/assets/b3dbdc92-aa21-498f-ae8a-7f8750d12dbf)
![Screenshot 20](https://github.com/user-attachments/assets/70d3ce38-7461-40c6-b1b7-ba89d8cdfb87)













### Login Page 🔑
![Screenshot 202](https://github.com/user-attachments/assets/7d309652-902b-4ebb-8179-aa2b64708c89)

![Screenshot 2](https://github.com/user-attachments/assets/154abde5-9cd7-4a07-85e4-ee3c790bef80)

### Profile Page 👤
![bush-profile-initial](https://github.com/user-attachments/assets/1b66f197-5c72-45ef-abff-6facdb60e81e)
![bush-profile](https://github.com/user-attachments/assets/c57e5805-5bd2-454a-8f4e-6c897f3ddbda)

![bush-profile-1](https://github.com/user-attachments/assets/cd7b0964-30ab-4941-b43d-d2a147ef0dbf)

![hasma-profile-1](https://github.com/user-attachments/assets/025cb7c9-593d-4023-9283-15c3120817cd)

[hasma-profile-2](https://github.com/user-attachments/assets/64ae082f-6d7c-4620-b441-47c1dc26c546)
![hasma-profile-3](https://github.com/user-attachments/assets/5d71db4e-046e-4a31-9147-8b5c4f58e23f)


### All Posts 📜

![Screenshot 2024-](https://github.com/user-attachments/assets/b67c7fce-9524-4072-8049-ea569822cffb)
![Screenshot 20240](https://github.com/user-attachments/assets/d328f9ae-68ef-4967-b7d2-68ec0f78386a)
![Screenshot 2024-](https://github.com/user-attachments/assets/0a17823a-508f-4cfa-b85c-659ef7516758)
```
