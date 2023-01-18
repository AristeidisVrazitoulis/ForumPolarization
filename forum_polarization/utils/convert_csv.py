'''
Converts edge list to csv file for the gephi software
'''

theme = "conspiracy0_top_modified_space_top_modified"



filename = f"{theme}.txt"
source_path = f"../preprocessing/graph_data/modified_graphs/{filename}"
target_path = f"../preprocessing/graph_data/gephi_format/{theme}_gephi.csv"


first_line = "Source Target Weight\n"
final_content = ""
with open(source_path, "r") as f1, open(target_path, "w") as f2:
    content = f1.read()
    final_content = first_line+content
    f2.write(final_content)








