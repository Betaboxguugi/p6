__author__ = 'Mathias Claus Jensen & Alexander Brandborg'


class DWRepresentation(object):
    """
    Class used to represent an entire DW.
    Allows for access to specific tables simply through their name.
    """

    def __init__(self, dims, fts, connection):
        """
        :param dims: A list of DimensionRepresentation Objects
        :param fts: A lost of FTRepresentation Objects
        :param connection: A PEP 249 connection to a database
        """

        try:
            self.dims = dims
            self.fts = fts
            self.connection = connection

            # Turns all our names to lower case as SQL is case insensitive
            # Also collects a list of names for a later check
            name_list = []
            self.rep = self.dims + self.fts
            for entry in self.rep:
                low = entry.name.lower()
                entry.name = low
                name_list.append(low)

            # Makes sure that no two tables have the same name. Else we raise an exception.
            if len(name_list) != len(list(set(name_list))):
                raise ValueError("Table names are not unique")

            # Fills the up our dictionary with tables keyed by their names.
            self.tabledict = {}
            for entry in self.rep:
                self.tabledict[entry.name] = entry

        finally:
            try:
                pass
            except Exception:
                pass

    def __str__(self):
        return self.tabledict.__str__()

    def __repr__(self):
        return self.__str__()

    def get_data_representation(self, name):
        """
        :param name: Name of the requested table
        :return: A TableRepresentation Object corresponding to the name
        """
        return self.tabledict[name.lower()]


class TableRepresentation(object):
    """
    Super class for representing tables in a DW
    """

    def __iter__(self):
        """
        :return: A generator for iterating over the contents of the table
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(self.query)
            names = [t[0] for t in cursor.description]

            while True:
                data = cursor.fetchmany(500)
                # Some cursor.description return null if the cursor hasn't fetched.
                # Thus we call it again after fetch if this is the case.
                if not names:
                    names = [t[0] for t in cursor.description]
                if not data:
                    break
                # Checks that the entries have the correct amount of attributes
                if len(names) != len(data[0]):
                    raise ValueError(
                        "Incorrect number of names provided. " +
                        "%d given, %d needed." % (len(names), len(data[0])))
                for row in data:
                    yield dict(zip(names, row))
        finally:
            try:
                cursor.close()
            except Exception:
                pass

    def itercolumns(self, column_names):
        """
        Lets us fetch only a subset of columns from the table
        :param column_names: The subset of columns of interest
        :return: A generator for iterating over the contents of the table
        """
        for data in self.__iter__():
            result = {}
            for name in column_names:
                result.update({name: data[name]})
            yield result


class DimRepresentation(TableRepresentation):
    """
    An object for representing data in a DW dimension
    """
    def __init__(self, name, key, attributes, connection, lookupatts=None):
        """
        :param name: Name of table
        :param key: Name of primary key attribute
        :param attributes: List of non-lookup attributes of the table
        :param lookupatts: List of lookup attributes of the table
        :param connection: PEP249 connection to a database
        :param query: SQL query used for fetching contents of the table
        """
        self.name = name
        self.key = key
        self.attributes = attributes
        if lookupatts:
            self.lookupatts = lookupatts
        else:
            self.lookupatts = self.attributes
        self.connection = connection
        self.all = [self.key] + self.attributes + self.lookupatts
        self.query = "SELECT " + ",".join(self.all) + " FROM " + self.name

    def __str__(self):
        row_list = []
        for row in self.itercolumns(self.all):
            row_list.append(row)
        text = "{} {}".format(self.name, row_list)
        return text

    def __repr__(self):
        return self.__str__()


class FTRepresentation(TableRepresentation):
    """
    An Object for representing data in a DW fact table
    """
    def __init__(self, name, keyrefs, measures, connection):
        """
        :param name: Name of table
        :param keyrefs: List of attributes that are foreign keys to other tables
        :param measures: List of attributes containing non-key values
        :param connection: PEP249 connection to a database
        :param query: SQL query used for fetching contents of the table
        """
        self.name = name
        self.keyrefs = keyrefs
        self.measures = measures
        self.connection = connection
        self.all = self.keyrefs + self.measures
        self.query = "SELECT " + ",".join(self.all) + " FROM " + self.name

    def __str__(self):
        row_list = []
        for gen in self.itercolumns(self.all):
            row_list.append(gen)
        text = "{} {}".format(self.name, row_list)
        return text

    def __repr__(self):
        return self.__str__()
