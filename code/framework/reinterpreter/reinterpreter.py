import ast
import collections
from .transform_visitor import TransformVisitor
from .extract_visitor import ExtractVisitor
from .representation_maker import RepresentationMaker

__author__ = 'Mathias Claus Jensen'
__all__ = ['Reinterpreter']


class Reinterpreter(object):
    """ Class in charge of reinterpreting a pygrametl program, using different
    connections.
    """

    def __init__(self, program, source_conns, dw_conn, program_is_path=False):
        """ 
        :param program: A string containing the program that is to be 
        reinterpreted or a path to it.
        :conn_scope: A dictionary of string:connection pairs. Used to specify
        which connections should be used in the program. The dictionary must be
        ordered in the occurence of use in the program, and there has to be as
        many connections in the dictionary as there are used in the program
        :param program_is_path: Boolean that specifies if the program string is 
        the actual program or a path to a file containing the program.
        """

        self.program = program
        self.dw_conn = dw_conn
        self.conn_scope = source_conns
        self.program_is_path = program_is_path

        self.dw_id = '__0__'
        self.source_ids = []
        for entry in source_conns:
            self.source_ids.append("__" + str(source_conns.index(entry) + 1) +
                                   "__")

        self.varname = 'extract_src_dict'

    def __transform(self, node):
        """ Swaps out the connections in the old program, with the ones given.
        """
        tv = TransformVisitor(self.source_ids, self.dw_id)
        tv.start(node)

    def __extract(self, node):
        """ Makes and extracts DataSource objects for each dimension/facttable
        in the program.
        :param: Root node of AST
        :return: An AST node that represents a dictionary containing all the 
        dimension/facttable datasources. 
        """
        ev = ExtractVisitor(self.varname)
        return ev.start(node)

    def __compile_exec(self, node, gscope=None, lscope=None):
        """ Compiles and executes an AST node
        """
        p = compile(source=node, filename='<string>', mode='exec')
        exec(p, gscope, lscope)

    def run(self):
        """ Reinterpretes the pygrametl program, returns a dict containing 
        :return: A dictionary with all the dimension/facttable datasources.
        """
        scope = self.conn_scope.copy()
        program = ''
        if self.program_is_path:
            with open(self.program, 'r') as f:
                program = f.read()
        else:
            program = self.program

        tree = ast.parse(program) # Parsing the pygrametl program to an AST

        self.__transform(tree)  # Transforming the AST to include the user defined connections
        self.__compile_exec(node=tree, gscope=None, lscope=scope)  # Executing the transformed AST

        RepresentationMaker()

        src_module = self.__extract(tree)  # Creating a new AST for extracting DW tables
        self.__compile_exec(node=src_module, gscope=None, lscope=scope)  # Executing executing extract AST

        # The extract AST extends the scope to include source objects for all DW tables.
        # This is returned here for the user to test upon.
        return scope[self.varname]
