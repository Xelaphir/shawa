from random import randrange, choice as randchoice
from bisect import bisect

from rest_framework import generics
from rest_framework.response import Response

from .models import *
from .serializers import *
from .paginators import *


class AllComponentsList(generics.ListAPIView):
    queryset = Component.objects.all()
    serializer_class = BriefComponentSr


class ComponentOwnershipList(generics.ListAPIView):
    queryset = ComponentOwnership.objects.all()
    serializer_class = ComponentOwnershipSr

    # select only ownerships corresponded to the specified customer
    def list(self, request, *args, **kwargs):
        if 'username' in kwargs:
            ownership = ComponentOwnership.objects.filter(owner_username=kwargs['username'])
        else:
            ownership = ComponentOwnership.objects.filter(owner_id=kwargs['pk'])
        serializer = ComponentOwnershipSr(ownership, many=True)
        return Response(serializer.data)


class AvailableComponentsList(generics.ListAPIView):
    queryset = Component.objects.all()
    serializer_class = DetailComponentSr

    # select only components in ownership of the specified customer applying another serializer
    def list(self, request, *args, **kwargs):
        if 'username' in kwargs:
            ownership = ComponentOwnership.objects.filter(owner_username=kwargs['username'])
        else:
            ownership = ComponentOwnership.objects.filter(owner_id=kwargs['pk'])
        comp_ids = [o.component.id for o in ownership]
        available_comps = Component.objects.filter(id__in=comp_ids)
        serializer = DetailComponentSr(available_comps, many=True)
        return Response(serializer.data)


# returns id of component to get from roulette
def pick_component():
    # picking the rarity
    entry = randrange(100)              # [0,0] legendary   # [26,55] especial
    prob = [0, 1, 6, 26, 56, 100]       # [1,5] mythical    # [56,99] rare
    rarity = bisect(prob, entry)        # [6,25] epic

    # todo: remove when there are at least one component with each rarity
    rarity = 6
    # picking the component
    to_pick = [comp.id for comp in Component.objects.filter(rarity=rarity)]
    return randchoice(to_pick)


# implementation of picking component from roulette
class Roulette(generics.RetrieveAPIView):
    queryset = Component.objects.all()
    serializer_class = BriefComponentSr

    def retrieve(self, request, *args, **kwargs):
        # picking random component
        comp_id = pick_component()

        # increasing qty in ComponentOwnership by 1 or creating a new row with qty=1
        if 'username' in kwargs:
            pk = Customer.objects.get(username=kwargs['username']).id
        else:
            pk = kwargs['pk']

        try:
            ownership = ComponentOwnership.objects.get(owner_id=pk, component_id=comp_id)
            ownership.qty += 1
            ownership.save()
        except ComponentOwnership.DoesNotExist:
            ComponentOwnership.objects.create(owner_id=pk, component_id=comp_id, qty=1)

        # returning picked component
        component = Component.objects.get(id=comp_id)
        serializer = BriefComponentSr(component)
        return Response(serializer.data)


class DiscountsList(generics.ListAPIView):
    queryset = DiscountOwnership.objects.all()
    serializer_class = DiscountSr

    # implements such sql query:
    # SELECT rarity, percents, qty
    # FROM Discount LEFT JOIN DiscountOwnership USING(rarity)
    # WHERE DiscountOwnership.owner=pk
    def list(self, request, *args, **kwargs):
        if 'username' in kwargs:
            pk = Customer.objects.get(username=kwargs['username']).id
        else:
            pk = kwargs['pk']
        existing_discounts = DiscountOwnership.objects.filter(owner_id=pk)

        # adding such discounts to ownership that are not in ownership yet with qty=0
        if len(existing_discounts) < Discount.objects.count():
            all_rarities = set([d.rarity for d in Discount.objects.all()])
            existing_rarities = set([d.rarity.rarity for d in existing_discounts])
            for rarity in all_rarities - existing_rarities:
                d = Discount.objects.get(rarity=rarity)
                DiscountOwnership.objects.create(owner_id=pk, rarity=d, qty=0)

        existing_discounts = DiscountOwnership.objects.filter(owner_id=pk)
        serializer = DiscountSr(existing_discounts, many=True)
        return Response(serializer.data)


class LotsList(generics.ListAPIView):
    queryset = Lot.objects.all()
    serializer_class = LotSr
    pagination_class = LotsPg
