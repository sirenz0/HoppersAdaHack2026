from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app import db
from app.constants import DAYS_OF_WEEK, TIME_PERIODS, format_time_range
from app.models import DeliveryBooking, DeliveryRequest, Volunteer, VolunteerAvailability

volunteers_bp = Blueprint("volunteers", __name__, url_prefix="/volunteer")


@volunteers_bp.route("/")
def landing():
    pickup_opportunities = [
        {
            "id": d.id,
            "kind": "pickup",
            "title": "Food collection",
            "subtitle": f"Pick up from {d.pickup_location}",
            "detail": f"Deliver to {d.food_bank.name}",
            "notes": d.notes,
        }
        for d in DeliveryRequest.query.filter_by(status="open").all()
    ]

    delivery_opportunities = [
        {
            "id": b.id,
            "kind": "delivery",
            "title": "Deliveries",
            "subtitle": f"{DAYS_OF_WEEK[b.day_of_week]}, {format_time_range(b.start_time, b.end_time)}",
            "detail": f"From {b.food_bank.name} to a recipient in {b.recipient.city}",
            "notes": b.notes,
        }
        for b in DeliveryBooking.query.filter_by(status="requested").all()
    ]

    return render_template(
        "volunteer_landing.html",
        pickup_opportunities=pickup_opportunities,
        delivery_opportunities=delivery_opportunities,
    )


@volunteers_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        volunteer = Volunteer(
            name=request.form["name"],
            email=request.form["email"],
            phone=request.form.get("phone"),
            city=request.form.get("city"),
            has_vehicle=bool(request.form.get("has_vehicle")),
        )
        db.session.add(volunteer)
        db.session.flush()  # assign volunteer.id before creating availability rows

        period = request.form.get("period", "morning")
        start_time, end_time = TIME_PERIODS.get(period, TIME_PERIODS["morning"])

        for day_str in request.form.getlist("days"):
            db.session.add(
                VolunteerAvailability(
                    volunteer_id=volunteer.id,
                    day_of_week=int(day_str),
                    start_time=start_time,
                    end_time=end_time,
                )
            )

        db.session.commit()
        flash("Thanks for signing up to volunteer!", "success")
        return redirect(url_for("volunteers.landing"))

    dev_volunteers = (
        Volunteer.query.order_by(Volunteer.id.desc()).limit(10).all()
        if current_app.debug
        else []
    )

    return render_template(
        "volunteer_signup.html", days_of_week=DAYS_OF_WEEK, dev_volunteers=dev_volunteers
    )


@volunteers_bp.route("/claim/<int:delivery_id>", methods=["POST"])
def claim_delivery(delivery_id):
    delivery = DeliveryRequest.query.get_or_404(delivery_id)
    email = request.form.get("volunteer_email", "").strip().lower()
    volunteer = Volunteer.query.filter_by(email=email).first()

    if not volunteer:
        flash("We couldn't find a volunteer with that email. Please sign up first.", "error")
    elif delivery.status != "open":
        flash("Sorry, that pickup has already been claimed.", "error")
    else:
        delivery.volunteer_id = volunteer.id
        delivery.status = "claimed"
        db.session.commit()
        flash("Pickup claimed — thank you!", "success")

    return redirect(url_for("volunteers.landing"))


@volunteers_bp.route("/book-delivery/<int:booking_id>", methods=["POST"])
def book_delivery(booking_id):
    booking = DeliveryBooking.query.get_or_404(booking_id)
    email = request.form.get("volunteer_email", "").strip().lower()
    volunteer = Volunteer.query.filter_by(email=email).first()

    if not volunteer:
        flash("We couldn't find a volunteer with that email. Please sign up first.", "error")
    elif booking.status != "requested":
        flash("Sorry, that delivery has already been booked.", "error")
    else:
        booking.volunteer_id = volunteer.id
        booking.status = "booked"
        db.session.commit()
        flash("Delivery booked — thank you!", "success")

    return redirect(url_for("volunteers.landing"))
