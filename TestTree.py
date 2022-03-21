import unittest
from Tree import BPTree


class TestTreeMethods(unittest.TestCase):

    def test_tree(self):
        tree = BPTree.from_dict(
            {"Resources": {"RUS": {"obj1": {"lbl": "Window"}, "obj2": "disgusting"}, "ENU": {"obj1": {"lbl": "Окно"}},
                           "obj1": {"title": "hello"}}})
        # tree.print()
        self.assertEqual(4, tree.h)

    def test_join(self):
        tree1 = BPTree.from_dict(
            {"Resources":
             {
                 "RUS": {
                     "obj1": {"lbl": "Window"}
                 },
                 "ENU": {
                     "obj1": {"lbl": "Окно"}
                 }
             }
             }
        )
        # tree1.print()
        # print(tree1)
        d1 = tree1.to_dict()
        # print(d1)
        tree2 = BPTree.from_dict(
            {"Resources":
             {
                 "UKR": {
                     "obj1": {"lbl": "Вiкно"}
                 }
             }
             }
        )
        # print(tree2)
        d2 = tree2.to_dict()
        # print(d2)
        tree = BPTree.left_join(tree1, tree2)
        d = tree.to_dict()
        # print(d)
        self.assertEqual(
            d,
            {
                'Resources': {
                    'RUS': {'obj1': {'lbl': 'Window'}},
                    'ENU': {'obj1': {'lbl': 'Окно'}},
                    'UKR': {'obj1': {'lbl': 'Вiкно'}}}
            }
        )

    def test_delete(self):
        tree = BPTree.from_dict(
            {"Resources": {"RUS": {"obj1": {"lbl": "Window"}, "obj2": "disgusting"}, "ENU": {"obj1": {"lbl": "Окно"}},
                           "obj1": {"title": "hello"}}})
        # tree.print()
        tree.key_delete("RUS")
        tree.key_delete("ENU")
        # tree.print()
        d = tree.to_dict()
        # print(d)
        self.assertDictEqual(d,
                             {
                                 "Resources": {
                                     "obj2": "disgusting",
                                     "obj1": {
                                         "title": "hello",
                                         "lbl": ['Window', 'Окно']
                                     }
                                 }
                             })

    def test_unhashable_types_in_leaves(self):
        d = {
            "Resources": {
                "obj2": "disgusting",
                "obj1": {
                    "title": "hello",
                    "lbl": set("123")  # set is not hashable
                }
            }
        }
        self.assertRaises(TypeError, BPTree.from_dict, d)
