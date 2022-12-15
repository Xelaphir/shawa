from django.contrib.auth.models import AbstractUser
from django.db import models


# wrapper, topping, species, sauces, beverage, doping
class ComponentType(models.Model):
    type = models.CharField(max_length=20)
    # лаваш и пита не сочетаются, а вот помидор и огурец очень даже
    is_self_compatible = models.BooleanField(default=False)


# kinds of components
class Component(models.Model):
    rarity = models.PositiveSmallIntegerField()
    # common components is such components that everybody owns
    # not-common components are gotten from the roulette
    is_common = models.BooleanField(default=True)
    type = models.ForeignKey(ComponentType, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=20)
    # в предложном падеже
    name_in = models.CharField(max_length=20)
    # в творительном падеже
    name_with = models.CharField(max_length=20)


# discount got after component exchange
class Discount(models.Model):
    # since all components of the same rarity give the same discount
    # we can choose rarity column as primary key
    rarity = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    # value of discount
    percents = models.PositiveIntegerField()


# TODO: add abstract user with authorization
# Customer = AbstractUser
# there were errors with name User, maybe it's worth to rename
class Customer(models.Model):
    components = models.ManyToManyField(Component, through='ComponentOwnership')
    discounts = models.ManyToManyField(Discount, through='DiscountOwnership')


# Inherited class for two following classes
# These classes make intermediate tables for many-to-many relations
# with additional columns like 'quantity'
class Ownership(models.Model):
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        abstract = True


class ComponentOwnership(Ownership):
    component = models.ForeignKey(Component, on_delete=models.CASCADE)


class DiscountOwnership(Ownership):
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)
