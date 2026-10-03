from datetime import datetime

from app import db


class FoodBank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(255))
    postcode = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    need_level = db.Column(db.String(20), default="medium", nullable=False)  # low/medium/high/urgent
    needed_items = db.Column(db.String(255))

    # % of typical stock needed per category, shown as bars on the donate page
    need_protein_pct = db.Column(db.Integer, default=50, nullable=False)
    need_carbs_pct = db.Column(db.Integer, default=50, nullable=False)
    need_fats_pct = db.Column(db.Integer, default=50, nullable=False)
    need_fiber_pct = db.Column(db.Integer, default=50, nullable=False)
    need_fruit_veg_pct = db.Column(db.Integer, default=50, nullable=False)
    need_tinned_goods_pct = db.Column(db.Integer, default=50, nullable=False)

    donations = db.relationship("Donation", backref="food_bank", lazy=True)
    delivery_requests = db.relationship("DeliveryRequest", backref="food_bank", lazy=True)
    collection_slots = db.relationship(
        "CollectionSlot",
        backref="food_bank",
        lazy=True,
        order_by="CollectionSlot.day_of_week",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "address": self.address,
            "postcode": self.postcode,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "need_level": self.need_level,
            "needed_items": self.needed_items,
            "open_delivery_requests": sum(
                1 for d in self.delivery_requests if d.status == "open"
            ),
        }


class CollectionSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_bank_id = db.Column(db.Integer, db.ForeignKey("food_bank.id"), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Mon ... 6=Sun
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    notes = db.Column(db.String(255))


class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_name = db.Column(db.String(120), nullable=False)
    donor_email = db.Column(db.String(120), nullable=False)
    items = db.Column(db.String(500), nullable=False)  # comma-separated
    notes = db.Column(db.Text)
    food_bank_id = db.Column(db.Integer, db.ForeignKey("food_bank.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(30))
    city = db.Column(db.String(80))
    has_vehicle = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    deliveries = db.relationship("DeliveryRequest", backref="volunteer", lazy=True)
    availability = db.relationship(
        "VolunteerAvailability",
        backref="volunteer",
        lazy=True,
        order_by="VolunteerAvailability.day_of_week",
    )


class VolunteerAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey("volunteer.id"), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)


class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    address = db.Column(db.String(255))
    city = db.Column(db.String(80), nullable=False)
    postcode = db.Column(db.String(20))
    household_size = db.Column(db.Integer, default=1, nullable=False)
    dietary_needs = db.Column(db.String(255))
    notes = db.Column(db.Text)

    preferred_food_bank_id = db.Column(db.Integer, db.ForeignKey("food_bank.id"), nullable=True)
    preferred_food_bank = db.relationship("FoodBank", backref="recipients", lazy=True)

    status = db.Column(db.String(20), default="pending", nullable=False)  # pending/contacted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DeliveryBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey("recipient.id"), nullable=False)
    food_bank_id = db.Column(db.Integer, db.ForeignKey("food_bank.id"), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey("volunteer.id"), nullable=True)

    day_of_week = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    notes = db.Column(db.Text)

    status = db.Column(db.String(20), default="requested", nullable=False)  # requested/booked/completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    recipient = db.relationship("Recipient", backref="delivery_bookings", lazy=True)
    food_bank = db.relationship("FoodBank", backref="delivery_bookings", lazy=True)
    volunteer = db.relationship("Volunteer", backref="delivery_bookings", lazy=True)


class DeliveryRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pickup_location = db.Column(db.String(255), nullable=False)
    food_bank_id = db.Column(db.Integer, db.ForeignKey("food_bank.id"), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey("volunteer.id"), nullable=True)
    status = db.Column(db.String(20), default="open")  # open/claimed/completed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
