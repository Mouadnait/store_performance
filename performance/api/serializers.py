from rest_framework import serializers
from core.models import Product, Bill, Client, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "cid"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "pid",
            "title",
            "description",
            "price",
            "old_price",
            "stock",
            "product_status",
            "status",
            "in_stock",
            "featured",
            "digital",
            "sku",
            "category",
            "category_id",
            "date",
            "updated",
        ]
        read_only_fields = ["pid", "date", "updated"]


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "id",
            "lid",
            "full_name",
            "email",
            "phone",
            "address",
            "city",
            "country",
            "postal_code",
        ]
        read_only_fields = ["lid"]


class SaleSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    client_id = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.CharField(required=False, allow_blank=True)


class TimeSeriesRequestSerializer(serializers.Serializer):
    start = serializers.DateField(required=False)
    end = serializers.DateField(required=False)
    granularity = serializers.ChoiceField(choices=["day", "week", "month"], default="day")


class ExportRequestSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=["csv", "xlsx"], default="csv")
    start = serializers.DateField(required=False)
    end = serializers.DateField(required=False)
