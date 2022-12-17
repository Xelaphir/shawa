from django.contrib.auth.models import AbstractUser
from django.db import models


# wrapper, topping, species, sauces, beverage, doping etc
class ComponentType(models.Model):
    type = models.CharField(max_length=20)
    # what types are compatible with each other
    # not sauce with beverage, wrapper to wrapper, etc
    # todo: remove compability
    compability = models.ManyToManyField('self')

    def __str__(self):
        return 'Тип компонента ' + self.type


# kinds of components
class Component(models.Model):
    # probability of getting component from roulette
    rarity = models.PositiveSmallIntegerField()
    # common components is such components that everybody owns
    # not-common components are gotten from the roulette
    # todo: common = rarity 5
    is_common = models.BooleanField(default=True)
    type = models.ForeignKey(ComponentType, null=True, on_delete=models.SET_NULL)
    # cost for 1 kilo of component
    cost = models.PositiveIntegerField()
    # min, max weight of component that can be added to recipe, grams
    min_weight = models.PositiveIntegerField()
    max_weight = models.PositiveIntegerField()
    # such value that shows how small can increasing of component weight be
    weight_step = models.PositiveIntegerField()
    # as component called in recipe making, roulette, auctions etc
    name = models.CharField(max_length=20)
    # в предложном падеже
    name_in = models.CharField(max_length=20)
    # в творительном падеже
    name_with = models.CharField(max_length=20)

    def __str__(self):
        return 'Компонент ' + self.name


# discount got after component exchange
class Discount(models.Model):
    # since all components of the same rarity give the same discount
    # we can choose rarity column as primary key
    rarity = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    # value of discount
    percents = models.PositiveSmallIntegerField()

    def __str__(self):
        return 'Скидка ' + str(self.percents) + \
               ' при обмене компонентов редкости ' + str(self.rarity)


# TODO: add abstract user with authorization
# Customer = AbstractUser
# there were errors with name User, maybe it's worth to rename
class Customer(models.Model):
    components = models.ManyToManyField(Component, through='ComponentOwnership')
    discounts = models.ManyToManyField(Discount, through='DiscountOwnership')

    def __str__(self):
        return 'Ну тупа наш клиент' + str(self.id)


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
    lot = models.ForeignKey('Lot', null=True, on_delete=models.SET_NULL, default=None)

    def __str__(self):
        return str(self.owner) + ' владеет компонентом '\
               + str(self.component.name) + ' в количестве ' + str(self.quantity)


class DiscountOwnership(Ownership):
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.owner) + ' владеет скидкочными картами в '\
               + str(self.discount.percents) + '% в количестве ' + str(self.quantity)


# Just a combination of compatible components
class Recipe(models.Model):
    name = models.CharField(max_length=40)
    author = models.ForeignKey(Customer, on_delete=models.CASCADE)
    composition = models.ManyToManyField(Component, through='RecipeComposition')
    price = models.PositiveIntegerField()
    is_private = models.BooleanField(default=True)
    rating = models.PositiveIntegerField(null=True, default=0)

    def __str__(self):
        return 'Рецепт ' + self.name + ' от ' + str(self.author)


# intermediate table for many-to-many relation between recipes and components
# with additional column net_weight and price
class RecipeComposition(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    # may vary from recipe.min_weight up to recipe.max_weight
    net_weight = models.PositiveIntegerField()

    def __str__(self):
        return str(self.component.name) + ' имеется в рецепте ' + str(self.recipe.name)

# todo: quantity for each component
# Lot for an auction
# It should has one-to-many field to ComponentOwnership, but there isn't such field
# so ComponentOwnership has foreign key to this shit
class Lot(models.Model):
    seller = models.ForeignKey(Customer, related_name='lot_seller', on_delete=models.CASCADE)
    purchaser = models.ForeignKey(Customer, related_name='lot_purchaser', null=True, on_delete=models.SET_NULL)
    price = models.PositiveIntegerField()

    def __str__(self):
        return str(self.seller) + ' предлагает че-то купить за ' + str(self.price)


# set of recipes
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe)
    # sum of recipes's prices
    price = models.PositiveIntegerField()
    # applied discount
    discount = models.ForeignKey(DiscountOwnership, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return 'Заказ от ' + str(self.customer) + ' на сумму ' + str(self.price) + ' бубликов'
