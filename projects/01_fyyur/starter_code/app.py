#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from werkzeug import datastructures
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
from datetime import date
from models import Venue, Artist, Show, db, app
import sys

# TODO: connect to a local postgresql database

# Fix turn genres into list
def string_to_list(record):
  parsed = record.replace("{", "")
  parsed = parsed.replace("}", "")
  parsed = parsed.split(',')

  return parsed


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  value = str(value)
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  venues = Venue.query.order_by(Venue.id.desc()).limit(3)

  return render_template('pages/home.html', venues=venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  #cities = Venue.query.distinct(Venue.city, Venue.state).all()
 
  # Get all venues back from the database
  venues = Venue.query.all()

  # Create empty cities and areas lists
  cities = []
  areas = []

  # Create distinct list of cities
  for venue in venues:
    cities.append((venue.city, venue.state))
    cities = list(set(cities))

  #Return a list of city objects called areas
  for city in cities:
    # Create a list item for each distinct city
    city_obj = {
      'city': city[0], 
      'state': city[1],
      'venues': []
    }

    areas.append(city_obj)  

    # Add venue object to the venues item
    for venue in venues:
      if city[0] == venue.city:
        
        venue_obj = {
          'id': venue.id, 
          'name': venue.name
        }

        city_obj['venues'].append(venue_obj)

  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST', 'GET'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # Get search term from form
  search_term = request.form.get('search_term', '')

  # Query the database for results that ilike the search term
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  # Add query results along with count
  response = {
    "count": len(venues), 
    "data": venues
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # Get the venue
  # If no shows and inner join is empty, ignore the joins
  if Venue.query.filter_by(id=venue_id).join(Show).join(Artist).first():
    venue = Venue.query.filter_by(id=venue_id).join(Show).join(Artist).first()
  else:
    venue = Venue.query.filter_by(id=venue_id).first()

  data = venue

  # Function defined in below models logic in app.py
  data.genres = string_to_list(data.genres)

  today = datetime.now()
  
  data.upcoming_shows = []
  data.past_shows = []

  for show in data.shows:
    if show.start_time>today:
      upcoming_show = {
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time
      }
      data.upcoming_shows.append(upcoming_show)  
    else:
      past_show = {
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time
      }
      data.past_shows.append(past_show)
  
  data.upcoming_shows_count = len(data.upcoming_shows)
  data.past_shows_count = len(data.past_shows)

  return render_template('pages/show_venue.html', venue=data)
  #return render_template('pages/home.html')

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  
  try:

    venue = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data, 
      website_link=form.website_link.data, 
      seeking_talent=form.seeking_talent.data,
      seeking_description=form.seeking_description.data
    )

    db.session.add(venue)
    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    # Error message
    flash('Venue ' + request.form['name'] + ' encountered an error and could not be listed. Crikey!')
    print(sys.exc_info())

  finally: 
    db.session.close()


  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' has been deleted. Good riddance.')
  except:
    db.session.rollback()
     # Error message
    flash('We encountered an error and ' + venue.name + ' could not be deleted. Saved by the database')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST', 'GET'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term=request.form.get('search_term', '')
  #Venue.query.filter_by(id=venue_id).join(Show).join(Artist).first()

  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).join(Show, isouter=True).all()
  
  response = {
    "count": len(artists),
    "data": artists
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  if Artist.query.filter_by(id=artist_id).join(Show).join(Venue).first():
    artist = Artist.query.filter_by(id=artist_id).join(Show).join(Venue).first()
  else:
    artist = Artist.query.get(artist_id)

  artist.past_shows = []
  artist.upcoming_shows = []

  now = datetime.now()

  artist.genres = string_to_list(artist.genres)

  for show in artist.shows:
    show_to_add = {
      "venue_id": show.venue_id,
      "start_time": show.start_time,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link
    }
    
    if show.start_time > now:
      artist.upcoming_shows.append(show_to_add)
    else:
      artist.past_shows.append(show_to_add)
  
  artist.upcoming_shows_count = len(artist.upcoming_shows)
  artist.past_shows_count = len(artist.past_shows)
  

  #return redirect(url_for('index'))
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()

  try:
    artist = db.session.query(Artist).filter(Artist.id == artist_id).first()

    # Update fields only if there is something listed
    def update_if_there(fields):
      for field in fields:
        if form[field].data:
          setattr(artist, field, form[field].data)

    update_if_there(['name', 'phone', 'city', 'state', 'genres', 'facebook_link', 'image_link'])

    db.session.add(artist)
    db.session.commit()

    flash('Artist ' + artist.name + ' has been updated. Times are changing!')

  except:
    db.session.rollback()
    flash('Artist ' + artist.name + ' has NOT been updated. What did you do?')

  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue=Venue.query.get(venue_id)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()

  try:
    venue = Venue.query.get(venue_id)

    # Update fields only if there is something listed
    def update_if_there(fields):
      for field in fields:
        if form[field].data:
          setattr(venue, field, form[field].data)

    update_if_there(['name', 'phone', 'city', 'state', 'address', 'genres', 'facebook_link', 'image_link'])

    db.session.add(venue)
    db.session.commit()

    flash('Venue ' + venue.name + ' has been updated. Times are changing!')

  except:
    db.session.rollback()
    flash('Venue ' + venue.name + ' has NOT been updated. What did you do?')

  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  try:
    form = ArtistForm()

    artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website_link=form.website_link.data, 
      seeking_venue=form.seeking_venue.data,
      seeking_description=form.seeking_description.data
    )

    db.session.add(artist)
    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()

    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed. Bummer dude')
    print(sys.exc_info())

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows = Show.query.join(Venue).join(Artist).all()

  data = []

  for show in shows:
    obj = {
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time
    }
    data.append(obj)

    print(data)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    form = ShowForm()

    show = Show(
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
      start_time=form.start_time.data
    )

    db.session.add(show)
    db.session.commit()

      # on successful db insert, flash success
    flash('Show was successfully listed!')

  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')

  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
