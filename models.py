from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    # admin, organizer, attendee
    role = db.Column(db.String(20), default='attendee')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    organizer_profile = db.relationship(
        'OrganizerProfile', backref='user', uselist=False)
    reviews = db.relationship('Review', backref='author', lazy=True)
    tickets = db.relationship('Ticket', backref='user', lazy=True)
    organized_events = db.relationship(
        'Event', backref='organizer_user', lazy=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class OrganizerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    organization = db.Column(db.String(100))
    bio = db.Column(db.Text)
    website = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Remove the events relationship for now
    # events = db.relationship('Event', backref='organizer', lazy=True)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.String(10))
    location = db.Column(db.String(200))
    address = db.Column(db.String(300))
    image = db.Column(db.String(200), default='default_event.jpg')
    price = db.Column(db.Float, default=0.0)
    capacity = db.Column(db.Integer, default=100)
    available_tickets = db.Column(db.Integer, default=100)
    category = db.Column(db.String(50))  # String field, not foreign key
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    weather_data = db.Column(db.Text)

    tickets = db.relationship('Ticket', backref='event', lazy=True)
    bookings = db.relationship('Booking', backref='event', lazy=True)
    reviews = db.relationship('Review', backref='event', lazy=True)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    qr_code = db.Column(db.String(200))
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    # active, used, cancelled
    status = db.Column(db.String(20), default='active')


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(20), unique=True, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tickets_count = db.Column(db.Integer, default=1)
    total_amount = db.Column(db.Float, nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    # pending, confirmed, cancelled
    status = db.Column(db.String(20), default='pending')


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey(
        'booking.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100), unique=True)
    # pending, completed, failed
    status = db.Column(db.String(20), default='pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    booking = db.relationship('Booking', backref='payment', uselist=False)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
