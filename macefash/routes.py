from flask import Flask, render_template, redirect, url_for, request, session, flash, Response
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from functools import wraps
from subprocess import Popen, PIPE
from random import randint, choice, sample, shuffle
from redirectSolver import solveRedirect
import macefash
from models import *
import os

basePic = 'https://graph.facebook.com/%s/picture?width=%s&height=%s'

""" AUTH SHIT """
def checkAuth(username, password):
    return (username, password) in [('schioara', 'oarba')] #this should probably be moved to the db in the future

def requiresAuth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.authorization
    if not auth or not checkAuth(auth.username, auth.password):
      return Response('sorry, can\'t let you in :-(\n', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    return f(*args, **kwargs)
  return decorated
""" /AUTH SHIT """

def sh(script):
  (out, err) = Popen(list(script.split()), stdout=PIPE).communicate()
  return str(out)

def getIP():
  ip = request.headers.get('X-Real-IP')
  if ip is None:
    ip = 'unknown'
  return ip

def getThemes():
  return sorted(db.session.query(Theme).all(), key=lambda x: x.name)

def getCurrentTheme():
  themeName = UserSettings.query.filter_by(ip=getIP()).first()
  themeName = themeName.theme if themeName is not None else "United"
  themeURL = Theme.query.filter_by(name=themeName).first().source

  return (themeName, themeURL)

def getCurrentGender():
  currentGender = UserSettings.query.filter_by(ip=getIP()).first()
  return currentGender.gender if currentGender is not None else False

def getGenderCount(gender):
  return len(Person.query.filter_by(gender=gender).all())

@app.route('/', methods=['GET', 'POST'])
def home():
  global basePic

  if request.method == 'POST':
    print "voted for %i"

  L, R = sample([x for x in db.session.query(Person).filter_by(gender=getCurrentGender()).all()], 2)

  picL = solveRedirect(basePic % (L.username, 500, 500))
  picR = solveRedirect(basePic % (R.username, 500, 500))

  return render_template(
          'home.html',
          L=L,
          R=R,
          picL=picL,
          picR=picR,
          ip=getIP(),
          currentGender=getCurrentGender(),
          currentTheme=getCurrentTheme(),
          themes=getThemes(),
          girls=getGenderCount(False),
          boys=getGenderCount(True),
          ungendered=getGenderCount(None),
          userIP=getIP()
          )

@app.route('/setTheme/<string:theme>')
def setTheme(theme):
  currentUser = UserSettings.query.filter_by(ip=getIP()).first()
  if currentUser is None:
    db.session.add(UserSettings(ip=getIP(), theme=theme))
    print "user %s selected theme <%s> for the first time" % (getIP(), theme)
  else:
    currentUser.theme = theme
    print "user %s changed theme to <%s>" % (getIP(), theme)

  db.session.commit()
  return redirect(url_for('home'))

@app.route('/setGender/<int:gender>')
def setGender(gender):
  gender = (gender == 1)
  currentUser = UserSettings.query.filter_by(ip=getIP()).first()
  if currentUser is None:
    db.session.add(UserSettings(ip=getIP(), gender=gender))
    print "user %s selected gender <%r> for the first time" % (getIP(), gender)
  else:
    currentUser.gender = gender
    print "user %s changed gender to <%r>" % (getIP(), gender)

  db.session.commit()
  return redirect(url_for('home'))

@app.route('/genderHelp')
@requiresAuth
def genderHelp():
  try:
    remaining = [x for x in db.session.query(Person).filter(and_(Person.gender==None, Person.hidden==False)).all()]
    entry = choice(remaining)
    #entry = db.session.query(Person).filter(and_(Person.gender==None, Person.hidden==False)).first() #by id
  except:
    print "no more genders to classify (probably)"
    return redirect(url_for('home'))

  pic = solveRedirect(basePic % (entry.username, 400, 400))
  girls = getGenderCount(False)
  boys = getGenderCount(True)
  ungendered = getGenderCount(None)

  total = len([x for x in db.session.query(Person).all()])
  classified = total - len(remaining)

  percentage = float("%.2f" % ((100.0 * classified) / total))

  return render_template(
          'genderclassifier.html',
          x=entry,
          pic=pic,
          currentGender=getCurrentGender(),
          currentTheme=getCurrentTheme(),
          themes=getThemes(),
          girls=girls,
          boys=boys,
          ungendered=ungendered,
          percentage=percentage
          )

@app.route('/classifyGender/<string:username>')
@app.route('/classifyGender/<string:username>/<int:newGender>')
@requiresAuth
def classifyGender(username=None, newGender=None):
  if username is None:
    print "username is None. dunno wot 2 do :-??"
    return redirect(url_for('genderHelp'))

  if newGender is not None:
    if newGender == 3:
      db.session.query(Person).filter_by(username=username).first().hidden = True
    else:
      db.session.query(Person).filter_by(username=username).first().gender = [False, True, None][newGender]

  db.session.commit()
  return redirect(url_for('genderHelp'))

@app.route('/all')
@app.route('/all/<int:page>')
@requiresAuth
def showAll(page=None):
  if page is None: page = 1
  onPage = 40

  entries = db.session.query(Person).all()
  #shuffle(entries)
  pages = len(entries) // onPage + (len(entries) % onPage != 0)
  firstNav, lastNav = max(1, page-3), min(page+3, pages)
  shownEntries = entries[(page-1)*onPage: min(len(entries), page*onPage)]

  return render_template(
          'all.html',
          entries=shownEntries,
          page=page,
          pages=pages,
          firstNav=firstNav,
          lastNav=lastNav,
          currentTheme=getCurrentTheme(),
          themes=getThemes(),
          girls=getGenderCount(False),
          boys=getGenderCount(True),
          ungendered=getGenderCount(None)
          )

@app.errorhandler(404)
def pageNotFound(e):
  return render_template(
          '404.html',
          currentTheme=getCurrentTheme(),
          themes=getThemes(),
          girls=getGenderCount(False),
          boys=getGenderCount(True),
          ungendered=getGenderCount(None)
          ), 404

