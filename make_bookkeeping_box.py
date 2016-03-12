#!/usr/bin/env python3

from collections import namedtuple, Iterable
from enum import Enum
from itertools import repeat, chain
from math import ceil
from operator import add,sub,mul
from pprint import pprint

Coordinate = namedtuple('Coordinate', ['x', 'y', 'z'])
MCItem = namedtuple('MCItem', ['name', 'id', 'data'])
MCItem.__new__.__defaults__ = ('Barrier', 'minecraft:barrier', 0)

def __CoordinateAdd(self, other):
    assert isinstance(other, Coordinate)
    return Coordinate(*map(add, self ,other))

def __CoordinateMul(self, factor):
    assert isinstance(factor, int)
    return Coordinate(*map(mul, self, repeat(factor)))

def __CoordinateSub(self, other):
    assert isinstance(other, Coordinate)
    return Coordinate(*map(sub, self ,other))

# monkey-patch arithmetic operators into Coordinate
Coordinate.__add__ = __CoordinateAdd
Coordinate.__sub__ = __CoordinateSub
Coordinate.__mul__ = __CoordinateMul

north = Coordinate(0,0,-1)
east  = Coordinate(+1,0,0)
south = Coordinate(0,0,+1)
west  = Coordinate(-1,0,0)
up    = Coordinate(0,1,0)
down  = Coordinate(0,-1,0)

# values are normalized to mean "we're building into direction x,
# face the correct according to that"
itemframefacing = {
        north: 0,
        east:  1,
        south: 2,
        west:  3,
}

commandblockfacing = {
        north: 2,
        east:  5,
        south: 3,
        west:  4,
}

Commandblock = Enum('Commandblock', {
    'plain'     : ('Command Block', 'minecraft:command_block'), 
    'repeating' : ('Repeating Command Block', 'minecraft:repeating_command_block'), 
    'chain'     : ('Chain Command Block', 'minecraft:chain_command_block')
})

def GenCommandBlock(type=Commandblock.plain, direction=north, repeating=False,
        alwaysActive=False):
    """Generate commandblock MCItem"""
    data = commandblockfacing[direction]
    if repeating:
        data += 8
    if alwaysActive:
        data += 16
    return MCItem(*type.value, data=data)

#      S
#      ^
#      |
# W <--+--> E
#      |
#      v 
#      N

def SquareCorners(nwcorner=Coordinate(0,80,0), width=35):
    """Yields starting corner, wall direction and build direction"""
    for (start, wdir, bdir) in (
            ((0,0,0), south, west),
            ((0,0,1), east, south),
            ((1,0,1), north, east),
            ((1,0,0), west, north)):
        yield (nwcorner + (Coordinate(*start) * (width-1)) +Coordinate(*bdir), wdir, bdir)

def DetectorStartIter(numitems=533, height=5, nwcorner=Coordinate(0,80,0)):
    """Yield all starting positions for each single item detector mechanism"""
    lengthwall = ceil(numitems/height/4)
    for (corner, walldir, builddir) in SquareCorners(nwcorner, lengthwall):
        for walloffset in range(lengthwall):
            for heightoffset in range(height):
                yield(corner+(up*heightoffset)+(walldir*walloffset), builddir)

def escaped(val):
    return val.replace('"', '\\"')

t_foundblock      = 'minecraft:wool 5'
t_testforblock    = 'testfor @a[m=s] {{Inventory:[{{{}}}]}}'
t_playsound       = 'playsound minecraft:entity.firework.launch master @a 0 0 0 1 1 1'
t_foundmessage    = 'say Found {}'
t_setblock        = 'setblock {} {} {} {} {} replace'
t_summonitemframe = 'summon ItemFrame {} {} {} {{Facing:{}, Item:{{id: "{}", Damage:{}, ' + \
        'Count:1, Invulnerable:1, tag:{{display:{{Name:"{}"}},Age:1}}}},ItemRotation:0,Invulnerable:1,Age:1}}'
t_commandblock   = 'setblock {} {} {} {} {} replace {{Command:"{}"}}'
t_commandblockauto = 'setblock {} {} {} {} {} replace {{Command:"{}",auto:1}}'

def DetectorString(item = MCItem('Sand', 'minecraft:sand', 0), coord = Coordinate(0,64,0), direction = north):
    """str.format ist eine grosse Scheisse, ich mach das jetzt in haesslich"""
    output = []
    # Redstone Block
    c = coord+(direction*1)
    output.append(t_setblock.format(c.x, c.y, c.z, 'minecraft:redstone_block', 0))
    
    # Labeled Itemframe
    c = coord
    if item.data == '':
        data = 0
    else:
        data = item.data
    output.append(t_summonitemframe.format(c.x, c.y, c.z,
        itemframefacing[direction], item.id, data, item.name))

    # commandblock: check inventory 
    c = coord+(direction*2)
    block = GenCommandBlock(Commandblock.repeating, direction, False)
    if item.data:
        spec = 'id:"{}",Damage:{}s'.format(item.id, item.data)
    else:
        spec = 'id:"{}"'.format(item.id)
    command = escaped(t_testforblock.format(spec))
    output.append(t_commandblock.format(c.x, c.y, c.z,
        block.id, block.data, command))

    # commandblock: replace redstone block
    c = coord+(direction*3)
    block = GenCommandBlock(Commandblock.chain, direction, True)
    # FIXME: make this code position-independant
    bc = coord+(direction*1)
    command = escaped(t_setblock.format(bc.x, bc.y, bc.z,
        'minecraft:emerald_block', 0))
    output.append(t_commandblockauto.format(c.x, c.y, c.z,
        block.id, block.data, command))

    # commandblock: play sound
    c = coord+(direction*4)
    block = GenCommandBlock(Commandblock.chain, direction, True)
    command = escaped(t_playsound)
    output.append(t_commandblockauto.format(c.x, c.y, c.z,
        block.id, block.data, command))

    # commandblock: tell found in chat
    c = coord+(direction*5)
    block = GenCommandBlock(Commandblock.chain, direction, True)
    command = escaped(t_foundmessage.format(item.name))
    output.append(t_commandblockauto.format(c.x, c.y, c.z,
        block.id, block.data, command))

    # return all commands
    return "\n".join(output)
    
def ItemListIter(filename='all_items.txt'):
    """Yield all items from itemlist file"""
    with open(filename) as f:
        for line in f:
            (name, id, data) = [x.strip() for x in line.split(',')]
            yield MCItem(name, id, data)

# main
# /setspawn
width  = 35
heigth = 5
nwcorner = Coordinate(256,90,256)
(x1,_,x2,_) = SquareCorners(nwcorner=nwcorner, width=width)
c1 = x1[0]+Coordinate(-6,-1,-6)
c2 = x2[0]+Coordinate(+6,heigth+2,+6)

print('/fill {} {} {} {} {} {} minecraft:air 0 replace'.format(c1.x, c1.y, c1.z, c2.x, c2.y, c2.z))
print('/fill {} {} {} {} {} {} minecraft:stained_glass 15 outline'.format(c1.x, c1.y, c1.z, c2.x, c2.y, c2.z))

items = tuple(ItemListIter())

for item, (start, direction) in zip(iter(items),
        DetectorStartIter(numitems=len(items), nwcorner=nwcorner)):
    print(DetectorString(item, start, direction))

