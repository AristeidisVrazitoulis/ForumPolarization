from deserialize_tree import load_file, load_tree



filename = "tree_xdb9dj.json"
tree_json = load_file(filename)
tree = load_tree(tree_json)
tree.show()













