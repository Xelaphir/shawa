from rest_framework import serializers as sr
from .models import *


# used in url 'components'
class BriefComponentSr(sr.ModelSerializer):
    type_name = sr.CharField(max_length=3, source='type.name')

    class Meta:
        model = Component
        fields = ('id', 'type_name', 'rarity', 'name', 'desc')


# used in url 'customer/components/'
class DetailComponentSr(sr.ModelSerializer):
    type_measure = sr.CharField(max_length=1, source='type.measure')

    class Meta:
        model = Component
        fields = ('id', 'type_measure', 'cost', 'min_qty', 'max_qty', 'qty_step', 'name_in_with')


# used in url 'customer/owns/components/'
class ComponentOwnershipSr(sr.ModelSerializer):
    class Meta:
        model = ComponentOwnership
        fields = ('component', 'qty')


# used in url 'discounts'
class DiscountSr(sr.ModelSerializer):
    rarity = sr.IntegerField(source='rarity.rarity')
    percents = sr.IntegerField(source='rarity.percents')

    class Meta:
        model = DiscountOwnership
        fields = ('rarity', 'percents', 'qty')



