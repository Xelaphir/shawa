from django.urls import path
from .views import *


urlpatterns = [
    # all existing components briefly
    path('components', AllComponentsList.as_view()),

    # ownerships of components i.e. tuple of (component_id, qty)
    path('customer/owns/components/<int:pk>', ComponentOwnershipList.as_view()),
    path('customer/owns/components/<str:username>', ComponentOwnershipList.as_view()),

    # all available (existing in ownership) components in detail
    path('customer/components/<int:pk>', AvailableComponentsList.as_view()),
    path('customer/components/<str:username>', AvailableComponentsList.as_view()),

    # picking a component from roulette
    path('customer/roulette/<int:pk>', Roulette.as_view()),
    path('customer/roulette/<str:username>', Roulette.as_view()),

    # ownerships of discounts i.e. tuple of (rarity, percent, qty(may be null))
    path('customer/discounts/<int:pk>', DiscountsList.as_view()),
    path('customer/discounts/<str:username>', DiscountsList.as_view()),

    # open lots (without specified purchaser) in brief form with paginator
    path('lots/', LotsList.as_view()),
    # lot details like purchaser, stat
    path('lot/<int:pk>', LotDetail.as_view()),

    # branch corresponds to comment with pk:
    # replies, replies to replies, etc
    path('comment/branch/<int:pk>', CommentBranch.as_view())
]
