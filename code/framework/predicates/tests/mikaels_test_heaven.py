_author__ = 'Mikael Vind Mikkelsen'
__maintainer__ = 'Mikael Vind Mikkelsen'

# Imports
import sqlite3
from framework.predicates.column_not_null_predicate import ColumnNotNullPredicate
from framework.predicates.rule_row_predicate import RuleRowPredicate
from framework.predicates.rule_predicate import RulePredicate
from framework.predicates.no_duplicate_row_predicate import NoDuplicateRowPredicate
from framework.case import Case
from framework.reinterpreter.datawarehouse_representation \
    import DWRepresentation, DimRepresentation, FTRepresentation

"""
table_name1 = 'company'
table_name2 = 'bompany'
column_names1 = 'age'
column_names2 = ['age', 'salary']

def constraint_function1(a):
    if a < 50:
        return True
    else:
        return False

cnnp1 = ColumnNotNullPredicate('company', 'age')
cnnp2 = ColumnNotNullPredicate('company', ['age', 'salary'])
cnnp3 = ColumnNotNullPredicate('bompany', 'salary')
cnnp4 = ColumnNotNullPredicate('bompany', ['address', 'salary'])
rp1 = RulePredicate(table_name1, constraint_function1, column_names1)
rp2 = RulePredicate(table_name1, constraint_function1, None, column_names1)
rrp1 = RuleRowPredicate(table_name1, column_names1, constraint_function1)

ukp1 = UniqueKeyPredicate(table_name1, column_names2)
ndrp1 = NoDuplicateRowPredicate(table_name1, column_names2)
ndrp2 = NoDuplicateRowPredicate(table_name1, column_names2, True)

pAll = [cnnp1, cnnp2, cnnp3, cnnp4, rp1, rp2, rrp1, ukp1, ndrp1, ndrp2]

pl = [ukp1, ndrp1, ndrp2]
"""
# Case(None, None, pl, None)

csv_name = './region.csv'
dw_name = './dw.db'  # The one found in pygrametl_examples
dw_conn = sqlite3.connect(dw_name)

query1 = "SELECT * FROM bookDim WHERE bookid < 3"
query2 = "SELECT * FROM timeDim"
query3 = "SELECT * FROM locationDim"
query4 = "SELECT * FROM factTable WHERE bookid > 1"
book_dim = DimRepresentation('bookDim', 'bookid', ['book', 'genre'], dw_conn)

time_dim = DimRepresentation('timeDim', 'timeid', ['day', 'month', 'year'],
                             dw_conn)

location_dim = DimRepresentation('locationDim', 'locationid',
                                 ['city', 'region'], dw_conn, ['city'])

facttable = FTRepresentation('factTable', ['bookid', 'locationid', 'timeid'],
                             dw_conn, ['sale'])
"""
book_dim.query = query1
time_dim.query = query2
location_dim.query = query3
facttable.query = query4
"""

dw = DWRepresentation([book_dim, time_dim, location_dim], [facttable], dw_conn)

ref_tester1 = NoDuplicateRowPredicate('bookdim', ['genre', 'book'], False)
ref_tester2 = NoDuplicateRowPredicate('bookdim', None, True)
ref_tester3 = NoDuplicateRowPredicate('bookdim')


print(ref_tester1.run(dw))
print(ref_tester2.run(dw))
print(ref_tester3.run(dw))















# Eksempel på brug af itercolumns taget fra ColumnNotNullPredicate før det
# viste sig at være forkert at bruge der.
"""
 for e in dw_rep.get_data_representation(self.table_name).\
         itercolumns(self.column_names):
     print(e, ' ', row_counter)
     for key, value in e.items():
         if not value:
             self.__result__ = False
             self.rows_with_null.append(row_counter)
         print(key, value)
     row_counter += 1
 """