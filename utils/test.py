import hashlib
data = 'a123456'
m = hashlib.md5()
b = data.encode('utf-8')
m.update(b)
str_md5 = m.hexdigest()
print(str_md5)
