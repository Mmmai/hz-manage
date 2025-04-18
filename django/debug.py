import os
aaa = [
    {"name":8,'children':[{"name":9,'children':[{"name":10,'children':[{"name":11}]}]}]},

    {"name":1,'children':[{"name":2}]},
    {"name":3,'children':[{"name":4}]},
    {"name":5,'children':[{"name":6,'children':[{"name":7}]}]},

]
bbb = []
def test(aaa,bbb,ccc=''):
    for i in aaa:
        print(i)
        parent = str(ccc)+str(i["name"])
        if 'children' in i.keys():
            test(i['children'],bbb,parent)
        else:
            print(i)
            bbb.append({"path":parent})
            # print(bbb)
test(aaa,bbb)
print(bbb)