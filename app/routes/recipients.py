from collections import defaultdict

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app import db
from app.constants import DAYS_OF_WEEK, TIME_PERIODS, format_time_range
from app.models import DeliveryBooking, FoodBank, Recipient, VolunteerAvailability

recipients_bp = Blueprint("recipients", __name__, url_prefix="/receive")


@recipients_bp.route("/", methods=["GET", "POST"])
def receive():
    food_banks = FoodBank.query.order_by(FoodBank.name).all()

    if request.method == "POST":
        preferred_food_bank_id = request.form.get("preferred_food_bank_id") or None

        recipient = Recipient(
            name=request.form["name"],
            email=request.form["email"],
            phone=request.form.get("phone"),
            address=request.form.get("address"),
            city=request.form["city"],
            postcode=request.form.get("postcode"),
            household_size=int(request.form.get("household_size") or 1),
            dietary_needs=request.form.get("dietary_needs"),
            notes=request.form.get("notes"),
            preferred_food_bank_id=(
                int(preferred_food_bank_id) if preferred_food_bank_id else None
            ),
        )
        db.session.add(recipient)
        db.session.commit()
        flash(
            "Thanks for signing up — here's your collection and delivery schedule.",
            "success",
        )
        return redirect(url_for("recipients.schedule", recipient_id=recipient.id))

    dev_recipients = (
        Recipient.query.order_by(Recipient.id.desc()).limit(10).all()
        if current_app.debug
        else []
    )
    return render_template(
        "receive.html", food_banks=food_banks, dev_recipients=dev_recipients
    )


@recipients_bp.route("/schedule/<int:recipient_id>")
def schedule(recipient_id):
    recipient = Recipient.query.get_or_404(recipient_id)

    if recipient.preferred_food_bank_id:
        food_banks = [recipient.preferred_food_bank]
    else:
        food_banks = FoodBank.query.order_by(FoodBank.name).all()

    collection_schedule = []
    for fb in food_banks:
        slots = [
            {
                "day": DAYS_OF_WEEK[slot.day_of_week],
                "time_range": format_time_range(slot.start_time, slot.end_time),
                "notes": slot.notes,
            }
            for slot in fb.collection_slots
        ]
        collection_schedule.append({"food_bank": fb, "slots": slots})

    # Aggregate volunteer availability by day/time window — counts only,
    # never individual volunteer identities, to protect volunteer privacy.
    availability_counts = defaultdict(int)
    for avail in VolunteerAvailability.query.all():
        key = (avail.day_of_week, avail.start_time, avail.end_time)
        availability_counts[key] += 1

    delivery_availability = sorted(
        (
            {
                "day": DAYS_OF_WEEK[day],
                "time_range": format_time_range(start, end),
                "volunteer_count": count,
            }
            for (day, start, end), count in availability_counts.items()
        ),
        key=lambda row: (DAYS_OF_WEEK.index(row["day"]), row["time_range"]),
    )

    my_bookings = [
        {
            "day": DAYS_OF_WEEK[b.day_of_week],
            "time_range": format_time_range(b.start_time, b.end_time),
            "food_bank_name": b.food_bank.name,
            "status": b.status,
            "volunteer_first_name": b.volunteer.name.split(" ")[0] if b.volunteer else None,
            "notes": b.notes,
        }
        for b in sorted(
            recipient.delivery_bookings, key=lambda b: b.created_at, reverse=True
        )
    ]

    return render_template(
        "schedule.html",
        recipient=recipient,
        collection_schedule=collection_schedule,
        delivery_availability=delivery_availability,
        my_bookings=my_bookings,
        request_food_banks=food_banks,
        days_of_week=DAYS_OF_WEEK,
    )


@recipients_bp.route("/schedule/<int:recipient_id>/request-delivery", methods=["POST"])
def request_delivery(recipient_id):
    recipient = Recipient.query.get_or_404(recipient_id)

    food_bank_id = request.form.get("food_bank_id") or recipient.preferred_food_bank_id
    if not food_bank_id:
        flash("Please choose a food bank for your delivery.", "error")
        return redirect(url_for("recipients.schedule", recipient_id=recipient.id))

    period = request.form.get("period", "morning")
    start_time, end_time = TIME_PERIODS.get(period, TIME_PERIODS["morning"])

    booking = DeliveryBooking(
        recipient_id=recipient.id,
        food_bank_id=int(food_bank_id),
        day_of_week=int(request.form["day_of_week"]),
        start_time=start_time,
        end_time=end_time,
        notes=request.form.get("notes"),
    )
    db.session.add(booking)
    db.session.commit()
    flash("Delivery requested — a volunteer will book it soon.", "success")
    return redirect(url_for("recipients.schedule", recipient_id=recipient.id))
