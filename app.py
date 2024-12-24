#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from models import db, Venue, Artist, Show
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    recent_artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
    recent_venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
    return render_template('pages/home.html', recent_artists=recent_artists, recent_venues=recent_venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # Fetch distinct city-state pairs
    cities_states = db.session.query(Venue.city, Venue.state).distinct().all()
    data = []

    for city, state in cities_states:
        # Fetch venues for each city-state pair
        venues = Venue.query.filter_by(city=city, state=state).all()
        venue_data = []
        for venue in venues:
            # Count upcoming shows for each venue
            num_upcoming_shows = db.session.query(Show).filter(
                Show.venue_id == venue.id, Show.start_time > datetime.now()
            ).count()
            venue_data.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": num_upcoming_shows
            })
        data.append({
            "city": city,
            "state": state,
            "venues": venue_data
        })

    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    # Fetch venues matching the search term
    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    response = {
        "count": len(venues),
        "data": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": db.session.query(Show).filter(
                Show.venue_id == venue.id, Show.start_time > datetime.now()
            ).count()
        } for venue in venues]
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)

    # Fetch past shows
    past_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id, Show.start_time < datetime.now()
    ).all()

    # Fetch upcoming shows
    upcoming_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id, Show.start_time > datetime.now()
    ).all()

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": [{
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        } for show in past_shows],
        "upcoming_shows": [{
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        } for show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    try:
        # Create a new Venue instance
        new_venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            website=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data,
            image_link=form.image_link.data
        )
        db.session.add(new_venue)
        db.session.commit()
        flash(f'Venue "{new_venue.name}" was successfully listed!')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred. Venue "{form.name.data}" could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get_or_404(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash(f'Venue "{venue.name}" was successfully deleted!')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred. Venue could not be deleted.')
    finally:
        db.session.close()
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.all()
    data = [{"id": artist.id, "name": artist.name} for artist in artists]
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    # Search artists matching the search term
    artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    response = {
        "count": len(artists),
        "data": [{
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": db.session.query(Show).filter(
                Show.artist_id == artist.id, Show.start_time > datetime.now()
            ).count()
        } for artist in artists]
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)

    # Fetch past shows
    past_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id, Show.start_time < datetime.now()
    ).all()

    # Fetch upcoming shows
    upcoming_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id, Show.start_time > datetime.now()
    ).all()

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": [{
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        } for show in past_shows],
        "upcoming_shows": [{
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        } for show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    form = ArtistForm(request.form)
    try:
        form.populate_obj(artist)
        db.session.commit()
        flash(f'Artist "{artist.name}" was successfully updated!')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred. Artist "{artist.name}" could not be updated.')
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(obj=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm(request.form)
    try:
        form.populate_obj(venue)
        db.session.commit()
        flash(f'Venue "{venue.name}" was successfully updated!')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred. Venue "{venue.name}" could not be updated.')
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
    form = ArtistForm(request.form)
    try:
        new_artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            website=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data,
            image_link=form.image_link.data
        )
        db.session.add(new_artist)
        db.session.commit()
        flash(f'Artist "{new_artist.name}" was successfully listed!')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred. Artist "{form.name.data}" could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = db.session.query(Show).join(Artist).join(Venue).all()
    data = [{
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    } for show in shows]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    try:
        new_show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data
        )
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('index'))


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
