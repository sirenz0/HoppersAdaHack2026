from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.constants import DONATION_ITEMS, NEED_CATEGORIES
from app.models import Donation, FoodBank

donations_bp = Blueprint("donations", __name__, url_prefix="/donate")


@donations_bp.route("/", methods=["GET", "POST"])
def donate():
    food_banks = FoodBank.query.order_by(FoodBank.name).all()

    if request.method == "POST":
        items = request.form.getlist("items")
        if not items:
            flash("Please select at least one item to donate.", "error")
            return redirect(url_for("donations.donate", food_bank_id=request.form.get("food_bank_id")))

        donation = Donation(
            donor_name=request.form["donor_name"],
            donor_email=request.form["donor_email"],
            food_bank_id=int(request.form["food_bank_id"]),
            items=", ".join(items),
            notes=request.form.get("notes"),
        )
        db.session.add(donation)
        db.session.commit()
        flash("Thank you for your donation!", "success")
        return redirect(url_for("donations.donate", food_bank_id=donation.food_bank_id))

    selected_id = request.args.get("food_bank_id", type=int)
    selected_food_bank = None
    if food_banks:
        selected_food_bank = next(
            (fb for fb in food_banks if fb.id == selected_id), food_banks[0]
        )

    need_bars = []
    if selected_food_bank:
        need_bars = [
            {"label": label, "pct": getattr(selected_food_bank, attr)}
            for label, attr in NEED_CATEGORIES
        ]

    return render_template(
        "donate.html",
        food_banks=food_banks,
        selected_food_bank=selected_food_bank,
        need_bars=need_bars,
        donation_items=DONATION_ITEMS,
    )
