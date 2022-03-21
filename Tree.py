from ApcLogger import getLogger


class BPTree:
    """implementation of B+Tree.

    узел - словарь, листья - словари, где все ключи имеют значения None
    """
    logger = getLogger(name="BPTree")

    def __init__(self):
        self.children = dict()
        self.parent = [None, None]
        self._h = None

    def _get_h(self):
        def calc_h(root):
            r = 0
            if not root.is_leaf():
                for k in root.children:
                    if root.children[k]:
                        h = calc_h(root.children[k]) + 1
                        if h >= r:
                            r = h
            root._h = r
            return root._h

        if self._h is None:
            self._h = calc_h(self)
        return self._h

    def get_root(self):
        return self if not self.parent[0] else self.parent[0].get_root()

    def key_insert(self, where: str, key: str, value: dict = None):
        if where == self.parent[1]:
            if value:
                value = BPTree.from_dict(value)
                value.parent[1] = key
                value.parent[0] = self
            self.children[key] = value
        elif where in self.children:
            if not self.children[where]:  # if 'self' - leaf
                self.children[key] = BPTree.from_dict({where: value})
                self.children[key].parent = key
                self.children.pop(where)
        else:
            for k in self.children:
                if self.children[k]:  # insert in children not leaves
                    self.children[k].key_insert(where, key)

    def node_delete(self, key: str):
        if key in self.children:
            self.children.pop(key)
        else:  # check for key in children
            for child in self.children:
                if self.children[child]:  # search in children not leaves
                    self.children[child].key_delete(key)

    def key_delete(self, key):
        if key in self.children:
            if not self.children[key]:  # self - leaf
                self.children.pop(key)
            else:
                child = self.children.pop(key)
                self.left_join(self, child)
        else:  # check for key in children
            for child in self.children:
                if self.children[child]:  # search in children not leaves
                    self.children[child].key_delete(key)

    @staticmethod
    def left_join(t_l, t_r):
        for key in t_r.children:
            child_t_r = t_r.children[key]
            if key in t_l.children:  # same key in t_l and in t_r
                child_t_l = t_l.children[key]
                if child_t_l and child_t_r:  # not leaves
                    t_l.children[key] = BPTree.left_join(child_t_l, child_t_r)
                elif child_t_r:  # child_t_r is not a leaf
                    child_t_r.parent = [t_l, key]
                    t_l.children[key] = child_t_r
            else:  # only in t_r - add to t_l
                if child_t_r:
                    child_t_r.parent = [t_l, key]
                t_l.children.update({key: child_t_r})
        return t_l

    def print(self, indent=0):
        for k in self.children:
            if self.children[k]:
                print(" " * indent + k)
                self.children[k].print(indent + 2)
            else:
                print(" " * indent + k)

    def __str__(self, indent=0):
        s = ""
        for k in self.children:
            if self.children[k]:
                s += "\n" + " " * indent + f"subtree: '{k}' {self.children[k].parent}"
                s += self.children[k].__str__(indent + 2)
            else:
                s += "\n" + " " * indent + f"leaf: '{k}'"
        return s

    # def __repr__(self, indent=0):
    #     s = ""
    #     for k in self.children:
    #         if self.children[k]:
    #             s += "\n" + " " * indent + f"subtree: '{k}' {self.children[k].parent}"
    #             s += self.children[k].__repr__(indent + 2)
    #         else:
    #             s += "\n" + " " * indent + f"leaf: '{k}'"
    #     return s

    def to_dict(self):
        d = dict()
        if not self.is_leaf():
            self.logger.debug(f"subtree children: {self.children}")
            for k in self.children:
                if self.children[k]:  # tree child
                    d.update({k: self.children[k].to_dict()})
                else:  # leaf child
                    d.update({k: None})

        else:
            self.logger.debug(f"Leaf, children: {self.children}")
            len_children = len(self.children)
            if len_children > 1:
                d = [k for k in self.children]
            elif len_children == 1:
                for k in self.children:
                    d = k
            else:
                d = dict()
        return d

    @staticmethod
    def from_dict(d: dict):
        tree = BPTree()
        if isinstance(d, dict):
            for k in d:
                t = BPTree.from_dict(d[k])
                t.parent = [tree, k]
                tree.children[k] = t
        elif isinstance(d, list):
            for k in d:
                tree.children[k] = None
        else:
            tree.children[d] = None
        return tree

    def is_leaf(self):
        return not any(self.children.values())

    root = property(fget=get_root)
    h = property(fget=_get_h)


if __name__ == "__main__":
    tree = BPTree.from_dict({"Resources": {"RUS": {"lol": "sdfsdf", "Einstein": "disgusting"}, "ENU": {"lol": "fuck"},
                                           "lol": {"mama": "hello"}}})
    tree.key_delete("RUS")
    tree.key_delete("ENU")
    print(tree)
    d = tree.to_dict()
    print("высота:", tree.h)
