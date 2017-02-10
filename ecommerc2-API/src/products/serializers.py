from rest_framework import serializers
from .models import Category


class CategorySerializers(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='category_detail_api')

    class Meta:
        model = Category
        fields = [
            "url",
            "id",
            "title",
            "description",
        ]