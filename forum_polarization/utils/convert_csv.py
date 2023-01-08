'''
Converts edge list to csv file for the gephi software
'''

theme = "lgbt_top_Conservative_top"



filename = f"{theme}.txt"
path = "../preprocessing/graph_data/"
source_path = path+f"{filename}"
target_path = path+f"gephi_format/{theme}_gephi.csv"


first_line = "Source Target Weight\n"
final_content = ""
with open(source_path, "r") as f1, open(target_path, "w") as f2:
    content = f1.read()
    final_content = first_line+content
    f2.write(final_content)








