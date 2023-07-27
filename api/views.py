import datetime
import math

from django.db.models import Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from random import randrange
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet

from frontend.models import Products, Reviews, Category, Profile, Order, Delivery, Tags
from api.serializers import ProductSerializer


User = get_user_model()


def banners(request):
    data = []
    popular_products = Products.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:1]

    i = 0
    for p in popular_products:
        data.append({
            'id': p.id,
            'category': p.category.id,
            'price': p.price,
            'count': p.count,
            'title': p.title,
            'date': p.date.strftime('%Y-%m-%d %H:%M'),
            'description': p.description,
            'freeDelivery': p.freeDelivery,
        })
        images_list = []
        # for img in p.image:
        #     images_list.append({'src': img.image.url})
        # data[i]['images'] = images_list
        data[i]['images'] = p.image
        tags_list = []
        for tag in p.tags.all():
            tags_list.append({'id': tag.id, 'name': tag.name})
        data[i]['tags'] = tags_list
        i += 1
    return JsonResponse(data, safe=False)


def categories(request):
    cats = Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related('children')

    data = []
    i = 0
    for cat in cats:
        data.append({
            'id': cat.id,
            'title': cat.name,
            'image': {
                'src': cat.icon.url
            }
        })
        data[i]['subcategories'] = []
        if cat.children.all():
            for child in cat.children.all():
                data[i]['subcategories'].append({
                    'id': child.id,
                    'title': child.name,
                    'image': {
                        'src': child.icon.url
                    }
                })
        i += 1
    return JsonResponse(data, safe=False)



class CatalogViewSet(ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer


def catalog(request):
    prof = Profile.objects.all()
    if request.method == 'GET':
        count_page = 9
        name = request.GET.get('filter[name]')
        minPrice = request.GET.get('filter[minPrice]')
        maxPrice = request.GET.get('filter[maxPrice]')
        freeDelivery = request.GET.get('filter[freeDelivery]')
        available = request.GET.get('filter[available]')
        currentPage = request.GET.get('currentPage')
        tags_fil = request.GET.get('tags[]')

        sort = request.GET.get('sort')
        sortType = request.GET.get('sortType')
        cur_product = int(currentPage) * int(count_page)
        start_product = cur_product - count_page
        if sortType == 'inc':
            sortt = '-' + sort
        else:
            sortt = sort

        limit = int(request.GET.get('limit'))
        if freeDelivery == 'true':
            freeDelivery = True
        else:
            freeDelivery = False
        if available == 'true':
            available = True
        else:
            available = False
        if request.session['id_cat']:
            if name != '':
                pr = Products.objects.filter(category=request.session['id_cat'], title__iregex=name, price__gte=minPrice,
                                             price__lte=maxPrice, freeDelivery=freeDelivery, available=available).order_by(
                    sortt)

            else:
                pr = Products.objects.filter(category=request.session['id_cat'], price__gte=minPrice, price__lte=maxPrice,
                                             freeDelivery=True, available=available).order_by(sortt)
            count = pr.count()
            pr = pr[start_product:cur_product]
        else:

            if name != '':
                pr = Products.objects.filter(title__iregex=name, price__gte=minPrice, price__lte=maxPrice,
                                             freeDelivery=freeDelivery, available=available).order_by(sortt)
            else:
                pr = Products.objects.filter(price__gte=minPrice, price__lte=maxPrice, available=available).order_by(sortt)
            count = pr.count()
            pr = pr[start_product:cur_product]

        count_page = math.ceil(count / count_page)

        data = {
            "items": [

            ]
        }
        i = 0
        for p in pr:
            data['items'].append({
                'id': p.id,
                'category': p.category.id,
                'price': p.price,
                'count': p.count,
                'title': p.title,
                'date': p.date.strftime('%Y-%m-%d %H:%M'),
                'description': p.description,
                'freeDelivery': p.freeDelivery,
            })
            images_list = []
            for img in Products.images:
                images_list.append({'src': img.image.url})
            data['items'][i]['images'] = [p.images]
            tags_list = []
            for tag in p.tags.all():
                tags_list.append({'id': tag.id, 'name': tag.name})
            data['items'][i]['tags'] = tags_list
            data['lastPage'] = count_page
            data['currentPage'] = currentPage
            i += 1

        return JsonResponse(data, safe=False)


def productsPopular(request):
    data = []
    pr = Products.objects.order_by('-rating')[:3]
    prof = Profile.objects.all()
    # popular_products = Products.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:8]

    i = 0
    for p in pr:
        data.append({
            'id': p.id,
            'category': p.category.id,
            'price': p.price,
            'count': p.count,
            'title': p.title,
            'date': p.date.strftime('%Y-%m-%d %H:%M'),
            'description': p.description,
            'freeDelivery': p.freeDelivery,
        })
        images_list = []
        for img in p.images.id:
            images_list.append({'src': img.image.url})
        data[i]['images'] = images_list
        tags_list = []
        for tag in p.tags.all():
            tags_list.append({'id': tag.id, 'name': tag.name})
        data[i]['tags'] = tags_list
        i += 1

    return JsonResponse(data, safe=False)


def productsLimited(request):
    data = []
    popular_products = Products.objects.filter(available=True, count__lt=10).annotate(
        avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:3]

    i = 0
    for p in popular_products:
        data.append({
            'id': p.id,
            'category': p.category.id,
            'price': p.price,
            'count': p.count,
            'title': p.title,
            'date': p.date.strftime('%Y-%m-%d %H:%M'),
            'description': p.description,
            'freeDelivery': p.freeDelivery,
        })
        images_list = []
        for img in p.image.all():
            images_list.append({'src': img.image.url})
        data[i]['images'] = images_list
        tags_list = []
        for tag in p.tags.all():
            tags_list.append({'id': tag.id, 'name': tag.name})
        data[i]['tags'] = tags_list
        i += 1
    return JsonResponse(data, safe=False)


def sales(request):
    data = []
    images_list = []
    midl_list = []
    pprod = Products.objects.all()
    # popular_products = Products.objects.filter(available=True, count__lt=10).annotate(
    #     avg_rating=Avg('reviews__rating')).order_by('-avg_rating')[:3]

    data = {
        "items": [

        ]
    }
    i = 0
    for p in pprod:
        data['items'].append({
            'id': p.id,
            "price": p.price,
            "salePrice": p.price,
            "dateFrom": p.date.strftime('%Y-%m-%d %H:%M'),
            "dateTo": p.date.strftime('%Y-%m-%d %H:%M'),
            "title": p.title,
        })
        data['currentPage'] = i
        data['lastPage'] = 3
        # items = [{
        #     'id': p.get(id=i),
        #     "price": p.price,
        #     "salePrice": p.price,
        #     "dateFrom": p.date.strftime('%Y-%m-%d %H:%M'),
        #     "dateTo": p.date.strftime('%Y-%m-%d %H:%M'),
        #     "title": p.title,
        #     'currentPage': randrange(1, 4),
        #     'lastPage': 3}]
        #
        # data['items'][i]['images'] = images_list
        for img in p.images:
            images_list.append({'src': img.image.url})
        data[i]['images'] = images_list
        # data[i]['images'] = p.image
        images_list = []
        i += 1
    return JsonResponse(data, safe=False)


# def sales(request):
#     data = {
#         'items': [
#             {
#                 "id": 123,
#                 "price": 500.67,
#                 "salePrice": 200.67,
#                 "dateFrom": "05-08",
#                 "dateTo": "05-20",
#                 "title": "video card",
#                 "images": [
#                     {
#                         "src": "https://proprikol.ru/wp-content/uploads/2020/12/kartinki-ryabchiki-14.jpg",
#                         "alt": "hello alt",
#                     }
#                 ],
#             }
#         ],
#         'currentPage': randrange(1, 4),
#         'lastPage': 3,
#     }
#     return JsonResponse(data)


def basket(request):
    if (request.method == "GET"):

        print('[GET] /api/basket/')
        data = []
        if 'cart' in request.session:
            index = 0
            for i in request.session['cart']:
                pr = Products.objects.filter(id=i).first()
                data.append(
                    {
                        "id": pr.id,
                        "category": pr.category.id,
                        "price": pr.price,
                        "count": request.session['cart'][i]['count'],
                        "date": pr.date.strftime('%Y-%m-%d %H:%M'),
                        "title": pr.title,
                        "description": pr.description,
                        "freeDelivery": pr.freeDelivery,
                    }
                )
                images_list = []
                for img in pr.image.all():
                    images_list.append({'src': img.image.url})
                data[index]['images'] = images_list
                tags_list = []
                for tag in pr.tags.all():
                    tags_list.append({'id': tag.id, 'name': tag.name})
                data[index]['tags'] = tags_list
                data[index]['reviews'] = Reviews.objects.filter(product=pr.id).count()
                data[index]['rating'] = pr.rating
                index = index + 1
        return JsonResponse(data, safe=False)

    elif (request.method == "POST"):
        body = json.loads(request.body)
        id = body['id']
        count = body['count']
        print('[POST] /api/basket/   |   id: {id}, count: {count}'.format(id=id, count=count))
        cart = request.session.get('cart', {})
        if ('cart' in request.session) and (str(id) in request.session['cart']):
            print('yes')
            cart[str(id)] = {'count': cart[str(id)]['count'] + 1}
        else:
            print('no')
            cart[str(id)] = {'count': count}

        request.session['cart'] = cart

        data = []
        if 'cart' in request.session:
            index = 0
            for i in request.session['cart']:
                pr = Products.objects.filter(id=i).first()
                data.append(
                    {
                        "id": pr.id,
                        "category": pr.category.id,
                        "price": pr.price,
                        "count": request.session['cart'][i]['count'],
                        "date": pr.date.strftime('%Y-%m-%d %H:%M'),
                        "title": pr.title,
                        "description": pr.description,
                        "freeDelivery": pr.freeDelivery,
                    }
                )
                images_list = []
                for img in pr.image.all():
                    images_list.append({'src': img.image.url})
                data[index]['images'] = images_list

                index = index + 1

        return JsonResponse(data, safe=False)

    elif (request.method == "DELETE"):
        body = json.loads(request.body)
        id = body['id']
        print(body)

        cart = request.session.get('cart', {})
        if cart[str(id)]['count'] > 1:
            print('yes')
            cart[str(id)] = {'count': cart[str(id)]['count'] - 1}
        else:
            del cart[str(id)]
        request.session['cart'] = cart
        print('[DELETE] /api/basket/')
        data = []
        if 'cart' in request.session:
            index = 0
            for i in request.session['cart']:
                pr = Products.objects.filter(id=i).first()
                data.append(
                    {
                        "id": pr.id,
                        "category": pr.category.id,
                        "price": pr.price,
                        "count": request.session['cart'][i]['count'],
                        "date": pr.date.strftime('%Y-%m-%d %H:%M'),
                        "title": pr.title,
                        "description": pr.description,
                        "freeDelivery": pr.freeDelivery,
                    }
                )
                images_list = []
                for img in pr.image.all():
                    images_list.append({'src': img.image.url})
                data[index]['images'] = images_list
                tags_list = []
                for tag in pr.tags.all():
                    tags_list.append({'id': tag.id, 'name': tag.name})
                data[index]['tags'] = tags_list
                data[index]['reviews'] = Reviews.objects.filter(product=pr.id).count()
                data[index]['rating'] = pr.rating
                index = index + 1
        return JsonResponse(data, safe=False)


def signIn(request):
    if request.method == "POST":
        body = json.loads(request.body)
        username = body['username']
        password = body['password']
        print(username)
        print(password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=500)


def signUp(request):
    body = json.loads(request.body)
    user = User.objects.create_user(body['name'], body['username'], body['password'])
    # user.save()
    return HttpResponse(status=200)


def signOut(request):
    logout(request)
    return HttpResponse(status=200)


def product(request, id):
    pr = Products.objects.filter(id=id)
    data = {}
    for p in pr:
        data['id'] = p.id
        data['category'] = p.category.id
        data['price'] = p.price
        data['count'] = p.count
        data['title'] = p.title
        data['date'] = p.date
        data['description'] = p.description
        data['freeDelivery'] = p.freeDelivery
        images_list = []
        for img in p.image.all():
            images_list.append({'src': img.image.url})

        data['images'] = images_list
        tags_list = []
        for tag in p.tags.all():
            tags_list.append({'id': tag.id, 'name': tag.name})
        data['tags'] = tags_list

        revs = Reviews.objects.filter(product=p.id)
        rev_list = []
        for rev in revs:
            rev_list.append({
                'author': rev.author,
                'email': rev.email,
                'text': rev.name,
                'rate': rev.rating,
                'date': rev.date.strftime('%Y-%m-%d %H:%M')
            })
        data['reviews'] = rev_list

    return JsonResponse(data)


def tags(request):
    tags = Tags.objects.all()[:6]
    data = []
    for tag in tags:
        data.append({
            'id': tag.id,
            'name': tag.name
        })
    return JsonResponse(data, safe=False)


def productReviews(request, id):
    body = json.loads(request.body)

    rev = Reviews()
    rev.author = body['author']
    rev.email = body['email']
    rev.name = body['text']
    rev.rating = body['rate']
    rev.product = Products.objects.get(id=id)
    rev.save()
    data = [

    ]
    revs = Reviews.objects.filter(product=Products.objects.get(id=id))
    for res in revs:
        print(res.author)
        data.append({
            "author": res.author,
            "email": res.email,
            "text": res.name,
            "rate": res.rating,
            "date": res.date.strftime('%Y-%m-%d %H:%M')
        })

    print(data)
    return JsonResponse(data, safe=False)


def profile(request):
    if request.method == 'GET':
        if Profile.objects.filter(user_id=request.user).exists():
            user_cur = Profile.objects.filter(user_id=request.user).first()
            phone = user_cur.phone
            avatar = user_cur.avatar.url
        else:
            phone = 0
            avatar = "https://proprikol.ru/wp-content/uploads/2020/12/kartinki-ryabchiki-14.jpg"

        data = {
            'fullName': request.user.first_name,
            'email': request.user.email,
            'phone': phone,
            "avatar": {
                "src": avatar,
                "alt": "hello alt",
            }
        }
        return JsonResponse(data)
    elif (request.method == 'POST'):
        body = json.loads(request.body)
        user = get_object_or_404(User, id=request.user.id)
        if Profile.objects.filter(user_id=request.user).exists():
            user_cur = get_object_or_404(Profile, user_id=user)
            user_cur.phone = body["phone"]
            user_cur.save()
        else:
            profile = Profile()
            profile.phone = body["phone"]
            profile.user_id = user
            profile.save()
        user.first_name = body['fullName']
        user.email = body['email']
        user.save()
        data = {
            'fullName': body['fullName'],
            'email': body['email'],
            'phone': body["phone"],
            "avatar": {
                "src": body['avatar']['src'],
                "alt": "hello alt",
            }
        }
        return JsonResponse(data)

    return HttpResponse(status=500)


def profilePassword(request):
    body = json.loads(request.body)
    # print(request.user.username)
    print(body)
    if authenticate(username=request.user.username, password=body['currentPassword']):
        user = request.user
        user.set_password(body["newPassword"])
        user.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=500)


def orders(request):
    if (request.method == 'GET'):
        print('orders get')

        orders = Order.objects.filter(email=request.user.email).order_by('-created_at')

        data = [

        ]
        count = 0
        for order in orders:
            data.append({
                'id': order.id,
                'createdAt': order.created_at.strftime('%Y-%m-%d %H:%M'),
                "fullName": order.full_name,
                "email": order.email,
                "phone": order.phone,
                "deliveryType": order.delivery_type,
                "paymentType": order.payment_type,
                "totalCost": order.total_cost,
                "status": order.status,
                "city": order.status,
                "address": order.address
            })
            print(data)
            count += 1

        return JsonResponse(data, safe=False)

    elif (request.method == 'POST'):
        print('orders post')
        body = json.loads(request.body)
        ids = []
        summa = 0
        for i in body:
            ids.append(i['id'])
            summa += i['price']

        order = Order()
        if request.user.is_authenticated:
            order.full_name = request.user.first_name
            order.email = request.user.email
            profile = Profile.objects.filter(user_id=request.user).first()
            order.phone = profile.phone
            order.total_cost = summa
            """for j in ids:
				product1 = Products.objects.get(id=j)
				order.products.set(product1)
				order.save()"""
        else:
            order.total_cost = summa
        order.save()
        for j in ids:
            product1 = Products.objects.get(id=j)
            order.products.add(product1)
            order.save()

        data = {
            "orderId": order.id,
        }
        return JsonResponse(data)

    return HttpResponse(status=500)


def order(request, id):
    if (request.method == 'GET'):
        print('order get')
        order = Order.objects.filter(id=id).first()
        data = {
            'id': order.id,
            'createdAt': order.created_at.strftime('%Y-%m-%d %H:%M'),
            "fullName": order.full_name,
            "email": order.email,
            "phone": order.phone,
            "deliveryType": order.delivery_type,
            "paymentType": order.payment_type,
            "totalCost": order.total_cost,
            "status": order.status,
            "city": order.status,
            "address": order.address
        }
        data['products'] = []
        count = 0

        for i in order.products.all():
            if 'cart' in request.session:
                keys = request.session['cart'].keys()
                if str(i.id) in keys:
                    count_ses = request.session['cart'][str(i.id)]['count']
                else:
                    count_ses = 1
            else:
                count_ses = 1
            data['products'].append({
                "id": i.id,
                "category": i.category.id,
                "price": i.price,
                "count": count_ses,
                "date": i.date.strftime('%Y-%m-%d %H:%M'),
                "title": i.title,
                "description": i.description,
                "freeDelivery": i.freeDelivery,
            })
            images_list = []
            for img in i.image.all():
                images_list.append({'src': img.image.url})
            data['products'][count]['images'] = images_list
            tags_list = []
            for tag in i.tags.all():
                tags_list.append({'id': tag.id, 'name': tag.name})
            data['products'][count]['tags'] = tags_list
            data['products'][count]['reviews'] = Reviews.objects.filter(product=i.id).count()
            data['products'][count]['rating'] = i.rating

            count += 1
        return JsonResponse(data)

    elif (request.method == 'POST'):
        body = json.loads(request.body)
        deliv = Delivery.objects.filter(id=1).first()
        deliv1 = Delivery.objects.filter(id=2).first()
        deliv2 = Delivery.objects.filter(id=3).first()
        summa = float(body['totalCost'])
        if body['deliveryType'] == 'free' or body['deliveryType'] == 'express':
            summa += float(deliv.price)
        if summa < deliv1.price:
            summa += deliv2.price
        order = Order(id=int(body['orderId']))
        order.created_at = datetime.datetime.now()
        order.full_name = body['fullName']
        order.email = body['email']
        order.phone = body['phone']
        order.delivery_type = body['deliveryType']
        order.payment_type = body['paymentType']
        order.total_cost = summa
        order.city = body['city']
        order.address = body['address']
        order.save()
        request.session['paymentType'] = body['paymentType']
        if 'cart' in request.session:
            del request.session['cart']

        data = {"orderId": body['orderId'], 'paymentType': body['paymentType']}
        return JsonResponse(data)

    return HttpResponse(status=500)


def payment(request, id):
    print('qweqwewqeqwe', id)
    body = json.loads(request.body)
    number = body['number']
    if (number.isdigit() and len(number) <= 8 and int(number) % 2 == 0):
        cur_order = Order.objects.filter(id=id).first()
        order = Order(id=int(id))
        order.created_at = datetime.datetime.now()
        order.status = 'paid'
        order.full_name = cur_order.full_name
        order.email = cur_order.email
        order.phone = cur_order.phone
        order.delivery_type = cur_order.delivery_type
        order.payment_type = cur_order.payment_type
        order.total_cost = cur_order.total_cost
        order.status = 'Paid'
        order.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=500)


def avatar(request):
    if request.method == "POST":
        user = get_object_or_404(User, id=request.user.id)
        if Profile.objects.filter(user_id=request.user).exists():
            user_cur = get_object_or_404(Profile, user_id=user)
            user_cur.avatar = request.FILES['avatar']
            user_cur.save()
        # return HttpResponse(status=500)
        else:
            profile = Profile()
            profile.user_id = user
            profile.avatar = request.FILES['avatar']
            profile.save()
        return HttpResponse(status=200)
