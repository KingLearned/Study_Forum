from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer
from django.http import JsonResponse, Http404

import requests
import bs4
import re


@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id',
    ]
    return JsonResponse(routes, safe=False)


@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getRoom(request, pk):
    try:
        room = Room.objects.get(id=pk)
        serializer = RoomSerializer(room)
        return Response(serializer.data)
    except Room.DoesNotExist:
        raise Http404



category = [{'Politics':'politics'}, {'Business':'business'}, {'Sports':'sports'}, {'National':'metro-plus'}, {'Education':'education'}]

def AutoPost(url_link, post_categoty):
    url = f"https://punchng.com/topics/{url_link}"

    try:
        getWeb = requests.get(url)
        getWeb.raise_for_status()

        soup = bs4.BeautifulSoup(getWeb.content.decode(getWeb.encoding), "lxml")

        if soup.select('.just-in-timeline'):
            get_news_link = [link.get('href') for link in soup.select('.just-in-timeline h3 a')]

            newsData = []

            for index, news_link in enumerate(get_news_link):
                if index == 1:

                    each_news_link = bs4.BeautifulSoup(requests.get(news_link).content.decode(requests.get(news_link).encoding), "lxml")

                    news_heading = re.sub(r'[^a-zA-Z\'!<>/ ]', '', each_news_link.select('.single-article .post-title')[0].text)
                    news_image = each_news_link.select('.post-image-wrapper img')[0].get('src')

                    if each_news_link.select('.post-content'):
                        paragraphs = [re.sub(r'[^a-zA-Z\'!<>/. ]', '', f'{p}<p><br></p>') for p in each_news_link.select('.post-content p')]
                        newsData.append({'Title': news_heading, 'Image': news_image, 'Content': paragraphs})

            url = "http://localhost:1000/server/posts/autopost"
            data = { 'payLoad': newsData, 'category': post_categoty }
            response = requests.post(url, json=data)

            if response:
                print(response.json())
            else:
                print(f"POST request failed {response.status_code}")

        else:
            print({"error": "No news elements found on the page."}, status=404)

    except requests.exceptions.RequestException as e:
        print({"error": f"Error fetching the URL: {e}"}, status=500)
    except Exception as e:
        print({"error": f"An error occurred: {e}"}, status=500)


# const Proxy = 'https://learnedsblogapi.vercel.app/server'

def Run_Post(category_list, key_to_find):
    for item in category_list:
        if key_to_find in item:
            return AutoPost(item[key_to_find], key_to_find)
    return print(None)

# Politics
# Business
# Sports
# National
# Education
Run_Post(category, 'Politics')
