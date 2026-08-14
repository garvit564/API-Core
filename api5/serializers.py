from rest_framework import serializers
from api.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ["owner"]

    def validate_price(self,value):
        if value <= 0:
            raise serializers.ValidationError("price cannot be less then or equal to zero")  
        return value
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Stock cannot be negative"
            )

        return value

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "Name must contain at least 3 characters"
            )

        return value

    def validate(self, data):
        price = data.get("price")
        discount_price = data.get("discount_price")

        if price is not None and discount_price is not None:
            if discount_price > price:
                raise serializers.ValidationError(
                    "Discount price cannot be greater than price"
                )

        return data

