from random import sample

from BlockSearch.block import Block, ORIENTATIONS, ORIENTATION, Floor, RingFloor
from unittest import TestCase
from stl import mesh
from BlockSearch.render import *
from matplotlib.colors import to_rgba
import time
# from BlockSearch.tower_state import Tower_State
from pprint import pprint as pp

DISPLAY = True  # False
block_mesh = mesh.Mesh.from_file('kapla.stl')
floor_mesh = mesh.Mesh.from_file('floor.stl')


class Block_Test(TestCase):

    def test_constructor(self):
        block1 = Block(block_mesh, (0, 0, 0), (0, 0, 0))
        self.assertEqual(list(block1.get_cog()), [0, 0, 0])
        if DISPLAY:
            print(str(block1))
            display([block1.render()])

    def test_translate(self):
        block1 = Block(block_mesh, (0, 0, 0), (10, 10, 10))
        self.assertEqual(list(block1.get_cog()), [10, 10, 10])
        if DISPLAY:
            print(str(block1))
            display([block1.render()])

    def test_rotate(self):
        blocks = []
        for orientation in ORIENTATIONS:
            blocks.append(Block(block_mesh, orientation, (0, 0, 0)))
        for block in blocks:
            self.assertEqual(list(block.get_cog()), [0, 0, 0])
        if DISPLAY:
            for b in blocks:
                print (b)
            display([b.render() for b in blocks])

        with self.assertRaises(AssertionError):
            Block(block_mesh, (-90, -90, -90), (0, 0, 0))

    def test_overlap(self):
        block1 = Block(block_mesh, (0, 0, 0), (0, 0, 0))

        #Overlapping
        overlapping_blocks = []

        overlapping_blocks.append(Block(block_mesh, (0, 0, 0), (0, 0, 0)))      # 0
        overlapping_blocks.append(Block(block_mesh, (90, 90, 0), (0, 0, 1)))    # 1
        overlapping_blocks.append(Block(block_mesh, (90, 0, 0), (0, 7, 0)))     # 2
        overlapping_blocks.append(Block(block_mesh, (90, 0, 0), (0, -7, 0)))    # 3
        overlapping_blocks.append(Block(block_mesh, (90, 0, 0), (0, 0, 0)))     # 4
        for i, block in enumerate(overlapping_blocks):
            if DISPLAY:
                display([b.render() for b in [block1, block]])
                display_multiple_cells([b.get_cells() for b in [block1, block]], scale=10)
            self.assertTrue(block1.is_overlapping(block),
                            "Block {} found not to be overlapping! Joint cells:{}".format(i, str(block.get_cells() & block1.get_cells())))

        if DISPLAY:
            display([b.render() for b in [block1] + overlapping_blocks])

        #Non- Overlapping
        not_overlapping_blocks = []
        not_overlapping_blocks.append(Block(block_mesh, (0, 0, 0), (30, 0, 0)))     # 0
        not_overlapping_blocks.append(Block(block_mesh, (0, 0, 0), (0, 0, 10)))     # 1
        not_overlapping_blocks.append(Block(block_mesh, (0, 0, 0), (0, 0, 5)))      # 2
        not_overlapping_blocks.append(Block(block_mesh, (90, 90, 0),(0, 0, 2)))     # 3


        for i, block in enumerate(not_overlapping_blocks):
            if DISPLAY:
                display([b.render() for b in [block1, block]])
                display_multiple_cells([b.get_cells() for b in [block1, block]], scale=10)
            self.assertTrue(not block1.is_overlapping(block),
                            "Block {} found to be overlapping!\n Joint cells:{}".format(i, str(block.get_cells() & block1.get_cells())))

        if DISPLAY:
            display([b.render() for b in [block1] + not_overlapping_blocks])

    def test_orientation(self):
        block1 = Block(block_mesh, (0,  0, 0), (0, 0, 0))
        block2 = Block(block_mesh, 'short_wide', (0, 0, 0))
        block3 = Block(block_mesh, ORIENTATION.SHORT_WIDE, (0, 0, 0))
        self.assertEqual(block1.get_cells(), block2.get_cells())
        self.assertEqual(block1.get_cells(), block3.get_cells())

        block1 = Block(block_mesh, (90,  0, 0), (0, 0, 0))
        block2 = Block(block_mesh, 'tall_wide', (0, 0, 0))
        block3 = Block(block_mesh, ORIENTATION.TALL_WIDE, (0, 0, 0))
        self.assertEqual(block1.get_cells(), block2.get_cells())
        self.assertEqual(block1.get_cells(), block3.get_cells())

    def test_cells(self):
        blocks = []
        for i, orientation in enumerate(ORIENTATIONS):
            blocks.append(Block(block_mesh, orientation, ((-1)**i * i *10, (-1)**(i + 1) * i * 10, 0)))


        if DISPLAY:
            display_multiple_cells([block.get_cells() for block in blocks])

    def test_cover_cells(self):
        blocks = []
        for i, orientation in enumerate(ORIENTATIONS):
            blocks.append(Block(block_mesh, orientation, ((-1)**i * i *5, (-1)**(i + 1) * i * 5, 0)))


        if DISPLAY:
            display_multiple_grids([block.get_cover_cells() for block in blocks])


    def test_mesh(self):
        block1 = Block(block_mesh, (0, 0, 0), ( 0,  0, 0))
        print(block1)
        if DISPLAY:
            display([block1.render()])

    def test_levels(self):
        #same orientation
        orientation = 'tall_wide'
        block1 = Block(block_mesh, orientation, (0, 0, 0))
        block2 = Block(block_mesh, orientation, (2, 1, 0))

        print(block1.get_top_level())
        print(block2.get_top_level())
        self.assertTrue(block1.get_top_level() == block2.get_top_level())

        print(block1.get_bottom_level())
        print(block2.get_bottom_level())
        self.assertTrue(block1.get_bottom_level() == block2.get_bottom_level())

        # differing orientations
        block1 = Block(block_mesh, 'flat_wide', ( 0,  0, 0))
        block2 = Block(block_mesh, 'tall_thin', ( 5, 3, -7))

        print(block1.get_top_level())
        print(block2.get_top_level())
        self.assertTrue(block1.get_top_level() == block2.get_top_level())

        print(block1.get_bottom_level())
        print(block2.get_bottom_level())
        self.assertTrue(block1.get_bottom_level() > block2.get_bottom_level())

    def test_hash(self):
        block1 = Block(block_mesh, (0, 0, 0), (0, 0, 0))
        block2 = Block(block_mesh, (0, 0, 0), (0, 0, 0))
        self.assertEqual(hash(block1), hash(block2))

        blocks = [Block(block_mesh, (0, 0, 0), (0, 0, 0)) for _ in range(10)]
        for block1 in blocks:
            for block2 in blocks:
                self.assertEqual(hash(block1), hash(block2))

        blocks = [Block(block_mesh, (0, 0, 0), (0, 0, 0)) for _ in range(100)]
        for block1 in blocks:
            for block2 in blocks:
                self.assertEqual(hash(block1), hash(block2))

        for orientation in ORIENTATIONS:
            blocks = [Block(block_mesh, orientation, (0, 0, 0)) for _ in range(10)]
            for block1 in blocks:
                for block2 in blocks:
                    self.assertEqual(hash(block1), hash(block2))

        for orientation in ORIENTATIONS:
            blocks_1 = [Block(block_mesh, orientation, (10, 10, 10)) for _ in range(10)]
            blocks_2 = [Block(block_mesh, orientation, (10, 10, 10)) for _ in range(10)]
            for block1 in blocks_1:
                for block2 in blocks_2:
                    self.assertEqual(hash(block1), hash(block2))

    def test_next_block(self):
        # # simple
        block1 = Block(block_mesh, (0, 0, 0), (0, 0, 0))
        sons = [Block(block_mesh, orientation, position)
                    for orientation, position in block1.gen_possible_block_descriptors()]
        print("All : {}".format(len(sons)))
        if DISPLAY:
            display([b.render() for b in sons + [block1] ], scale=15)

        # limit to type of orientation
        block1 = Block(block_mesh, (0, 0, 0), (0, 0, 0))
        for orientation in ORIENTATIONS:
            sons = [Block(block_mesh, orientation, position)
                    for orientation, position in block1.gen_possible_block_descriptors(lambda o: o == orientation)]
            print(orientation + " : {}".format(len(sons)))
            if DISPLAY:
                display([b.render() for b in sons + [block1] ], scale=15)


        # all orientations around 0, 0, 0
        for orientation in ORIENTATIONS:
            block1 = Block(block_mesh, orientation, (0, 0, 0))
            for orientation in ORIENTATIONS:
                sons = [Block(block_mesh, orientation, position)
                        for orientation, position in block1.gen_possible_block_descriptors(lambda o: o == orientation)]
                print(orientation + " : {}".format(len(sons)))

                if DISPLAY:
                    display([b.render() for b in sons + [block1] ], scale=15)

        # all orientations around 1, 1, 0
        for base_orientation in ORIENTATIONS:
            print("Base orientation : {}".format(base_orientation))
            block1 = Block(block_mesh, base_orientation, (1, 1, 0))
            for son_orientation in ORIENTATIONS:
                sons = list(block1.gen_possible_block_descriptors(lambda o: o == son_orientation))
                print("\t" + son_orientation + " : {}".format(len(sons)))

                if DISPLAY:
                    display([b.render() for b in sons + [block1] ], scale=15)

    def test_str_time(self):
        block : Block = Block(block_mesh, (0,0,0), (0,0,0))
        s = time.time()
        r = 3000000
        for i in range(r):
            _ = str(block)
        elapse = time.time() - s
        print("For {}X:\t{}".format(r, elapse))
        # print(block._quick_data)

    def test_hash_time(self):
        block : Block = Block(block_mesh, (0,0,0), (0,0,0))
        s = time.time()
        r = 1000000
        for i in range(r):
            _ = hash(block)
        elapse = time.time() - s
        print("For {}X:\t{}".format(r, elapse))
        print(block.__str__())

    def test_son_desc_time(self):
        result = []
        size = 1000
        ss  = time.time()
        num_of_desc = 0
        for orientation in ORIENTATIONS:
            blocks = [Block(block_mesh, orientation, (i, i, 0)) for i in range(size)]
            # block1 = Block(block_mesh, orientation, (0, 0, 0))
            o_time = 0
            for block in blocks:
                s = time.time()
                sons_dsc = list(block.gen_possible_block_descriptors())
                o_time += time.time() - s
                num_of_desc += len(sons_dsc)
            result.append((orientation, o_time/size))
        ee = time.time() - ss
        print("Time to spawn {} descriptors: {}".format(num_of_desc, ee))
        pp(result)

    def test_spawn_block_time(self):
        size = 10
        all_desc = []
        for orientation in ORIENTATIONS:
            blocks = [Block(block_mesh, orientation, (i, i, 0)) for i in range(size)]
            o_time = 0
            for block in blocks:
                all_desc += list(block.gen_possible_block_descriptors())
        ss = time.time()
        for desc in all_desc:
            b = Block(block_mesh, desc[0], desc[1])
        ee = time.time() - ss
        print("Time to spawn {} Blocks: {}".format(len(all_desc), ee))

    def test_inertia(self):
        block1 = Block(block_mesh, (0,0,0,), (0,0,0))
        pp(block1.render().get_mass_properties())
        blocks = []
        for orientation in ORIENTATIONS:
            block1 = Block(block_mesh, orientation, (0, 0, 0))
            print(orientation)
            pp(block1.render().get_mass_properties())
            blocks.append(block1)

        m = combine([b.render() for b in blocks])
        print("all")
        pp(m.get_mass_properties())

        # inertia of tall tower
        blocks = [Block(block_mesh, 'tall_thin', (0, 0, i*15)) for i in range(1)]
        m  = combine([b.render() for b in blocks])
        print("Tall tower")
        pp(m.get_mass_properties())
        if DISPLAY:
            display([m])

        # inertia of wide (Y) tower
        blocks = [Block(block_mesh, 'short_thin', (i*15, 0, 0)) for i in range(10)]
        m  = combine([b.render() for b in blocks])
        print("inertia of wide (Y) tower")
        pp(m.get_mass_properties())
        if DISPLAY:
            display([m])

        # inertia of T shape tower
        blocks = [Block(block_mesh, 'short_thin', (0, 0, 0))] + \
                [Block(block_mesh, 'flat_wide', (i, 0, 2)) for i in range(-5, 5)]

        m  = combine([b.render() for b in blocks])
        print("inertia of T shape tower")
        pp(m.get_mass_properties())
        if DISPLAY:
            display([m])




class Floor_Tests(TestCase):

    def test_constructor(self):
        floor = Floor(floor_mesh)
        if DISPLAY:
            display([floor.render()])

        block1 = Block(block_mesh, (0, 0, 0), (0, 0, 0))
        if DISPLAY:
            display_colored([floor.render(), block1.render()], [to_rgba((0.1, 0.1, 0.1), 0.001 ), 'b'])


class Ring_Floor_Tests(TestCase):

    def test_constructor(self):
        floor = RingFloor(floor_mesh)
        if DISPLAY:
            display([floor.render()])

        block1 = Block(block_mesh, (0, 0, 0), (0, 0, 0))
        if DISPLAY:
            display_colored([floor.render(), block1.render()], [to_rgba((0.1, 0.1, 0.1), 0.001 ), 'b'])

    def test_sons(self):
        floor = RingFloor(floor_mesh, size=50)
        if DISPLAY:
            display([floor.render()])

        blocks = [Block(block_mesh, *d) for d in floor.gen_possible_block_descriptors()]
        some = sample(blocks, 100)
        if DISPLAY:
            display([b.render() for b in some])

    def test_perp_sons(self):
        floor = RingFloor(floor_mesh, size=50)

        blocks = [Block(block_mesh, *d) for d in floor.gen_possible_block_descriptors(
            limit_orientation=lambda o: floor.is_perpendicular(o))]
        some = sample(blocks, 100)
        print (floor.orientation)
        print (floor.is_perpendicular(floor))
        if DISPLAY:
            display([b.render() for b in some + [floor]])

    def test_multiring(self):
        floor = RingFloor(floor_mesh, size=100, number_of_rings=2, ring_size=4, distance_between_rings=15)
        if DISPLAY:
            display_cells(floor.get_cells())
            # display([floor.render()])




