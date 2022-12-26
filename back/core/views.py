from random import randrange, choice as randchoice
from bisect import bisect

from .models import Component


# returns id of component to get from roulette
def pick_component():
    entry = randrange(100)              # [0,0] legendary   # [26,55] especial
    prob = [0, 1, 6, 26, 56, 100]       # [1,5] mythical    # [56,99] rare
    rarity = bisect(prob, entry)        # [6,25] epic

    to_pick = [comp.id for comp in Component.objects.filter(rarity=rarity)]
    return randchoice(to_pick)
