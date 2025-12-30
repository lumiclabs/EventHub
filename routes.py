from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Event, Booking
from app.forms import RegistrationForm, LoginForm, EventForm, ProfileEditForm
from app.forms import EventForm
from datetime import datetime
import os

# We'll create a Blueprint for routes
from flask import Blueprint

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=(form.remember.data == 'yes'))
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login failed. Check email and password.', 'danger')

    return render_template('login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@main.route('/dashboard')
@login_required
def dashboard():
    # Get events created by the current user
    user_events = Event.query.filter_by(
        organizer_id=current_user.id).order_by(Event.created_at.desc()).all()

    # Get user's bookings (if they exist in your model)
    user_bookings = []
    if hasattr(current_user, 'bookings'):
        user_bookings = current_user.bookings

    return render_template('dashboard.html', events=user_events, bookings=user_bookings)


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileEditForm(original_email=current_user.email)

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data

        db.session.commit()
        flash('Your profile has been updated successfully!', 'success')
        return redirect(url_for('main.profile'))

    # Pre-fill form with current user data
    if request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.phone.data = current_user.phone

    return render_template('profile.html', form=form)


@main.route('/events')
def events():
    # Get search parameters
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '')
    date_filter = request.args.get('date', '')

    # Start with base query
    query = Event.query.filter_by(status='active')

    # Apply search filter
    if search_query:
        query = query.filter(
            (Event.title.ilike(f'%{search_query}%')) |
            (Event.description.ilike(f'%{search_query}%'))
        )

    # Apply category filter
    if category_filter:
        query = query.filter_by(category=category_filter)

    # Apply date filter
    if date_filter:
        # Convert string date to datetime
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d')
            query = query.filter(db.func.date(Event.date)
                                 == filter_date.date())
        except ValueError:
            pass  # If date format is invalid, ignore the filter

    # Order and execute
    events_list = query.order_by(Event.date.asc()).all()

    return render_template('events.html', events=events_list)


@main.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event_detail.html', event=event)


@main.route('/event/create', methods=['GET', 'POST'])
@login_required
def create_event():

    if current_user.role not in ['organizer', 'admin']:
        flash('Only organizers and admins can create events!', 'danger')
        return redirect(url_for('main.dashboard'))

    form = EventForm()

    if form.validate_on_submit():
        # Combine date and time
        event_datetime = datetime.combine(form.date.data, form.time.data)

        # Create event object
        event = Event(
            title=form.title.data,
            description=form.description.data,
            date=event_datetime,
            time=form.time.data.strftime('%H:%M'),
            location=form.location.data,
            address=form.address.data,
            category=form.category.data,
            price=form.price.data,
            capacity=form.capacity.data,
            available_tickets=form.capacity.data,
            organizer_id=current_user.id,
            status='active'
        )

        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('main.events'))

    return render_template('create_event.html', form=form)


@main.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    # Check if current user is the organizer
    if event.organizer_id != current_user.id:
        flash('You can only edit your own events!', 'danger')
        return redirect(url_for('main.events'))

    form = EventForm()

    if form.validate_on_submit():
        # Update event with form data
        event.title = form.title.data
        event.description = form.description.data
        event.date = datetime.combine(form.date.data, form.time.data)
        event.time = form.time.data.strftime('%H:%M')
        event.location = form.location.data
        event.address = form.address.data
        event.category = form.category.data
        event.price = form.price.data
        event.capacity = form.capacity.data

        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('main.event_detail', event_id=event.id))

    # Pre-fill form with existing data for GET request
    if request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.date.data = event.date.date()
        form.time.data = datetime.strptime(event.time, '%H:%M').time()
        form.location.data = event.location
        form.address.data = event.address
        form.category.data = event.category
        form.price.data = event.price
        form.capacity.data = event.capacity

    return render_template('edit_event.html', form=form, event=event)


@main.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    # Check if current user is the organizer
    if event.organizer_id != current_user.id:
        flash('You can only delete your own events!', 'danger')
        return redirect(url_for('main.events'))

    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('main.events'))


@main.route('/event/<int:event_id>/book', methods=['POST'])
@login_required
def book_event(event_id):
    event = Event.query.get_or_404(event_id)

    # Check if user is the organizer (can't book own event)
    if event.organizer_id == current_user.id:
        flash('You cannot book your own event!', 'danger')
        return redirect(url_for('main.event_detail', event_id=event.id))

    # Check ticket availability
    if event.available_tickets < 1:
        flash('No tickets available!', 'danger')
        return redirect(url_for('main.event_detail', event_id=event.id))

    # Generate booking number
    import random
    import string
    booking_number = 'BK-' + \
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # Create booking
    booking = Booking(
        booking_number=booking_number,
        event_id=event.id,
        user_id=current_user.id,
        tickets_count=1,
        total_amount=event.price,
        status='confirmed'
    )
    db.session.add(booking)

    # Update available tickets
    event.available_tickets -= 1

    db.session.commit()
    flash(
        f'Booking successful! Your booking number: {booking_number}', 'success')
    return redirect(url_for('main.dashboard'))


@main.route('/create-admin')
def create_admin():
    # Check if admin already exists
    admin = User.query.filter_by(email='admin@eventapp.com').first()
    if not admin:
        admin = User(
            name='Admin User',
            email='admin@eventapp.com',
            phone='1234567890',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        return 'Admin user created: admin@eventapp.com / admin123'
    return 'Admin user already exists'


@main.route('/admin')
@login_required
def admin_dashboard():
    # Check if user is admin
    if current_user.role != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('main.dashboard'))

    # Get all data for admin
    total_users = User.query.count()
    total_events = Event.query.count()
    total_bookings = Booking.query.count()

    # Get recent activities
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_events = Event.query.order_by(
        Event.created_at.desc()).limit(5).all()
    recent_bookings = Booking.query.order_by(
        Booking.booking_date.desc()).limit(5).all()

    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_events=total_events,
                           total_bookings=total_bookings,
                           recent_users=recent_users,
                           recent_events=recent_events,
                           recent_bookings=recent_bookings)
