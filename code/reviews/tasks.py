import requests
import json
from celery import shared_task
from .models import Meal, Review


@shared_task
def process_review(content, review_data):
    ### Backgroud task

    # Extract meal information
    meal_data = content['meals'][0]
    meal_name = meal_data['strMeal']
    meal_category = meal_data['strCategory']
    meal_thumb = meal_data['strMealThumb']

    meal, created = Meal.objects.get_or_create(
        name=meal_name,
        category=meal_category,
        thumbnail=meal_thumb
    )
    print(created)
    # Save the review in the database
    review = Review.objects.create(
        meal = meal,
        text = review_data['text'],
        score = review_data['score'],
        #user = review_data['user']
    )
    print("TASK COMPLETED\n")
    return review.id