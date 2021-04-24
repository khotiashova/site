from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from data import db_session, news_api
from flask_login import LoginManager, login_user
from forms.login import LoginForm
from forms.register import RegisterForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # bd
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class Article(db.Model):  # class of topic
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)  # introduse
    text = db.Column(db.Text, nullable=False)  # main text
    date = db.Column(db.DateTime, default=datetime.utcnow)  # date of publication

    def __repr__(self):
        return '<Article %r>' % self.id  # object + id


@app.route('/')  # main page
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/coffee')  # first ssilka
def coffee():
    return render_template('coffee.html')


@app.route('/posts')  # slezka za postsmi
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template('posts.html', articles=articles)


@app.route('/posts/<int:id>')  # slezka za postsmi
def post_detail(id):
    article = Article.query.get(id)
    return render_template('post-detail.html', article=article)


@app.route('/posts/<int:id>.del')  # slezka za postsmi
def post_del(id):
    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return 'При удалении статьи произошла ошибка'


@app.route('/eto')  # second ssilka
def eto():
    return render_template('eto.html')


@app.route('/create_article', methods=['POST', 'GET'])  # create topic
def create_article():
    if request.method == 'POST':
        title = request.form['title']
        intro = request.form['into']
        text = request.form['text']

        article = Article(title=title, intro=intro, text=text)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/')

        except:
            return 'При добавлении статьи произошла ошибка'
    else:
        return render_template('create_article.html')


@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])  # create topic
def post_update():
    article = Article.query.get(id)
    if request.method == 'POST':
        article.title = request.form['title']
        article.intro = request.form['into']
        article.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/posts')

        except:
            return 'При редактировании статьи произошла ошибка'
    else:
        return render_template('post-update.html', article=article)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('auth.html', message="Wrong pass/login")
    return render_template('auth.html', title='Auth', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    app.run(debug=True)
