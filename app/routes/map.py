from flask import Blueprint, jsonify, render_template

from app.models import FoodBank

map_bp = Blueprint("map", __name__)


@map_bp.route("/map")
def view_map():
    return render_template("map.html")


@map_bp.route("/api/food-banks")
def api_food_banks():
    food_banks = FoodBank.query.filter(
        FoodBank.latitude.isnot(None), FoodBank.longitude.isnot(None)
    ).all()
    return jsonify([fb.to_dict() for fb in food_banks])
