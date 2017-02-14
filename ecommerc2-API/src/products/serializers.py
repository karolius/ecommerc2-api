from rest_framework import serializers
from .models import Category, Product, Variation


class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = [
            "id",
            "title",
            "price",
        ]

"""
the error when u not specify many=True on item_set

Got AttributeError when attempting to get a value for field `title` on serializer
`VariationSerializer`. The serializer field might be named incorrectly and not
match any attribute or key on the `RelatedManager` instance. Original exception
text was: 'RelatedManager' object has no attribute 'title'.
"""


class ProductDetailUpdateSerializer(serializers.ModelSerializer):
    variation_set = VariationSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "image",
            "variation_set"
        ]

    def get_image(self, obj):
        return obj.productimage_set.first().image.url


class ProductDetailSerializer(serializers.ModelSerializer):
    variation_set = VariationSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "image",
            "variation_set"
        ]

    def get_image(self, obj):
        try:
            return obj.productimage_set.first().image.url
        except AttributeError:
            return None

    def create(self, validated_data):
        title = validated_data["title"]
        Product.objects.get(title=title)
        product = Product.objects.create(**validated_data)
        return product

    def update(self, instance, validated_data):
        instance.title = validated_data["title"]
        instance.save()
        return instancex


class ProductSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='product_detail_api')
    variation_set = VariationSerializer(many=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "url",
            "id",
            "title",
            "image",
            "variation_set"
        ]

    def get_image(self, obj):
        try:
            return obj.productimage_set.first().image.url
        except AttributeError:
            return None


class CategorySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='category_detail_api')
    product_set = ProductSerializer(many=True)  # we have M2M/FK relationship, O2O->False

    class Meta:
        model = Category
        fields = [
            "url",
            "id",
            "title",
            "description",
            "product_set",  # obj.product_set.all()
            "default_category",
        ]