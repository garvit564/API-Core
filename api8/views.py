from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.db.models import Q,F
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ProductSerializer
from api.models import Product
from django.db import transaction
import logging
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response

logger = logging.getLogger(__name__)
# ============================================================
# PRODUCT PERMISSION
# ============================================================

class ProductPermission(BasePermission):

    def has_permission(self, request, view):

        # Anyone can view products
        if request.method == "GET":
            return True

        # Login required for creating
        if request.method == "POST":
            return request.user.is_authenticated

        # Login required for updating
        if request.method in ["PUT", "PATCH"]:
            return request.user.is_authenticated

        # Only superuser can delete
        if request.method == "DELETE":
            return request.user.is_superuser

        return False

    def has_object_permission(self, request, view, obj):

        # Only owner or superuser can update
        if request.method in ["PUT", "PATCH"]:

            return (
                request.user.is_superuser
                or obj.owner == request.user
            )

        return True

# class LoginThrottle(AnonRateThrottle):
#     scope = "login"
# ============================================================
# LOGIN API
# ============================================================

class LoginView(APIView):

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        # Check username and password
        user = authenticate(
            username=username,
            password=password
        )

        # Wrong credentials
        if user is None:

            return Response(
                {
                    "error": "Invalid username or password"
                },
                status=401
            )

        # Generate refresh token
        refresh = RefreshToken.for_user(user)

        # Generate access token from refresh token
        access = refresh.access_token

        return Response(
            {
                "message": "Login successful",
                "refresh": str(refresh),
                "access": str(access)
            },
            status=200
        )


# ============================================================
# LOGOUT API
# ============================================================

class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        refresh_token = request.data.get("refresh")

        # Refresh token not provided
        if not refresh_token:

            return Response(
                {
                    "error": "Refresh token required"
                },
                status=400
            )

        try:

            # Convert string into RefreshToken object
            token = RefreshToken(refresh_token)

            # Blacklist refresh token
            token.blacklist()

            return Response(
                {
                    "message": "Logout successful"
                },
                status=200
            )

        except Exception:

            return Response(
                {
                    "error": "Invalid refresh token"
                },
                status=400
            )


# ============================================================
# PRODUCT LIST + CREATE
# ============================================================

class ProductListView(APIView):

    permission_classes = [ProductPermission]

    # --------------------------------------------------------
    # GET PRODUCTS
    # --------------------------------------------------------

    def get(self, request):
        cache_key = request.get_full_path()
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        name = request.query_params.get("name")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")
        keyword = request.query_params.get("search")

        products = Product.objects.all()

        # Search
        if keyword:

            products = products.filter(
                name__icontains=keyword
            )

        # Name filter
        if name:

            products = products.filter(
                name__icontains=name
            )

        # Price range filter
        if min_price and max_price:

            products = products.filter(
                Q(price__gte=min_price) &
                Q(price__lte=max_price)
            )

        serializer = ProductSerializer(
            products,
            many=True
        )
        data = serializer.data
        cache.set(
            cache_key,
            data,
            timeout=60
        )

        return Response(
            data,
            status=200
        )

    # --------------------------------------------------------
    # CREATE PRODUCT
    # --------------------------------------------------------

    def post(self, request):

        serializer = ProductSerializer(
            data=request.data
        )

        if serializer.is_valid():

            # Automatically assign logged-in user
            serializer.save(
                owner=request.user
            )
            
            cache.clear()

            logger.info(
                "Product created successfully: user_id=%s",
                request.user.id
            )

            return Response(
                serializer.data,
                status=201
            )
        
        logger.warning(
            "Product creation failed validation: user_id=%s",
            request.user.id
        )

        return Response(
            serializer.errors,
            status=400
        )


# ============================================================
# PRODUCT DETAIL
# ============================================================

class ProductDetailView(APIView):

    permission_classes = [ProductPermission]

    # --------------------------------------------------------
    # PUT
    # --------------------------------------------------------

    def put(self, request, id):

        try:

            product = Product.objects.get(
                id=id
            )

        except Product.DoesNotExist:

            return Response(
                {
                    "error": "Product not found"
                },
                status=400
            )

        # Check owner/superuser permission
        self.check_object_permissions(
            request,
            product
        )

        serializer = ProductSerializer(
            product,
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()
            cache.clear()

            return Response(
                serializer.data,
                status=200
            )

        return Response(
            serializer.errors,
            status=400
        )

    # --------------------------------------------------------
    # PATCH
    # --------------------------------------------------------

    def patch(self, request, id):

        product = get_object_or_404(
            Product,
            id=id
        )

        # Check owner/superuser permission
        self.check_object_permissions(
            request,
            product
        )

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()
            cache.clear()

            return Response(
                serializer.data,
                status=200
            )

        return Response(
            serializer.errors,
            status=400
        )

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    def delete(self, request, id):

        product = get_object_or_404(
            Product,
            id=id
        )

        product.delete()
        cache.clear()

        return Response(
            {
                "message": "Product deleted successfully"
            },
            status=204
        )



class ProductStockView(APIView):

    permission_classes = [ProductPermission]

    def patch(self, request, id):

        change = request.data.get("change")

        if change is None:
            return Response(
                {"error": "change is required"},
                status=400
            )

        try:
            change = int(change)

        except (ValueError, TypeError):
            return Response(
                {"error": "change must be a number"},
                status=400
            )

        # Calculate minimum required stock
        if change < 0:
            required_stock = abs(change)
        else:
            required_stock = 0

        # Start transaction
        with transaction.atomic():

            # Get product and lock its row
            try:
                product = Product.objects.select_for_update().get(
                    id=id
                )

            except Product.DoesNotExist:
                return Response(
                    {"error": "Product not found"},
                    status=404
                )

            # Check whether enough stock is available
            if product.stock < required_stock:

                return Response(
                    {"error": "Insufficient stock"},
                    status=400
                )

            # Database-level update using F()
            Product.objects.filter(
                id=id
            ).update(
                stock=F("stock") + change
            )

            # Get updated value
            product.refresh_from_db()

        # Transaction successfully committed
        cache.clear()

        return Response(
            {
                "id": product.id,
                "stock": product.stock
            },
            status=200
        )



class HealthCheckView(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request):

        try:

            # Try to communicate with database
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")

            return Response(
                {
                    "status": "healthy",
                    "database": "ok"
                },
                status=200
            )

        except Exception:

            return Response(
                {
                    "status": "unhealthy",
                    "database": "error"
                },
                status=503
            )    