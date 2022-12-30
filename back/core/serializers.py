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


class LotItemSr(sr.ModelSerializer):
    class Meta:
        model = ComponentOwnership
        fields = ('component', 'lot_qty')


class BriefLotSr(sr.ModelSerializer):
    consist_of = LotItemSr(many=True, read_only=True)

    class Meta:
        model = Lot
        fields = ('price', 'consist_of')


class DetailLotSr(sr.ModelSerializer):
    # todo: alter src to seller_comm.author.username when ready
    seller = sr.IntegerField(source='seller_comm.author.id')
    comm = sr.CharField(source='seller_comm.text')
    views = sr.IntegerField(source='stat.views')
    comments_count = sr.IntegerField(source='stat.comments_count')

    class Meta:
        model = Lot
        fields = ('seller', 'comm', 'purchaser', 'views',
                  'comments_count', 'upvotes_count', 'downvotes_count')
