

# Create your tests here.
aaa = 1714265293761
print(len(str(aaa)))
print(111)
bbb = "2024-04-28T08:39:55.67946754Z"
import datetime

print(type(datetime.datetime.fromisoformat(bbb[:23])))
sss = 1715330022631344025
timetamp = datetime.datetime.fromtimestamp(sss/(1* 10**9))
print(type(timetamp))