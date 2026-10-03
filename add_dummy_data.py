# Dummy data for dev/demo. Run: python add_dummy_data.py

from datetime import time

from app import create_app, db
from app.models import (
    CollectionSlot,
    DeliveryBooking,
    DeliveryRequest,
    Donation,
    FoodBank,
    Recipient,
    Volunteer,
    VolunteerAvailability,
)

SAMPLE_FOOD_BANKS = [
    dict(
        name="Edinburgh Food Project",
        city="Edinburgh",
        address="14 Westfield Avenue",
        postcode="EH11 2QH",
        contact_email="info@edinburghfoodproject.example",
        latitude=55.9412,
        longitude=-3.2375,
        need_level="high",
        needed_items="Tinned meat, UHT milk, pasta",
        need_protein_pct=65, need_carbs_pct=40, need_fats_pct=30,
        need_fiber_pct=55, need_fruit_veg_pct=70, need_tinned_goods_pct=50,
        collection_slots=[
            (0, time(10, 0), time(13, 0)),
            (3, time(14, 0), time(17, 0)),
        ],
    ),
    dict(
        name="Glasgow South West Foodbank",
        city="Glasgow",
        address="2 Paisley Road West",
        postcode="G51 1AA",
        contact_email="info@glasgowswfoodbank.example",
        latitude=55.8544,
        longitude=-4.2886,
        need_level="urgent",
        needed_items="Nappies, baby formula, tinned vegetables",
        need_protein_pct=80, need_carbs_pct=60, need_fats_pct=45,
        need_fiber_pct=75, need_fruit_veg_pct=85, need_tinned_goods_pct=65,
        collection_slots=[
            (1, time(9, 30), time(12, 30)),
            (4, time(9, 30), time(12, 30)),
        ],
    ),
    dict(
        name="Dundee Foodbank",
        city="Dundee",
        address="6 Brook Street",
        postcode="DD3 7EQ",
        contact_email="info@dundeefoodbank.example",
        latitude=56.4680,
        longitude=-2.9707,
        need_level="medium",
        needed_items="Rice, cereal, long-life juice",
        need_protein_pct=35, need_carbs_pct=50, need_fats_pct=20,
        need_fiber_pct=40, need_fruit_veg_pct=55, need_tinned_goods_pct=45,
        collection_slots=[
            (2, time(11, 0), time(14, 0)),
        ],
    ),
]

SAMPLE_VOLUNTEERS = [
    dict(
        name="Fiona Campbell",
        email="fiona.campbell@example.com",
        city="Edinburgh",
        phone="07700 900111",
        has_vehicle=True,
        availability=[(0, time(9, 0), time(12, 0)), (2, time(9, 0), time(12, 0))],
    ),
]

SAMPLE_RECIPIENTS = [
    dict(
        name="Morag Fraser",
        email="morag.fraser@example.com",
        city="Edinburgh",
        postcode="EH11 1QW",
        household_size=1,
        preferred_food_bank="Edinburgh Food Project",
    ),
]

SAMPLE_DONATIONS = [
    dict(donor_name="Alan Reid", donor_email="alan.reid@example.com",
         items="Pasta, Tinned Fish, Pasta Sauce",
         food_bank="Edinburgh Food Project", notes="Happy to help!"),
    dict(donor_name="Katie Munro", donor_email="katie.munro@example.com",
         items="Nappies, Baby Formula",
         food_bank="Glasgow South West Foodbank", notes=""),
    dict(donor_name="Gordon Webster", donor_email="gordon.webster@example.com",
         items="Rice, Cereal",
         food_bank="Dundee Foodbank", notes=""),
]

# one open, one claimed, one completed — covers every pickup status
SAMPLE_PICKUP_REQUESTS = [
    dict(pickup_location="4 Marchmont Road, Edinburgh", food_bank="Edinburgh Food Project",
         status="open", notes="2 boxes of tinned goods, ring doorbell"),
    dict(pickup_location="21 Nethergate, Dundee", food_bank="Dundee Foodbank",
         status="claimed", notes="Large box, may need help carrying", volunteer_email="fiona.campbell@example.com"),
    dict(pickup_location="88 Byres Road, Glasgow", food_bank="Glasgow South West Foodbank",
         status="completed", notes="", volunteer_email="fiona.campbell@example.com"),
]

# one requested, one booked, one completed — covers every booking status
SAMPLE_DELIVERY_BOOKINGS = [
    dict(recipient_email="morag.fraser@example.com", food_bank="Edinburgh Food Project",
         day_of_week=1, period="evening", status="requested",
         notes="Please call on arrival"),
    dict(recipient_email="morag.fraser@example.com", food_bank="Edinburgh Food Project",
         day_of_week=0, period="morning", status="booked",
         volunteer_email="fiona.campbell@example.com"),
    dict(recipient_email="morag.fraser@example.com", food_bank="Edinburgh Food Project",
         day_of_week=4, period="evening", status="completed",
         volunteer_email="fiona.campbell@example.com"),
]

TIME_PERIODS = {
    "morning": (time(9, 0), time(12, 0)),
    "afternoon": (time(12, 0), time(17, 0)),
    "evening": (time(17, 0), time(20, 0)),
}


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        food_banks_by_name = {}
        for data in SAMPLE_FOOD_BANKS:
            slots = data.pop("collection_slots")
            existing = FoodBank.query.filter_by(name=data["name"]).first()

            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
                food_bank = existing
                CollectionSlot.query.filter_by(food_bank_id=food_bank.id).delete()
            else:
                food_bank = FoodBank(**data)
                db.session.add(food_bank)
                db.session.flush()

            for day_of_week, start_time, end_time in slots:
                db.session.add(
                    CollectionSlot(
                        food_bank_id=food_bank.id,
                        day_of_week=day_of_week,
                        start_time=start_time,
                        end_time=end_time,
                    )
                )
            food_banks_by_name[food_bank.name] = food_bank

        volunteers_by_email = {}
        for data in SAMPLE_VOLUNTEERS:
            availability = data.pop("availability")
            existing = Volunteer.query.filter_by(email=data["email"]).first()

            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
                volunteer = existing
                VolunteerAvailability.query.filter_by(volunteer_id=volunteer.id).delete()
            else:
                volunteer = Volunteer(**data)
                db.session.add(volunteer)
                db.session.flush()

            for day_of_week, start_time, end_time in availability:
                db.session.add(
                    VolunteerAvailability(
                        volunteer_id=volunteer.id,
                        day_of_week=day_of_week,
                        start_time=start_time,
                        end_time=end_time,
                    )
                )
            volunteers_by_email[volunteer.email] = volunteer

        recipients_by_email = {}
        for data in SAMPLE_RECIPIENTS:
            data = dict(data)
            preferred_name = data.pop("preferred_food_bank")
            preferred_food_bank_id = (
                food_banks_by_name[preferred_name].id if preferred_name else None
            )

            existing = Recipient.query.filter_by(email=data["email"]).first()
            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
                existing.preferred_food_bank_id = preferred_food_bank_id
                recipient = existing
            else:
                recipient = Recipient(**data, preferred_food_bank_id=preferred_food_bank_id)
                db.session.add(recipient)
                db.session.flush()

            recipients_by_email[recipient.email] = recipient

        for data in SAMPLE_DONATIONS:
            food_bank_name = data.pop("food_bank")
            exists = Donation.query.filter_by(
                donor_email=data["donor_email"], items=data["items"]
            ).first()
            if not exists:
                db.session.add(
                    Donation(food_bank_id=food_banks_by_name[food_bank_name].id, **data)
                )

        for data in SAMPLE_PICKUP_REQUESTS:
            data = dict(data)
            food_bank_name = data.pop("food_bank")
            volunteer_email = data.pop("volunteer_email", None)
            exists = DeliveryRequest.query.filter_by(
                pickup_location=data["pickup_location"]
            ).first()
            if not exists:
                db.session.add(
                    DeliveryRequest(
                        food_bank_id=food_banks_by_name[food_bank_name].id,
                        volunteer_id=(
                            volunteers_by_email[volunteer_email].id
                            if volunteer_email
                            else None
                        ),
                        **data,
                    )
                )

        for data in SAMPLE_DELIVERY_BOOKINGS:
            data = dict(data)
            recipient_email = data.pop("recipient_email")
            food_bank_name = data.pop("food_bank")
            volunteer_email = data.pop("volunteer_email", None)
            period = data.pop("period")
            start_time, end_time = TIME_PERIODS[period]

            recipient = recipients_by_email[recipient_email]
            exists = DeliveryBooking.query.filter_by(
                recipient_id=recipient.id, day_of_week=data["day_of_week"]
            ).first()
            if not exists:
                db.session.add(
                    DeliveryBooking(
                        recipient_id=recipient.id,
                        food_bank_id=food_banks_by_name[food_bank_name].id,
                        volunteer_id=(
                            volunteers_by_email[volunteer_email].id
                            if volunteer_email
                            else None
                        ),
                        start_time=start_time,
                        end_time=end_time,
                        **data,
                    )
                )

        db.session.commit()
        print(
            f"Seeded {len(SAMPLE_FOOD_BANKS)} food banks, "
            f"{len(SAMPLE_VOLUNTEERS)} volunteers, "
            f"{len(SAMPLE_RECIPIENTS)} recipients, "
            f"{len(SAMPLE_DONATIONS)} donations, "
            f"{len(SAMPLE_PICKUP_REQUESTS)} pickup requests, "
            f"{len(SAMPLE_DELIVERY_BOOKINGS)} delivery bookings."
        )


if __name__ == "__main__":
    seed()
