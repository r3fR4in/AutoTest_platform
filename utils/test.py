import ast
import json

s = "{'a':[{'b':1}]}"
print(s)
print(type(s))
d = ast.literal_eval(s)
print(d)
print(type(d))
j = json.dumps(d)
print(j)
print(type(j))
