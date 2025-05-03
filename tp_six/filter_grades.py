from cassandra.cluster import Cluster

# الاتصال على localhost والبورت 9043 (وليس 9042)
cluster = Cluster(['127.0.0.1'], port=9043)
session = cluster.connect('resto_ny')

# الاستعلام
query = "SELECT grade, score FROM Inspection WHERE score > 30 ALLOW FILTERING;"
rows = session.execute(query)

# استخراج الدرجات غير الفارغة فقط
grades = set()
for row in rows:
    if row.grade:
        grades.add(row.grade)

print("الدرجات غير الفارغة التي score > 30:")
for grade in sorted(grades):
    print("-", grade)
