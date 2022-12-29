from django.db import models


# general types of components, classified by using in the same way
class ComponentType(models.Model):
    # wrp=wrapper, tpp=topping, sau=sauce, dcr=decoration, bvr=beverage, dpn=doping
    name = models.CharField(max_length=3)
    # e.g., it's impossible to mix wrapper with beverage in one recipe...
    compability = models.ManyToManyField('self')
    # g=гр, m=мл, q=шт
    measure = models.CharField(max_length=1, default='g')

    # related fields
    # type_instances

    def __str__(self):
        return 'Тип компонента {}'.format(self.name)


# kinds of components
class Component(models.Model):
    type = models.ForeignKey(ComponentType, related_name='type_instances',
                             null=True, on_delete=models.SET_NULL)

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
    # в предложном падеже или творительном падеже
    name_in_with = models.CharField(max_length=20)
    # delicious description
    desc = models.CharField(max_length=50, blank=True, default='')

    # related fields
    # owned_by, contained_in

    def __str__(self):
        return 'Компонент {}'.format(self.name)


# discount got after component exchange
class Discount(models.Model):
    # since all components of the same rarity give the same discount
    # we can choose rarity column as primary key
    rarity = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    # value of discount
    percents = models.PositiveSmallIntegerField()

    # related fields
    # owned_by

    def __str__(self):
        return 'Скидка {}% при обмене компонентов редкости {}' \
            .format(str(self.percents), str(self.rarity))


# TODO: add AbstractUser with authorization
class Customer(models.Model):
    components = models.ManyToManyField('Component', related_name='owned_by',
                                        through='ComponentOwnership')
    discounts = models.ManyToManyField('Discount', related_name='owned_by',
                                       through='DiscountOwnership')
    coins = models.PositiveIntegerField(default=0)

    # related fields
    # bought_lots, written_comments, upvote_for, downvote_for, react_with, created_orders

    def __str__(self):
        return 'Ну тупа наш клиент {}'.format(str(self.id))


# intermediate tables for M2M ownerships with additional columns like qty
class ComponentOwnership(models.Model):
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    qty = models.PositiveSmallIntegerField(default=1)

    # related fields
    # declared_lot

    def __str__(self):
        return '{} владеет компонентом {} в количестве {} шт' \
            .format(str(self.owner), self.component.name, str(self.qty))


class DiscountOwnership(models.Model):
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rarity = models.ForeignKey(Discount, on_delete=models.CASCADE, db_column='rarity')
    qty = models.PositiveSmallIntegerField(default=1)

    # related fields
    # applied_to

    def __str__(self):
        return '{} владеет скидкой на {}% в количестве {}' \
            .format(str(self.owner), str(self.rarity.percents), str(self.qty))


# Lot for an auction
class Lot(models.Model):
    # see Comment for explanations
    seller_comm = models.ForeignKey('Comment', related_name='linked_lot',
                                    on_delete=models.RESTRICT)
    purchaser = models.ForeignKey('Customer', related_name='bought_lots',
                                  null=True, on_delete=models.SET_NULL)
    price = models.PositiveIntegerField(default=0)
    # fast estimation for ordering
    rating = models.IntegerField(default=0)
    # see LotStat for explanations
    stat = models.ForeignKey('LotStat', related_name='observed_lot',
                             on_delete=models.RESTRICT)

    # related fields
    # consist_of,

    class Meta:
        ordering = ['rating']

    def __str__(self):
        return '{} предлагает че-то купить за {}' \
            .format(str(self.seller_comm.author), str(self.price))


# intermediate table for M2M relation between Lot and ComponentOwnership
# with additional field qty
class LotItem(models.Model):
    lot = models.ForeignKey('Lot', related_name='consist_of', on_delete=models.CASCADE)
    item = models.ForeignKey('ComponentOwnership', related_name='declared_lot',
                             on_delete=models.CASCADE)
    qty = models.PositiveSmallIntegerField(default=1)


# Just a combination of compatible components
class Recipe(models.Model):
    # see Comment for explanations
    author_comm = models.ForeignKey('Comment', related_name='linked_recipe',
                                    on_delete=models.RESTRICT)
    composition = models.ManyToManyField('Component', related_name='contained_in',
                                         through='RecipeComposition')
    price = models.PositiveIntegerField(default=0)
    is_private = models.BooleanField(default=True)
    # fast estimation for ordering
    rating = models.IntegerField(default=0)
    # see RecipeStat for explanations
    stat = models.ForeignKey('RecipeStat', related_name='observed_recipe',
                             on_delete=models.RESTRICT)

    # related fields
    # contained_in

    class Meta:
        ordering = ['rating']

    def __str__(self):
        return 'Рецепт {} от {}' \
            .format(self.author_comm.text, str(self.author_comm.author))


# intermediate table for M2M relation between recipes and components with additional column qty
class RecipeComposition(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    component = models.ForeignKey('Component', on_delete=models.CASCADE)
    # may vary from component.min_qty up to component.max_qty
    qty = models.PositiveSmallIntegerField()

    def __str__(self):
        return '{} имеется в рецепте {} в количестве {}' \
            .format(self.component.name, str(self.recipe.id), str(self.qty))


# Lot and Recipe have FK to the Comment for the following reasons:
# Comment has (author, text) = (Customer FK, TextField)
#                            = (LotSeller/RecipeAuthor, comm)
# another customers can write comments with arbitrary nesting level - work for reply_to field
class Comment(models.Model):
    author = models.ForeignKey('Customer', related_name='written_comments',
                               on_delete=models.CASCADE)
    text = models.TextField(max_length=1000, blank=True, default='')
    reply_to = models.ForeignKey('Comment', related_name='self_replies',
                                 null=True, on_delete=models.CASCADE)

    # related fields
    # linked_lot OR linked_recipe, self_replies

    def __str__(self):
        return '{} написал: {}'.format(str(self.author), self.text)


# inherited class for the LotStat and RecipeStat
class Stat(models.Model):
    # lets count requests to backend from authorized customers
    views = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True


# each lot may be rated with thumb up or down
# to prevent repeatable votes from one customer we should save customers votes
class LotStat(Stat):
    upvotes = models.ManyToManyField('Customer', related_name='upvote_for')
    downvotes = models.ManyToManyField('Customer', related_name='downvote_for')

    # related fields
    # observed_lot OR observed_recipe,

    def __str__(self):
        return 'Пальцев вверх {} и вниз {}' \
            .format(str(self.upvotes.count()), str(self.downvotes.count()))


# likely to LotStat yet each recipe can be rated with more votes (reactions)
class RecipeStat(Stat):
    reactions = models.ManyToManyField('Customer', related_name='react_with',
                                       through='RecipeStatReactions')

    def __str__(self):
        return 'Всего реакций {}'.format(str(self.reactions.count()))


# our measure of taste
class Reaction(models.Model):
    # dsg=disgusting, ins=insipid, swt=sweet, slt=salty, btr=bitter, sor=sour, ppr=pepper
    taste = models.CharField(max_length=3)

    # related fields
    # reacted_to

    def __str__(self):
        return 'Вкус {}'.format(self.taste)


# intermediate table for M2M relations between recipe stats and customers
# with additional field reaction
class RecipeStatReactions(models.Model):
    stat = models.ForeignKey('RecipeStat', on_delete=models.CASCADE)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    reaction = models.ForeignKey('Reaction', related_name='reacted_to',
                                 on_delete=models.CASCADE)

    def __str__(self):
        return '{} отреагировал: {}'.format(str(self.customer), str(self.reaction))


# set of recipes
class Order(models.Model):
    customer = models.ForeignKey('Customer', related_name='created_orders',
                                 on_delete=models.CASCADE)
    recipes = models.ManyToManyField('Recipe', related_name='contained_in',
                                     through='OrderComposition')
    # sum of recipes's prices
    price = models.PositiveIntegerField()
    # applied discount
    discount = models.ForeignKey('DiscountOwnership', related_name='applied_to',
                                 null=True, on_delete=models.SET_NULL, default=None)

    def __str__(self):
        return 'Заказ от {} на сумму {} бубликов' \
            .format(str(self.customer), str(self.price))


# intermediate table for M2M composition of order with additional column qty
class OrderComposition(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    qty = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return '{} есть в {} в количестве {}' \
            .format(str(self.recipe), str(self.order), str(self.qty))
