from deserialize_tree import DeserializeTree
from  post_id import *


if __name__ == "__main__":
    filename = get_file(POST2)
    tree_obj = DeserializeTree()
    tree_json = tree_obj.load_file(filename)
    tree = tree_obj.load_tree(tree_json)
    tree.show()













