import os
import requests as requests
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from numerize import numerize

MOVIE_API = os.environ.get('MOVIE_API')
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_IMAGE_URL = "https://image.tmdb.org/t/p/original"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movie_details.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)


class Movie_Details(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    movie_id = db.Column(db.Integer)
    title = db.Column(db.String(20))
    description = db.Column(db.String(5000))
    imbd = db.Column(db.Float)
    quote = db.Column(db.String(250))
    background_url = db.Column(db.String(250))
    poster_url = db.Column(db.String(250))
    runtime = db.Column(db.INTEGER)
    budget = db.Column(db.String)
    revenue = db.Column(db.String)
    release_date = db.Column(db.INTEGER)
    genre = db.Column(db.String(50))
    time = db.Column(db.Time)


@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/')
def home():
    movies = Movie_Details.query.order_by(Movie_Details.imbd).all()
    high_rated = movies[-5:]
    all_movies = Movie_Details.query.all()
    return render_template('home.html', high_rated=high_rated, enumurate=enumerate, len=len, all_movies=all_movies)


@app.route('/add')
def add_movie():
    return render_template('add.html')


@app.route('/find-movie', methods=['GET', 'POST'])
def find_movie():
    if request.method == "POST":
        global quote, imbd
        title = request.form.get('movie_title')
        quote = request.form.get('movie_quote')
        imbd = request.form.get('movie_imbd')
        response = requests.get(MOVIE_DB_SEARCH_URL, params={"api_key": MOVIE_API, "language": "en-US", "query": title})
        data = response.json()["results"]
        num_movie = len(data)
        return render_template('select.html', options=data, num_of_movie=num_movie, img_url=MOVIE_IMAGE_URL)
    return render_template('movie_details.html')


@app.route('/select-movie')
def select_movie():
    return render_template('select.html')


@app.route('/selected-movie')
def selected_movie():
    movie_id = request.args.get('id')
    if movie_id:
        movie_api_url = f'{MOVIE_DB_INFO_URL}/{movie_id}'
        response = requests.get(movie_api_url, params={'api_key': MOVIE_API, 'language': 'en-US'})
        data = response.json()
        new_movie = Movie_Details(
            title=data['title'],
            description=data['overview'],
            background_url=f"{MOVIE_IMAGE_URL}{data['backdrop_path']}",
            poster_url=f"{MOVIE_IMAGE_URL}{data['poster_path']}",
            runtime=f"{data['runtime']}min",
            release_date=data['release_date'].split('-')[0],
            revenue=numerize.numerize(data['revenue'], 2),
            budget=numerize.numerize(data['budget'], 2),
            quote=quote,
            imbd=imbd,
            movie_id=data['id'],
            genre=data['genres'][0]['name']

        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/movie-detail-viewer')
def movie_detail_viewer():
    movie_id = request.args.get('id')
    data = Movie_Details.query.filter_by(movie_id=movie_id).first()
    print(data)
    return render_template('movie_viewer.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
