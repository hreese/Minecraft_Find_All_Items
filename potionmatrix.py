#!/usr/bin/env python3

potionnames = {
    0  : "Mundane Potion",
    1  : "Potion of Regeneration",
    2  : "Potion of Swiftness",
    3  : "Potion of Fire Resistance",
    4  : "Potion of Poison",
    5  : "Potion of Healing",
    6  : "Potion of Night Vision",
    7  : "Clear Potion",
    8  : "Potion of Weakness",
    9  : "Potion of Strength",
    10 : "Potion of Slowness",
    11 : "Potion of Leaping",
    12 : "Potion of Harming",
    13 : "Potion of Water Breathing",
    14 : "Potion of Invisibility",
    15 : "Thin Potion",
    16 : "Awkward Potion",
    17 : "Potion of Regeneration",
    18 : "Potion of Swiftness",
    19 : "Potion of Fire Resistance",
    20 : "Potion of Poison",
    21 : "Potion of Healing",
    22 : "Potion of Night Vision",
    23 : "Bungling Potion",
    24 : "Potion of Weakness",
    25 : "Potion of Strength",
    26 : "Potion of Slowness",
    27 : "Potion of Leaping",
    28 : "Potion of Harming",
    29 : "Potion of Water Breathing",
    30 : "Potion of Invisibility",
    31 : "Debonair Potion",
    32 : "Thick Potion",
    33 : "Potion of Regeneration",
    34 : "Potion of Swiftness",
    35 : "Potion of Fire Resistance",
    36 : "Potion of Poison",
    37 : "Potion of Healing",
    38 : "Potion of Night Vision",
    39 : "Charming Potion",
    40 : "Potion of Weakness",
    41 : "Potion of Strength",
    42 : "Potion of Slowness",
    43 : "Potion of Leaping",
    44 : "Potion of Harming",
    45 : "Potion of Water Breathing",
    46 : "Potion of Invisibility",
    47 : "Sparkling Potion",
    48 : "Potent Potion",
    49 : "Potion of Regeneration",
    50 : "Potion of Swiftness",
    51 : "Potion of Fire Resistance",
    52 : "Potion of Poison",
    53 : "Potion of Healing",
    54 : "Potion of Night Vision",
    55 : "Rank Potion",
    56 : "Potion of Weakness",
    57 : "Potion of Strength",
    58 : "Potion of Slowness",
    59 : "Potion of Leaping",
    60 : "Potion of Harming",
    61 : "Potion of Water Breathing",
    62 : "Potion of Invisibility",
    63 : "Stinky Potion",
}

#effects = {
#    1  : { 'n' : 'Regeneration', 't2'    : True },
#    2  : { 'n' : 'Swiftness', 't2'       : True },
#    3  : { 'n' : 'Fire Resistance', 't2' : False },
#    4  : { 'n' : 'Poison', 't2'          : True },
#    5  : { 'n' : 'Healing', 't2'         : True },
#    6  : { 'n' : 'Night Vision', 't2'    : False },
#    8  : { 'n' : 'Weakness', 't2'        : False },
#    9  : { 'n' : 'Strength', 't2'        : True },
#    10 : { 'n' : 'Slowness', 't2'        : False },
#    11 : { 'n' : 'Leaping', 't2'         : True },
#    12 : { 'n' : 'Harming', 't2'         : True },
#    13 : { 'n' : 'Water Breathing', 't2' : False },
#    14 : { 'n' : 'Invisibility', 't2'    : False },
#}

# Source: http://minecraft.gamepedia.com/Potion
brewable_potions = (
    0, 16, 32, 64,
    8192, 8193, 8257, 8225, 8194, 8258, 8226, 8195, 8259, 8197, 8229, 8198,
    8262, 8201, 8265, 8233, 8203, 8267, 8235, 8205, 8269, 8206, 8270,
    8196, 8260, 8228, 8200, 8264, 8202, 8266, 8204, 8236,
)

tier_bit       = 0b0000000000100000
ext_bit        = 0b0000000001000000
can_splash_bit = 0b0010000000000000
splash_bit     = 0b0100000000000000

mask_effect = 0b0000000000001111
mask_name   = 0b0000000000111111
mask_tier   = tier_bit
mask_dura   = ext_bit
mask_splash = splash_bit

def apply_mask(v, mask):
    return v & mask

def is_bit_set(v, mask):
    if apply_mask(v, mask) != 0:
        return True
    else:
        return False

def potionname(v):
    (extended, splash, name, tier) = (False, False, False, False)

    if is_bit_set(v, splash_bit):
        splash = 'Splash'

    if is_bit_set(v, mask_dura):
        extended = 'Extended'
    elif is_bit_set(v, mask_tier):
        tier = 'II'

    name = potionnames[apply_mask(v, mask_name)]

    return ' '.join(filter(None, (extended, splash, name, tier)))

pots = []
# TODO: lingering potions

for p in brewable_potions:
    pots.append([potionname(p), 'minecraft:potion', str(p)])
    if is_bit_set(p, can_splash_bit):
        pots.append([potionname(p), 'minecraft:splash_potion', str(p+can_splash_bit)])

for p in pots:
    print(','.join(p))
