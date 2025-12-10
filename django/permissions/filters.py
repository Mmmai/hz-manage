from django_filters import rest_framework as filters
from .models import Button


class ButtonFilter(filters.FilterSet):
    menu = filters.CharFilter(field_name='menu')

    class Meta:
        model = Button
        fields = [
            'menu',
        ]
