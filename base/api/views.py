from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer
from base.api import serializers
from django.http import JsonResponse

import requests
import bs4
import re


@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id',
        'GET /api/getNews'
    ]
    return JsonResponse(routes, safe=False)


@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    serializer = RoomSerializer(room, many=False)
    return Response(serializer.data)


@api_view(['GET'])
def getNews(request):
    url = "https://punchng.com/topics/politics"

    try:
        getWeb = requests.get(url)
        getWeb.raise_for_status()

        soup = bs4.BeautifulSoup(getWeb.content.decode(getWeb.encoding), "lxml")

        if soup.select('.just-in-timeline'):
            get_news_link = [link.get('href') for link in soup.select('.just-in-timeline h3 a')]

            newsData = []

            for index, news_link  in enumerate(get_news_link):

                each_news_link = bs4.BeautifulSoup(requests.get(news_link).content.decode(requests.get(news_link).encoding), "lxml")

                news_heading = re.sub(r'[^a-zA-Z\'!<>/ ]', '', each_news_link.select('.single-article .post-title')[0].text)
                news_image = each_news_link.select('.post-image-wrapper img')[0].get('src')

                if each_news_link.select('.post-content'):
                    paragraphs = [re.sub(r'[^a-zA-Z\'!<>/ ]', '', f'{p}<p><br></p>') for p in each_news_link.select('.post-content p')]
                    newsData.append({'Title':news_heading,'Image':news_image,'Content':paragraphs})

            return Response(newsData)
        else:
                print("No element found on the page.")
    except requests.exceptions.RequestException as e:
        print("Error fetching the URL:", e)
    except Exception as e:
        print("An error occurred:", e)
