"""
Defines the models upon which
the database tables are based.
"""
from app import db


class Person(db.Model):
    __tablename__ = "person"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    gender = db.Column(db.Boolean, unique=False, nullable=True)
    city = db.Column(db.String, unique=False, nullable=True)
    school = db.Column(db.String, unique=False, nullable=True)

    rating = db.Column(db.Integer, unique=False, nullable=True)
    maxRating = db.Column(db.Integer, unique=False, nullable=True)
    kFactor = db.Column(db.Integer, unique=False, nullable=True)

    games = db.Column(db.Integer, unique=False, nullable=True)
    wins = db.Column(db.Integer, unique=False, nullable=True)

    hidden = db.Column(db.Boolean, unique=False, nullable=True)

    def __init__(
            self,
            username,
            gender=None,
            city=None,
            school=None,
            rating=1500,
            maxRating=1500,
            kFactor=40,
            games=0,
            wins=0,
            hidden=False
            ):
        self.username = username
        self.gender = gender
        self.city = city
        self.school = school
        self.rating = rating
        self.maxRating = maxRating
        self.kFactor = kFactor
        self.games = games
        self.wins = wins
        self.hidden = hidden

    def __repr__(self):
        return self.username


class Vote(db.Model):
    __tablename__ = 'vote'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String, unique=False, nullable=True)
    winner = db.Column(db.Integer, unique=False, nullable=True)
    loser = db.Column(db.Integer, unique=False, nullable=True)
    when = db.Column(db.String, unique=False, nullable=True)

    def __init__(self, ip, winner, loser, when):
        self.ip = ip
        self.winner = winner
        self.loser = loser
        self.when = when

    def __repr__(self):
        return "%s voted (%i, %i) at %s" % (self.ip, self.winner, self.loser, self.when)


class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=False, nullable=True)
    ip = db.Column(db.String, unique=False, nullable=True)
    message = db.Column(db.String, unique=False, nullable=False)
    when = db.Column(db.String, unique=False, nullable=True)

    def __init__(self, name, ip, message, when):
        self.name = name
        self.ip = ip
        self.message = message
        self.when = when

    def __repr__(self):
        return "%s (ip = %s) wrote: %s" % (self.name, self.ip, self.message)


class Theme(db.Model):
    __tablename__ = 'theme'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    source = db.Column(db.String, unique=True, nullable=False)

    def __init__(self, name, source):
        self.name = name
        self.source = source

    def __repr__(self):
        return "themeName: <%s>" % self.name


class Preference(db.Model):
    __tablename__ = 'preference'

    ip = db.Column(db.String, primary_key=True, nullable=True)
    theme = db.Column(db.String, unique=False, nullable=False)
    gender = db.Column(db.Boolean, unique=False, nullable=True)

    def __init__(self, ip, theme=None, gender=None):
        self.ip = ip
        self.theme = theme if theme is not None else "Standard"
        self.gender = gender if gender is not None else False

    def __repr__(self):
        return "ip %s wants:\n---> theme: <%s>\n---> gender: %r" % (self.ip, self.theme, self.gender)