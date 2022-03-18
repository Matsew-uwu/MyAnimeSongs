from enum import unique
from os import name
from re import search
from sqlalchemy.orm import backref
from .app import db, ma
from flask_login import UserMixin
from sqlalchemy.sql.expression import desc
from sqlalchemy import delete

class Anime(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200))
    img = db.Column(db.String(200))
    text = db.Column(db.String(1000))
    
    def __repr__(self):
        return "<Anime (%d) %s>" % (self.id, self.name)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200))
    relation = db.Column(db.String(10))
    interpreter = db.Column(db.String(200))
    ytb_url = db.Column(db.String(200))
    spoty_url = db.Column(db.String(200))
    anime_id = db.Column(db.Integer, db.ForeignKey("anime.id"))
    anime = db.relationship("Anime", backref = db.backref("songs", lazy = "dynamic"))

    def __repr__(self):
        return "<Song (%d) %s>" % (self.id, self.title)
    
def create_song(anime_id, title, relation, interpreter, ytb_url, spoty_url):
    obj = Song(
        title = title,
        relation = relation,
        interpreter = interpreter,
        ytb_url = ytb_url,
        spoty_url = spoty_url,
        anime_id = anime_id
    )
    db.session.add(obj)
    db.session.commit()
    
def get_animes():
    return Anime.query.order_by('name').all()

def get_anime(id):
    return Anime.query.get_or_404(id)

def get_songs_anime(id):
    return Anime.query.get_or_404(id).songs.all()

def get_songs():
    return Song.query.order_by('title').all()

def get_song(id):
    return Song.query.get_or_404(id)

def get_opening_by_anime_id(id):
    return Song.query.filter_by(anime_id = id).filter(Song.relation.contains("OP")).all()  

def get_ending_by_anime_id(id):
    return Song.query.filter_by(anime_id = id).filter(Song.relation.contains("ED")).all() 

def get_ost_by_anime_id(id):
    return Song.query.filter_by(anime_id = id, relation = "OST").all()

def get_anime_by_name(name):
    return Anime.query.filter_by(name = name).first()
    
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(15), unique = True)
    email = db.Column(db.String(50), unique = True)
    password = db.Column(db.String(80))
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    role = db.relationship("Role", backref = db.backref("users", lazy = "dynamic"))
    
    def __repr__(self):
        return "<User (%d) %s %s %s>" % (self.id, self.username, self.email, self.role)
    
class Role(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), unique = True)
    
    def __repr__(self):
        return "<Role (%d) %s>" % (self.id, self.name)
    
def get_role_id(role_name):
    return Role.query.filter_by(name = role_name).first().id

def get_user(user_id):
    return User.query.get_or_404(int(user_id))

def get_user_by_username(username):
    return User.query.filter_by(username = username).first()

def get_user_by_email(email):
    return User.query.filter_by(email = email).first()

def get_users():
    return User.query.all()

def create_user(username, email, password, role_id):
    new_user = User(username = username, email = email, password = password, role_id = role_id)
    db.session.add(new_user)
    db.session.commit()
    return new_user

class SongRequest(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(200))
    relation = db.Column(db.String(10))
    interpreter = db.Column(db.String(200))
    ytb_url = db.Column(db.String(200))
    spoty_url = db.Column(db.String(200))
    anime_id = db.Column(db.Integer, db.ForeignKey("anime.id"))
    anime = db.relationship("Anime")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref = db.backref("song_requests", lazy = "dynamic"))
    status_id = db.Column(db.Integer, db.ForeignKey("status.id"))
    status = db.relationship("Status", backref = db.backref("song_requests", lazy = "dynamic"))

    def __repr__(self):
        return "<Song Request (%d) %s %s %s>" % (self.id, self.title, self.user, self.status)

class Status(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(40), unique = True)
    
    def __repr__(self):
        return "<Status (%d) %s>" % (self.id, self.name)
    
def create_song_request(title, interpreter, relation, ytb_url, spoty_url, anime_name, user_id):
    anime_id = get_anime_by_name(anime_name).id
    obj = SongRequest(
        title = title,
        relation = relation,
        interpreter = interpreter,
        ytb_url = ytb_url,
        spoty_url = spoty_url,
        anime_id = anime_id,
        user_id = user_id,
        status_id = 2
    )
    db.session.add(obj)
    db.session.commit()
    
def get_song_requests_by_username(username):
    return User.query.filter_by(username = username).first().song_requests.all()

def get_song_requests_by_user(user):
    return user.song_requests.all()

def get_song_request(id):
    return SongRequest.query.get_or_404(id)

def get_song_requests():
    return SongRequest.query.all()

def delete_request(request):
    db.session.delete(request)
    db.session.commit()
    
def get_status_by_name(name):
    return Status.query.filter_by(name = name).first()

def get_status_by_id(id):
    return Status.query.get(id)

def set_status(songRequest, name):
    songRequest.status_id = get_status_by_name(name).id
    db.session.commit()
    
class AnimeRequest(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200))
    img_url = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref = db.backref("anime_requests", lazy = "dynamic"))
    status_id = db.Column(db.Integer, db.ForeignKey("status.id"))
    status = db.relationship("Status", backref = db.backref("anime_requests", lazy = "dynamic"))

    def __repr__(self):
        return "<Anime Request (%d) %s %s %s>" % (self.id, self.name, self.user, self.status)
    
def create_anime_request(name, img_url, user_id):
    obj = AnimeRequest(
        name = name,
        img_url = img_url,
        user_id = user_id,
        status_id = 2
    )
    db.session.add(obj)
    db.session.commit()
    
def create_anime(name):
    obj = Anime(
        name = name
    )
    db.session.add(obj)
    db.session.commit()

def create_anime_from_api(name, img, text):
    obj = Anime(
        name = name,
        img = img,
        text = text
    )
    db.session.add(obj)
    db.session.commit()

    return obj
    
def get_anime_requests_by_user(user):
    return user.anime_requests.all()

def get_anime_request(id):
    return AnimeRequest.query.get_or_404(id)

def get_anime_requests():
    return AnimeRequest.query.all()

def edit_song(title, interpreter, relation, ytb_url, spoty_url, song): 
    song.title = title
    song.interpreter = interpreter
    song.relation = relation
    song.ytb_url = ytb_url
    song.spoty_url = spoty_url

    db.session.commit()
        
def edit_anime(img_url, text, anime): 
    anime.img = img_url
    anime.text = text

    db.session.commit()

def edit_anime_from_api(name, img_url, text, anime): 
    anime.img = img_url
    anime.text = text
    anime.name = name

    db.session.commit()

def edit_user(email, password, userEdit):
    userEdit.email = email
    userEdit.password = password

    db.session.commit()

def get_anime_by_filter(tag, page, rows_per_page):
    return Anime.query.filter(Anime.name.like(f'%{tag}%')).paginate(page = page, per_page = rows_per_page)

class Favorites(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key = True)
    user = db.relationship("User", backref = db.backref("favorites", lazy = "dynamic"))
    song_id = db.Column(db.Integer, db.ForeignKey("song.id"), primary_key = True)
    song = db.relationship("Song")

    def __repr__(self):
        return "<Favoris %s %s>" % (self.user, self.song)

def add_favorite(user_id, song_id):
    obj = Favorites(
        user_id = user_id,
        song_id = song_id
    )
    db.session.add(obj)
    db.session.commit()

def remove_favorite(user_id, song_id):
    db.session.delete(get_favorite(user_id, song_id))
    db.session.commit()

def get_favorites_of_user(user):
    return user.favorites.all()

def get_favorite(user_id, song_id):
    return Favorites.query.filter(Favorites.song_id == song_id and Favorites.user_id == user_id).first()

def get_favorites_songs_of_user(user):
    return [favorite.song.id for favorite in get_favorites_of_user(user)]

def get_animes_pagination(page, rows_per_page):
    return Anime.query.paginate(page = page, per_page = rows_per_page)

def get_songs_pagination(page, rows_per_page):
    return Song.query.paginate(page = page, per_page = rows_per_page)

def get_song_by_filter(tag, page, rows_per_page):
    return Song.query.filter(Song.title.like(f'%{tag}%')).paginate(page = page, per_page = rows_per_page)

def get_songs_by_name_pagination_ascendant(page, rows_per_page):
    return Song.query.order_by(Song.title).paginate(page = page, per_page = rows_per_page)

def get_songs_by_name_pagination_descendant(page, rows_per_page):
    return Song.query.order_by(desc(Song.title)).paginate(page = page, per_page = rows_per_page)

def get_songs_by_relation_pagination(page, rows_per_page):
    return Song.query.order_by(Song.relation).paginate(page = page, per_page = rows_per_page)

def get_ost(page, rows_per_page):
    return Song.query.filter(Song.relation.like("OST")).paginate(page = page, per_page = rows_per_page)

def get_ed(page, rows_per_page):
    return Song.query.filter(Song.relation.like("ED%")).paginate(page = page, per_page = rows_per_page)

def get_op(page, rows_per_page):
    return Song.query.filter(Song.relation.like("OP%")).paginate(page = page, per_page = rows_per_page)

def remove_song(song_id):
    favoris = Favorites.query.filter(Favorites.song_id == song_id).all()
    for favori in favoris:
        db.session.delete(favori)
    db.session.delete(get_song(song_id))
    db.session.commit()

def remove_anime(anime_id):
    songs = Song.query.filter(Song.anime_id == anime_id).all()
    for song in songs:
        favoris = Favorites.query.filter(Favorites.song_id == song.id).all()
        for favori in favoris:
            db.session.delete(favori)
        db.session.delete(song)
    db.session.delete(get_anime(anime_id))
    db.session.commit()

# DB Marshmallow Schemas

# Song
class AnimeSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "img", "text")


# Anime
class SongSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "relation", "interpreter", "ytb_url", "spoty_url", "anime_id", "anime")

# Init Schema
anime_schema = AnimeSchema()
animes_schema = AnimeSchema(many=True)
song_schema = SongSchema()
songs_schema = SongSchema(many=True)