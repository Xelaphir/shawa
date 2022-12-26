from django.db import models


# wrapper, topping, sauces, beverage, doping
class ComponentType(models.Model):
    type = models.CharField(max_length=20)
    compability = models.ManyToManyField('self')

    MEASURE_CHOICES = [
        ('m', 'мл'),    # beverages
        ('g', 'гр'),    # others
    ]
    measure = models.CharField(max_length=1, choices=MEASURE_CHOICES, default='g')

    def __str__(self):
        return 'Тип компонента ' + self.type


# kinds of components
class Component(models.Model):
    type = models.ForeignKey(ComponentType, null=True, on_delete=models.SET_NULL)

    # 1 - legendary 2 - mythical 3 - epic 4 - especial 5 - rare 6 - common
    rarity = models.PositiveSmallIntegerField(default=6)

    # cost for 1 kilo/liter of component
    cost = models.PositiveSmallIntegerField()
    # min, max quantity of component that can be added to recipe
    min_qty = models.PositiveSmallIntegerField()
    max_qty = models.PositiveSmallIntegerField()
    # such value that shows how small can increasing of component quantity be
    qty_step = models.PositiveSmallIntegerField()

    # as component called in recipe making, roulette, auctions etc
    name = models.CharField(max_length=20)
    # в предложном падеже и творительном падеже
    name_in = models.CharField(max_length=20)
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


# TODO: add AbstractUser with authorization
class Customer(models.Model):
    components = models.ManyToManyField(Component, through='ComponentOwnership')
    discounts = models.ManyToManyField(Discount, through='DiscountOwnership')
    coins = models.PositiveIntegerField(default=0)

    def __str__(self):
        return 'Ну тупа наш клиент' + str(self.id)


# intermediate tables for many-to-many relations with additional columns like qty
class ComponentOwnership(models.Model):
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField()

    # ! self.qty >= self.lot_qty !
    lot = models.ForeignKey('Lot', null=True, on_delete=models.SET_NULL, default=None)
    lot_qty = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.owner) + ' владеет компонентом ' \
               + str(self.component.name) + ' в количестве ' + str(self.qty)


class DiscountOwnership(models.Model):
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rarity = models.ForeignKey(Discount, on_delete=models.CASCADE, db_column='discount_rarity')
    qty = models.PositiveIntegerField()

    def __str__(self):
        return str(self.owner) + ' владеет скидкочными картами в ' \
               + str(self.rarity.percents) + '% в количестве ' + str(self.qty)


# Lot for an auction
# It should has one-to-many field to ComponentOwnership, but there isn't such field
# so ComponentOwnership has foreign key to this shit
class Lot(models.Model):
    seller = models.ForeignKey(Customer, related_name='lot_seller', on_delete=models.CASCADE)
    purchaser = models.ForeignKey(Customer, related_name='lot_purchaser', null=True, on_delete=models.SET_NULL)
    price = models.PositiveIntegerField()

    def __str__(self):
        return str(self.seller) + ' предлагает че-то купить за ' + str(self.price)


# Just a combination of compatible components
class Recipe(models.Model):
    name = models.CharField(max_length=40, default='')
    author = models.ForeignKey(Customer, on_delete=models.CASCADE)
    composition = models.ManyToManyField(Component, through='RecipeComposition')
    price = models.PositiveIntegerField()
    is_private = models.BooleanField(default=True)
    rating = models.PositiveIntegerField(null=True, default=0)

    def __str__(self):
        return 'Рецепт ' + self.name + ' от ' + str(self.author)


# intermediate table for many-to-many relation between recipes and components
# with additional column qty
class RecipeComposition(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    # may vary from component.min_qty up to component.max_qty
    qty = models.PositiveIntegerField()

    def __str__(self):
        return str(self.component.name) + ' имеется в рецепте ' + str(self.recipe.name)


# set of recipes
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe, through='OrderComposition')
    # sum of recipes's prices
    price = models.PositiveIntegerField()
    # applied discount
    discount = models.ForeignKey(DiscountOwnership, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return 'Заказ от ' + str(self.customer) + ' на сумму ' + str(self.price) + ' бубликов'


# composition of order with additional column qty
class OrderComposition(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    qty = models.PositiveSmallIntegerField(default=1)
