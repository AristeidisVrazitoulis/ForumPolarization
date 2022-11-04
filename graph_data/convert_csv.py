'''
Converts edge list to csv file for the gephi software
'''

theme = "vaxx"
filename = f"{theme}_undirected.txt"

first_line = "Source Target\n"
final_content = ""
with open(filename, "r") as f1, open("gephi_format/"+theme+"_gephi.csv", "w") as f2:
    content = f1.read()
    final_content = first_line+content
    f2.write(final_content)


