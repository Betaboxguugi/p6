__author__ = 'Mikael Vind Mikkelsen'
__maintainer__ = 'Mikael Vind Mikkelsen'


# IMPORTS
import sqlite3
import test_predicates.t_predicate

test_parent = test_predicates.t_predicate.TPredicate
conn = sqlite3.connect('test.db')



class column_has_null(test_parent):

    def __init__(self):
        self.column_name = ''
        self.table_name = ''

    def run(self, table_name, column_name):
        """
        :param table_name: name of the table that should be tested
        :param column_name: name of the column which need to be tested
        """
        c.execute("SELECT {} FROM {} ORDER BY {}".format(self.column_name, self.table_name, self.column_name))
        cc = c.fetchall()
        column_length = len(cc)
        if cc[0][0] is None:
            #return true
        elif cc[column_length-1][0] is None:
            #return true
        else:
            #return false


