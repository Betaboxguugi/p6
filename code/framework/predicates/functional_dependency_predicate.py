from .predicate import Predicate
from .report import Report

__author__ = 'Alexander Brandborg'
__maintainer__ = 'Mikael Vind Mikkelsen'


class FunctionalDependencyPredicate(Predicate):
    """ Predicate that can check if a table or a join of tables holds a certain
    functional dependency.
    """
    def __init__(self, tables, attributes, dependent_attributes):
        """
        :param tables: tables from the database, which we wish to join
        :param attributes: attributes which are depended upon by other
        attributes. Given as either a single attribute name, or a tuple of
        attribute names.
        :param dependent_attributes: attributes which are functionally
        dependent on the former attributes. Given as either a single attribute
        name, or a tuple of attribute names.
        Example:
        attributes = ('a','b') and dependent_attributes = 'c'
        corresponds to the functional dependency: a, b -> c
        """
        self.tables = tables
        self.attributes = attributes
        self.dependent_attributes = dependent_attributes
        self.results = True

    def run(self, dw_rep):
        """
        :param dw_rep: a DWRepresentation object
        Checks whether each function dependency holds.
        """

        # SQL setup for the tables specified
        if len(self.tables) == 1 or isinstance(self.tables, str):
            join_sql = "{} as t1 , {} as t2".format(self.tables[0],
                                                    self.tables[0])
        else:
            joined_sql = " NATURAL JOIN ".join(self.tables)
            join_sql = "({}) as t1 , ({}) as t2".format(joined_sql, joined_sql)

        # Determining our dependencies, where alpha is the left side and beta
        # the right side of the dependency (alpha --> beta)
        alpha = self.attributes
        beta = self.dependent_attributes

        # SQL setup for first part of SELECT, which are the left side of
        # the dependencies
        select_alpha_sql_generator = (" t1.{} ".format(alpha[x])
                                      for x in range(0, len(alpha)))
        if len(alpha) == 1 or isinstance(alpha, str):
            select_sql_alpha = "t1.{}".format(alpha)
        else:
            select_sql_alpha = ",".join(select_alpha_sql_generator)

        # SQL setup for second part of SELECT, which are the right side of
        # the dependencies
        select_beta_sql_generator = (" t1.{} ".format(beta[x])
                                     for x in range(0, len(beta)))
        if len(beta) == 1 or isinstance(beta, str):
            select_sql_beta = "t1.{}".format(beta)
        else:
            select_sql_beta = ",".join(select_beta_sql_generator)

        # SQL setup for the whole SELECT portion. Used to only show relevant
        # columns when reporting to the user.
        select_sql = select_sql_alpha + " ," + select_sql_beta

        # SQL setup for the left side of the dependency
        alpha_sql_generator = (" t1.{} = t2.{} ".format(alpha[x], alpha[x])
                               for x in range(0, len(alpha)))
        if len(alpha) == 1 or isinstance(alpha, str):
            and_alpha = " t1.{} = t2.{} ".format(alpha, alpha)
        else:
            and_alpha = ' AND '.join(alpha_sql_generator)

        # SQL setup for the right side of the dependency
        beta_sql_generator = (" (t1.{} <> t2.{}) ".format(beta[x], beta[x])
                              for x in range(0, len(beta)))
        if len(beta) == 1 or isinstance(beta, str):
            or_beta = " (t1.{} <> t2.{}) ".format(beta, beta)
        else:
            or_beta = ' OR '.join(beta_sql_generator)

        # Final setup of the entire SQL command
        lookup_sql = "SELECT " + select_sql + " FROM " + join_sql +\
                     " WHERE " + and_alpha + " AND " + "( {} )".format(or_beta)

        func_dep = "{} --> {}".format(alpha, beta)
        print(lookup_sql)
        c = dw_rep.connection.cursor()
        c.execute(lookup_sql)
        elements = set()

        # If the SQL command returns rows that fail against the dependency if
        # any.
        for row in c.fetchall():
            elements.add(row)
            self.results = False

        return Report(result=self.results,
                      elements=elements,
                      tables=self.tables,
                      predicate=self,
                      msg='The predicate failed for the functional '
                          'dependency "{}" \n'
                          ' |  It did not hold on the following elements:'.
                      format(func_dep))
