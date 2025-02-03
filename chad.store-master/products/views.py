from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view 
from products.models import Product, ProductTag, Cart, FavoriteProduct
from products.serializers import CartSerializer, ProductTagSerializer, FavoriteProductSerializer

from products.models import Product, Review
from products.serializers import ProductSerializer, ReviewSerializer


@api_view(['GET', 'POST'])
def product_view(request):
    if request.method == 'GET':
        products = Product.objects.all()
        product_list = []
        
        for product in products:
            product_data = {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'currency': product.currency,
            }
            product_list.append(product_data)

        return Response({'products': product_list})
    elif request.method == "POST":
        data = request.data
        serializer = ProductSerializer(data)
        if serializer.is_valid():
            new_product = Product.objects.create(
                name=data.get('name'),
                description=data.get('description'),
                price=data.get('price'),
                currency=data.get('currency', 'GEL')  
            )
            return Response({'id': new_product.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def review_view(request):
    if request.method == 'GET':
        reviews = Review.objects.all()
        review_list = []
        
        for review in reviews:
            review_data = {
                'id': review.id,
                'product_id': review.product.id,
                'content': review.content,
                'rating': review.rating
            }
            review_list.append(review_data)
        
        return Response({'reviews': review_list})

    elif request.method == 'POST':
        serializer = ReviewSerializer(data=request.data, context={"request":request})
        if serializer.is_valid():
            review = serializer.save()
            return Response(
                {'id': review.id, 'message': 'Review created successfully!'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'POST'])
def cart_view(request):
    user = request.user

    cart, created = Cart.objects.get_or_create(user=user)

    if request.method == 'GET':
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    elif request.method == 'POST':
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        if not isinstance(quantity, int) or quantity < 1:
            return Response({"error": "Quantity must be a positive integer."}, status=status.HTTP_400_BAD_REQUEST)

        cart.products.add(product)
        return Response({"message": f"{product.name} added to cart!"}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def product_tag_view(request):
    product_id = request.query_params.get('product_id')

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        tags = product.tags.all()
        serializer = ProductTagSerializer(tags, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        tag_name = request.data.get('tag_name')

        if not tag_name:
            return Response({"error": "Tag name is required."}, status=status.HTTP_400_BAD_REQUEST)

        tag, created = ProductTag.objects.get_or_create(name=tag_name)
        product.tags.add(tag)

        return Response({"message": f"Tag '{tag.name}' added to {product.name}."}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def favorite_product_view(request):
    user = request.user

    if request.method == 'GET':
        favorites = FavoriteProduct.objects.filter(user=user)
        serializer = FavoriteProductSerializer(favorites, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        product_id = request.data.get('product_id')


        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        favorite, created = FavoriteProduct.objects.get_or_create(user=user, product=product)

        if created:
            return Response({"message": f"{product.name} added to favorites!"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Product is already in favorites!"}, status=status.HTTP_200_OK)