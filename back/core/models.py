from django.db.models import Model, CASCADE, SET_NULL, SET_DEFAULT, RESTRICT, \
    IntegerField, PositiveIntegerField, PositiveSmallIntegerField, CharField, TextField, \
    BooleanField, ForeignKey, ManyToManyField

# general types of components, classified by using in the same way
class ComponentType(Model):
    # wrp=wrapper, tpp=topping, sau=sauce, dcr=decoration, bvr=beverage, dpn=doping
    name = CharField(max_length=3)
    # e.g., it's impossible to mix wrapper with beverage in one recipe...
    compability = ManyToManyField('self')
    # g=гр, m=мл, q=шт
    measure = CharField(max_length=1, default='g')

    # related fields
    # type_instances

    def __str__(self):
        return 'Тип компонента {}'.format(self.name)


# components in their wild nature
class Component(Model):
    type = ForeignKey(ComponentType, related_name='type_instances',
                             null=True, on_delete=SET_NULL)

    # 1 - legendary 2 - mythical 3 - epic 4 - especial 5 - rare 6 - common
    rarity = PositiveSmallIntegerField(default=6)

    # cost for 1 kilo/liter of component
    cost = PositiveSmallIntegerField()
    # min, max quantity of component that can be added to recipe
    min_qty = PositiveSmallIntegerField()
    max_qty = PositiveSmallIntegerField()
    # such value that shows how small can increasing of component quantity be
    qty_step = PositiveSmallIntegerField()

    # as component called in recipe making, roulette, auctions etc
    name = CharField(max_length=20)
    # в предложном падеже или творительном падеже
    name_in_with = CharField(max_length=20)
    # delicious description
    desc = CharField(max_length=50, blank=True, default='')

    # related fields
    # owned_by, contained_in

    def __str__(self):
        return 'Компонент {}'.format(self.name)


# discount got after component exchange
class Discount(Model):
    # since all components of the same rarity give the same discount
    # we can choose rarity column as primary key
    rarity = PositiveSmallIntegerField(unique=True, primary_key=True)
    # value of discount
    percents = PositiveSmallIntegerField()

    # related fields
    # owned_by

    def __str__(self):
        return 'Скидка {}% при обмене компонентов редкости {}' \
            .format(str(self.percents), str(self.rarity))


# TODO: add AbstractUser with authorization
class Customer(Model):
    components = ManyToManyField('Component', related_name='owned_by',
                                        through='ComponentOwnership')
    discounts = ManyToManyField('Discount', related_name='owned_by',
                                       through='DiscountOwnership')
    coins = PositiveIntegerField(default=0)

    # related fields
    # bought_lots, written_comments, upvote_for, downvote_for, react_with, created_orders

    def __str__(self):
        return 'Ну тупа наш клиент {}'.format(str(self.id))


# intermediate tables for M2M ownerships with additional columns like qty
class ComponentOwnership(Model):
    owner = ForeignKey('Customer', on_delete=CASCADE)
    component = ForeignKey('Component', on_delete=CASCADE)
    qty = PositiveSmallIntegerField(default=1)

    # 1:M (Lot:ComponentOwnership) relation
    lot = ForeignKey('Lot', related_name='consist_of',
                            null=True, on_delete=SET_NULL, default=None)
    lot_qty = PositiveSmallIntegerField(null=True, default=None)

    def __str__(self):
        return '{} владеет компонентом {} в количестве {} шт' \
            .format(str(self.owner), self.component.name, str(self.qty))


class DiscountOwnership(Model):
    owner = ForeignKey(Customer, on_delete=CASCADE)
    rarity = ForeignKey(Discount, on_delete=CASCADE, db_column='rarity')
    qty = PositiveSmallIntegerField(default=1)

    # related fields
    # applied_to

    def __str__(self):
        return '{} владеет скидкой на {}% в количестве {}' \
            .format(str(self.owner), str(self.rarity.percents), str(self.qty))


# Lot and Recipe have FK to the Comment for the following reasons:
# Comment has (author, text) = (Customer FK, TextField)
#                            = (LotSeller/RecipeAuthor, comm)
# another customers can write comments with arbitrary nesting level - work for reply_to field
class Comment(Model):
    author = ForeignKey('Customer', related_name='written_comments', on_delete=CASCADE)
    text = TextField(max_length=1000, blank=True, default='')
    reply_to = ForeignKey('Comment', related_name='self_replies',
                                 null=True, on_delete=CASCADE)

    # related fields
    # linked_lot OR linked_recipe, self_replies

    def __str__(self):
        return '{} написал: {}'.format(str(self.author), self.text)


# common stat for Lot and Recipe
class Stat(Model):
    # lets count requests from backend from authorized customers
    views = PositiveIntegerField(default=0)
    # updated in views.py before creating comment
    comments_count = PositiveIntegerField(default=0)

    # related fields
    # observed_lot OR observed_recipe

    def __str__(self):
        return '{} просмотров и {} комментариев'.format(str(self.views), str(self.comments_count))


# our measure of taste
class Reaction(Model):
    # dsg=disgusting, ins=insipid, swt=sweet, slt=salty, btr=bitter, sor=sour, ppr=pepper
    taste = CharField(max_length=3)

    # related fields
    # reacted_to

    def __str__(self):
        return 'Вкус {}'.format(self.taste)


# Lot for an auction
class Lot(Model):
    # see Comment for explanations
    seller_comm = ForeignKey('Comment', related_name='linked_lot',
                                    on_delete=RESTRICT)
    purchaser = ForeignKey('Customer', related_name='bought_lots',
                                  null=True, on_delete=SET_NULL)
    price = PositiveIntegerField(default=0)
    # fast estimation for ordering
    rating = IntegerField(default=0)
    # see Stat for explanations
    stat = ForeignKey('Stat', related_name='observed_lot', on_delete=RESTRICT)

    # each lot may be rated with thumb up or down
    # to prevent repeatable votes from one customer we should save customers votes
    upvotes = ManyToManyField('Customer', related_name='upvote_for')
    downvotes = ManyToManyField('Customer', related_name='downvote_for')
    # for fast estimation of how many up/down votes were given at specific lot
    # updated in views.py before updating the vote from one frontend
    upvotes_count = PositiveIntegerField(default=0)
    downvotes_count = PositiveIntegerField(default=0)

    # related fields
    # consist_of

    class Meta:
        ordering = ['rating']

    def __str__(self):
        return '{} предлагает че-то купить за {}' \
            .format(str(self.seller_comm.author), str(self.price))


# Just a combination of compatible components
class Recipe(Model):
    # see Comment for explanations
    author_comm = ForeignKey('Comment', related_name='linked_recipe',
                                    on_delete=RESTRICT)
    composition = ManyToManyField('Component', related_name='contained_in',
                                         through='RecipeComposition')
    price = PositiveIntegerField(default=0)
    is_private = BooleanField(default=True)
    # fast estimation for ordering
    rating = IntegerField(default=0)
    # see Stat for explanations
    stat = ForeignKey('Stat', related_name='observed_recipe', on_delete=RESTRICT)

    # like lot up/down votes yet with more reactions (see Reaction class)
    reactions = ManyToManyField('Customer', related_name='react_with',
                                through='CustomersReactToRecipes')
    # for fast estimation of how many reactions of each type at specific recipe were given
    # updated in views.py before updating the reaction from each frontend
    reactions_count = ManyToManyField('Reaction', related_name='times_reacted',
                                      through='RecipeReactionsCount')

    # related fields
    # contained_in

    class Meta:
        ordering = ['rating']

    def __str__(self):
        return 'Рецепт {} от {}' \
            .format(self.author_comm.text, str(self.author_comm.author))


# intermediate table for M2M relation btw recipes and components with additional column qty
class RecipeComposition(Model):
    recipe = ForeignKey('Recipe', on_delete=CASCADE)
    component = ForeignKey('Component', on_delete=CASCADE)
    # may vary from component.min_qty up to component.max_qty
    qty = PositiveSmallIntegerField()

    def __str__(self):
        return '{} имеется в рецепте {} в количестве {}' \
            .format(self.component.name, str(self.recipe.id), str(self.qty))


# intermediate table for M2M relations btw recipes and customers
# with additional field reaction
class CustomersReactToRecipes(Model):
    recipe = ForeignKey('Recipe', on_delete=CASCADE)
    customer = ForeignKey('Customer', on_delete=CASCADE)
    reaction = ForeignKey('Reaction', related_name='reacted_to', on_delete=CASCADE)

    def __str__(self):
        return '{} отреагировал: {}'.format(str(self.customer), str(self.reaction))


# intermediate table for M2M relations btw recipes and reactions
# with additional field qty
class RecipeReactionsCount(Model):
    recipe = ForeignKey('Recipe', on_delete=CASCADE)
    reaction = ForeignKey('Reaction', on_delete=CASCADE)
    qty = PositiveIntegerField(default=0)

    def __str__(self):
        return '{} реакций {} на {}'.format(str(self.qty), str(self.reaction), str(self.recipe))


# set of recipes
class Order(Model):
    customer = ForeignKey('Customer', related_name='created_orders',
                                 on_delete=CASCADE)
    recipes = ManyToManyField('Recipe', related_name='contained_in',
                                     through='OrderComposition')
    # sum of recipes's prices
    price = PositiveIntegerField()
    # applied discount
    discount = ForeignKey('DiscountOwnership', related_name='applied_to',
                                 null=True, on_delete=SET_NULL, default=None)

    def __str__(self):
        return 'Заказ от {} на сумму {} бубликов' \
            .format(str(self.customer), str(self.price))


# intermediate table for M2M composition of order with additional column qty
class OrderComposition(Model):
    order = ForeignKey('Order', on_delete=CASCADE)
    recipe = ForeignKey('Recipe', on_delete=CASCADE)
    qty = PositiveSmallIntegerField(default=1)

    def __str__(self):
        return '{} есть в {} в количестве {}' \
            .format(str(self.recipe), str(self.order), str(self.qty))
