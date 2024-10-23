from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings

from rest_framework import viewsets
from rest_framework import status
from celery.result import AsyncResult
import requests
import json

from .models import Meal, Review
from .tasks import process_review


def search(request):
    meal_search_api = f"{settings.EXTERNAL_SERVICE_API}/1/search.php?s="
    
    keyword = request.GET.get('keyword')
    if not keyword:
        return HttpResponse("No keyword provided", status = status.HTTP_400_BAD_REQUEST)
    
    search_url =  f"{meal_search_api}{keyword}"
    try:
        response = requests.get(search_url)
        if response.content is None:
            return HttpResponse("Nothing found", status = status.HTTP_200_OK)
        else:
            # Keep only necessary info for response
            data = json.loads(response.content)
            meals = data.get('meals', [])
            response_content = [{
                    meal.get('strMeal'),
                    meal.get('idMeal')
                }
                for meal in meals]
            return HttpResponse(
                response_content,
                content_type='application/json',
                status = 200
                )
    except requests.RequestException as e:
        return HttpResponse (str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ReviewCreateViewSet(viewsets.ModelViewSet):
    """
    def _get_by_meal_id(self, value):
        meal_search_api = f"{settings.EXTERNAL_SERVICE_API}/1/lookup.php?i="
        url = f"{meal_search_api}{value}"
        response = requests.get(url)
        content = json.loads(response.content)
        # the response of the mealdb requires this approach... ¯\_(ツ)_/¯
        if content.get('meals') == 'Invalid ID':
            return None
        response_content = {
            'name': content['meals'][0]['idMeal'],
            'category': content['meals'][0]['strCategory'],
            'thumb': content['meals'][0]['strMealThumb']
        }
        return response_content
    """
    
    def post(self, request):
        ### RICORDATI DI FAR PARTIRE IL WORKER
        review_data = {
            'meal_id' : request.data['meal_id'],
            'text' : request.data['text'],
            'score' : request.data['score']
        }

        meal_search_api = f"http://www.themealdb.com/api/json/v1/1/lookup.php?i={review_data['meal_id']}"
    
        response = requests.get(meal_search_api)
        content = json.loads(response.content)

        # Handle case where the meal isn't found
        if content.get('meals') is None:
            return HttpResponse(
                f"Nothing found within provided id",
                status=status.HTTP_204_NO_CONTENT
            )

        # Trigger the asynchronous task using Celery
        task = process_review.delay(content, review_data)
        
        return HttpResponse(
            f"Review submitted successfully. It is being processed asynchronously. \n{task.id}",
            status=status.HTTP_202_ACCEPTED
            )
    
    
class ReviewStatusViewSet(viewsets.ViewSet):
    
    def get(self, request, pk=None):
        # Fetch the review by ID or 404
        review = get_object_or_404(Review, id=pk)
        response_data = {
            "review_id": review.id,
            "meal": {
                "name": review.meal.name,
                "category": review.meal.category,
                "thumbnail": review.meal.thumbnail
            },
            "text": review.text,
            "score": review.score,
        }
        
        return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        
        review_data = request.data
        new_text = review_data.get('text')
        new_score = review_data.get('score')
        #qua serve la validazione dei dati della request
        
        #if review.user != request.user:
        #    return HttpResponse("You do not have permission to edit this review.",
        #                        status=status.HTTP_403_FORBIDDEN)

        try:
            review = Review.objects.get(id=pk)
        except:
            return HttpResponse("Review does not exists", status=status.HTTP_204_NO_CONTENT)
        
        try:
            review.text = new_text
            review.score = new_score
            review.save()
            
        except:
            return HttpResponse("Something went wrong", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        
        response_data = {
            "review_id": review.id,
            "meal": {
                "name": review.meal.name,
                "category": review.meal.category,
                "thumbnail": review.meal.thumbnail
            },
            "text": review.text,
            "score": review.score,
        }            
        return HttpResponse(json.dumps(response_data), status=status.HTTP_200_OK)
        
    def retrieve(self, request, task_id=None):
        
        task_result = AsyncResult(task_id)
        
        if task_result.status == "PENDING":
            return HttpResponse("Review is still being processed.", status=status.HTTP_202_ACCEPTED)
        elif task_result.status == "FAILURE":
            return HttpResponse("Your task failed for some reason.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Fetch the review by from task ID
        review_id = task_result.result
        
        try:
            review = Review.objects.get(id=review_id)
            response_content = json.dumps(
                {
                    "review_id": review.id,
                    "meal": {
                        "name": review.meal.name,
                        "category": review.meal.category,
                        "thumbnail": review.meal.thumbnail
                    },
                    "text": review.text,
                    "score": review.score,
                }
            )
            return HttpResponse(response_content, status=status.HTTP_200_OK)
        
        except Review.DoesNotExist:
            return HttpResponse("Review not found", status=status.HTTP_404_NOT_FOUND)
        
    def delete(self, request, pk=None):
        
        try:
            review = Review.objects.get(id=pk)    
            
            #if review.user != request.user:
            #return HttpResponse("You do not have permission to delete this review.",
            #                    status=status.HTTP_403_FORBIDDEN)      
            
            review.delete()
            return HttpResponse(f"{pk} DELETED", status = status.HTTP_204_NO_CONTENT)
            
        except Review.DoesNotExist:
            return HttpResponse("Review not found.", status=status.HTTP_204_NO_CONTENT)
        except:
            return HttpResponse("Something went wrong.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

        