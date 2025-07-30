# test no partial imported, vs user defined partial, key, 
# redefining functions

#FIXME already jitted functions preprocess needs to be done
# FIXME we also need to solve the classes problem
    # init, object construction
    # objects
# (note that jax allows for nnx.Objects classes to be constructed inside jit code)
# annoyances:
# key_arg_name is at good name?

# FIXME even if the user manually sets the keys, we still are modifying
# the function to accept a key argument (as long there is a jaxpy random function),
# and still generating new key values,
# not super eficient, is it worth the change? (benchmarking)

"""
Approach 3.2.1
we are going to use partials for functions of interest,
but also locally reassign and replace all functions of interest names
    with new names

Example
def f():
    a = f2 if something else interest_f
    return a()

# this becomes
def f(key=None):
    new_name = partial(interest_f,key_arg = key)
    a = f2 if something else new_name
    return a()

To allow working with redefinitions of functions and variables, 
we need to realize this only happens on the main funcdef scope.
And that nodeDefs in main function (local variables) can be jit-compiled
on inner nodeDefs, without passing keyword arguments.
This approach should work for all python weird dynamic shenanigans.

3.2.1 change
+ if we modify a function that is in a module, how does it work?
well we compile a new function on that scope. Then we have this new 
function that could be used in other places.
The simplest approach is to create a new variable on the scope
of the upper variable, and use the new name in the modified function

warning nao sei como isto funciona com class methods...
-> penso que existe solucao mas
1. nao deve ser possivel criar classes dentro de jit code
2. we need to preprocess all class args before going to function
(a ideia e' q provavelmente e' registar rng no init, como rng e' global
em principio muda em todo o lado? uma ideia)

question 2:
what if 2 full names represent the same function?
-> the function id will give the same modified function, we will
just also create another variable on the scope (is okay i think)

Basically this means:
1. We only need to modify the main function definition
2. The key argument must be unique from all existent names
in the tree
3. we need to track all names in tree
4. we need detect initial attribute node, assign parent node to it
(simple previous node variable), process full name, set it as full_name on 
node, check if we already processed this node if not process full name (to check if callable and global scope) 
    4.1 if global scope and function of interest, put node on 
local_replace_function set (also if already processed)
5. after we process tree, set functiondef with new key argument,
add assignment nodes that replace function names with partials, 
go to all nodes in local_replace_function set, go to parent,
and replace name with replaced name

Implementation details:
+ To get all names in tree, we need to traverse the entire graph 
first. On the second traversal we only need a few nodes, so we 
can actually just same the important nodes to edit later
+ So in first traversal, what variables should we track?
    + first functiondef node, this will be the main function
    + all used names (not attribute, just names) in the tree

+ create a visit method that before calling generic_visit,
sets self.parent = node before visiting children
    
+ if name node, always add name to the set of names 
    (this encompasses) all names including calls, etc.
    + also do other part of attr node logic

+ if attr node, create mutex like thing, that 
sets true if inside_attr_chain. If name node just run follow thing
    + if inside_attr_chain is True, then do nothing/add name
    + if inside_attr_chain is False, then
        process full name, then check if in full_name_to_node_dict.keys():
        if not in full_name_to_node_dict.keys(),
            then check full name scope,
            if not in local names (current)
            and is global and callable, 
            (check first if already processed in global_ids_processed)
            if not process callable, do everything, including setting modified
                function in the scope

        if it is function of interest or in full_name_to_node_dict.keys():
            set full_name on node,
            set node.parent = self.parent
            add node to replace_function_node list
            add full_name: node to full_name_to_node_dict (dont re add if already in keys)
            set self.modified = True

+ if functiondef node, not main, add name to the set of names, 
add arguments and keywords also to set of names

Second traversal/ Final Processing:
in the main FunctionDef node, after visiting the entire tree
+ if class.modified is True, then we need to modify the function
+ find a unique key argument name, that is not in the set of names
+ add the key argument to the function definition

+ for each full_name in replace_function_dict:
    + create a new_unique name
    + append to functionDef assignment node with name new_unique_name
    and value replace_function_dict[full_name] (the name/attr node)
    + add full_name: new_unique_name to prev_name_to_new_name_dict
+ for each node in replace_function_node,
    + go to node.parent (fuck where to look???, 
    we need to find object with same id as node, search all attributes?
    seems a good approach with ast.iter_fields(node), gives gen dict attr:value
    do for attr, value, with raise if did not found node)
    + replace object with ast.Name(id=prev_name_to_new_name_dict[node.full_name], ctx=ast.Load())
+ end TransformAstTransformer class
+ finish the process function with the new compiled function

"""

from functools import partial
import uuid
import ast
import inspect
import textwrap

def resolve_attr_chain(node, scopes):
    """
    node: ast.Node
    scopes: (global_scope, local_scope)
    returns: (variable, full_name, if is in local scope)
    """
    if isinstance(node, ast.Name):
        global_scope, local_scope = scopes

        if local_scope and node.id in local_scope:
            return local_scope[node.id], node.id, True
        
        return global_scope.get(node.id), node.id, False
    elif isinstance(node, ast.Attribute):
        base, full_name, is_local = resolve_attr_chain(node.value, scopes)
        if base:
            return getattr(base, node.attr, None), f"{full_name}.{node.attr}", is_local
        
    elif isinstance(node, ast.Call):
        # then we are calling within an attribute
        # like a().b()
        # we will not resolve this #FIXME
        # FIXME we should actually still process the call.....
        """
        Example here there are 2 calls
....
                                value=Call(
                                    func=Attribute(
                                        value=Call(
                                            func=Attribute(
                                                value=Name(id='jp', ctx=Load()),
                                                attr='Rngs',
                                                ctx=Load()),
                                            args=[
                                                Constant(value=20)],
                                            keywords=[]),
                                        attr='get_next',
                                        ctx=Load()),
....
If not processing the attribute (as it is not defined in global scope),
we should process at least the inner for Rngs
        
        """
        return None, None, None
    else:
        raise ValueError(f"Node {node} is not expected, (Name, Attribute or Call expected).")
    return None, full_name, None

def get_all_args(a: ast.arguments):
    args = []
    args += a.args if isinstance(a.args, list) else [a.args]
    args += a.vararg if isinstance(a.vararg, list) else [a.vararg]
    args += a.kwonlyargs if isinstance(a.kwonlyargs, list) else [a.kwonlyargs]
    args += a.kwarg if isinstance(a.kwarg, list) else [a.kwarg]
    return [arg.arg for arg in args if isinstance(arg, ast.arg)]


# preprocess cache
global_ids_processed = {} # stores the info of processed functions, important to retrieve key name
global_id_to_function = {} 




class SomethingTransformer(ast.NodeTransformer):
    """

    """



    def __init__(self, global_scope, local_scope):
        super().__init__()
        self.global_scope = global_scope
        self.local_scope = local_scope
        # FIXME precisamos de arg para saber se tree foi modificada ou nao, mas ja temos o info???
        self.modified = False #?
        # FIXME e saber qual a key name....
        self.info = {} #?

        self._did_we_process_main_funcDef = False
        self._names = set() # set of all names in the tree
        self._replace_function_node_list = []
        self._full_name_to_node_dict = {} # fullname: attr/name node
        self._prev_name_to_new_name_dict = {}
        self._curr_inside_attr_chain = False # mutex to check if we are inside an attr chain
        self.parent_stack = [] # keep track of parent nodes
        self._modified_scope_names = {} # for new functions that require patching, we will store the new names here


    
    def generic_visit(self, node):
        self.parent_stack.append(node)
        new_node = super().generic_visit(node)
        self.parent_stack.pop()
        return new_node

    # def get_unique_key_arg_name(self, func_def_node: ast.FunctionDef):
    #     """
    #     Generate a unique key argument name for the function definition node.
    #     This is used to ensure that the key argument does not conflict with existing arguments.
    #     """
    #     base_name = "key"
    #     existing_names = {arg.arg for arg in func_def_node.args.args}
    #     unique_name = base_name
    #     counter = 1
    #     while unique_name in existing_names:
    #         unique_name = f"{base_name}_{counter}"
    #         counter += 1
    #     return unique_name
    
    def get_unique_name(self, base_name=""):
        unique_name = f"{base_name}_{uuid.uuid4().hex}"
        while unique_name in self._names:
            unique_name = f"{base_name}_{uuid.uuid4().hex}"

        self._names.add(unique_name)
        return unique_name

    def _import_partial_to_scope(self):
        """
        Ensure that the 'partial' function from functools is imported in the scope.
        This is necessary for the compilation stage to work correctly.

        To avoid user defining a variable called 'partial' in the scope,
        we will use a unique name for the partial function.
        """
        unique_partial_name = self.get_unique_name(base_name="partial")
        self.global_scope[unique_partial_name] = partial

        self._partial_name = unique_partial_name



    def visit_FunctionDef(self, node):
        if self._did_we_process_main_funcDef:
            self._names.add(node.name)
            return self.generic_visit(node) # just process the node normally

        # this section will only run on the main function definition
        self._did_we_process_main_funcDef = True 

        # add all scope names to the set of names
        self._names.add(node.name)
        self._names.update(get_all_args(node.args))
        self._names.update(self.global_scope.keys())
        self._names.update(self.local_scope.keys())

        node = self.generic_visit(node)

        if self.modified:
            # then this function definition as functions that require a key argument
            # we start by finding a unique key argument, not used anywhere in the scope/tree
            key_arg_name = self.get_unique_name(base_name="key")

            self.info['key_arg_name'] = key_arg_name # store the key name in the info dict

            # add the key argument to the function definition
            node.args.args.append(ast.arg(arg=key_arg_name, annotation=None))
            node.args.defaults.append(ast.Constant(value=None))  # requires Python 3.8+

            # Ensure 'partial' is available in the scope
            self._import_partial_to_scope()  

            # go through all full names
            for full_name, fname_node in self._full_name_to_node_dict.items():
                # we will create a new local variable in the function
                # that does partial(func, key=key_arg_name.get_next())
                new_unique_name = self.get_unique_name(base_name=full_name.split('.')[-1])


                # should use the new unique name in scope, or previous name?
                if full_name in self._modified_scope_names.keys():
                    func_node = ast.Name(id=self._modified_scope_names[full_name], ctx=ast.Load())
                else:
                    func_node = fname_node # we use the previous attr/name node
    
                key_value_node = ast.Name(id=key_arg_name, ctx=ast.Load())

                if fname_node.jaxpy_random_function:
                    # if it is a jaxpy random function, we should get next key
                    # key() # is the same as key.get_next() 
                    key_value_node = ast.Call(
                        func=key_value_node,
                        args=[],
                        keywords=[]
                    )

                # new_name = partial(func, key=key_arg_name.get_next())
                assignment_node = ast.Assign(
                    targets=[ast.Name(id=new_unique_name, ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Name(id=self._partial_name, ctx=ast.Load()),
                        args=[func_node],
                        keywords=[ast.keyword(arg=fname_node.key_arg_name, value=key_value_node)]
                    )
                )

                # add the assignment node to the function definition
                node.body.insert(0, assignment_node)

                # keep track of the previous name to new name mapping
                self._prev_name_to_new_name_dict[full_name] = new_unique_name
            
            # now we can replace all function references in the tree
            for fname_node in self._replace_function_node_list: # get all name/attr nodes that need to be replaced
                parent = fname_node.parent

                # find the attribute or name node in the parent
                for attr, value in ast.iter_fields(parent):
                    if value is fname_node: 
                        # replace the value with a new Name node with the new unique name
                        setattr(parent, attr, ast.Name(id=self._prev_name_to_new_name_dict[fname_node.full_name], ctx=ast.Load()))
                        break

        return node

    def visit_Name(self, node):
        """
        Visit a Name node and add its id to the set of names.
        If it is an attribute, we will process it later.
        """
        self._names.add(node.id)

        # if we are inside an attr chain, do not process this name
        if self._curr_inside_attr_chain:
            return self.generic_visit(node)

        self._process_node_name(node)

        return self.generic_visit(node)

    def visit_Attribute(self, node):
        if self._curr_inside_attr_chain:
            return self.generic_visit(node)

        # Set the mutex to True, we are now inside an attr chain
        self._curr_inside_attr_chain = True

        self._process_node_name(node)

        node = self.generic_visit(node)

        # After visiting the node, set the mutex back to False
        self._curr_inside_attr_chain = False

        return node



    def _process_node_name(self,node):
        """
        Processes the Attribute or Name node to resolve its full name
        and check if it is a function of interest.
        """
        # Process the full name
        func, full_name, is_local = resolve_attr_chain(node, (self.global_scope, self.local_scope))

        if func is None or not inspect.isfunction(func):
            # FIXME we are not processing classes created inside the function
            # then is a local or not a callable
            return

        # if func in global_id_to_function FIXME
        # Process the called function
        key_arg_name = None
        if hasattr(func, '__jaxpy_random_function__'):
            print(f"Function {func.__name__} is marked as a JAX random function.")
            key_arg_name = 'key' # By default, __jaxpy_random_function__ use key argument

            # This could actually be also a __jaxpy_key_arg_name__ variable if interesting to have
            # but will always need to be a keyword, so that positional argument does set the key
            # and such we can search here directly for keyword arguments

        else:
            # check if we need to process the function
            if id(func) not in global_ids_processed.keys():
                print(f"Processing function {func.__name__}")
                # Processes new tree
                # if function is defined in previous function local scope
                # this means it at same level as the current tree,
                # thus we also need to pass the local scope to process this function
                local_scope = self.local_scope if is_local else {} 
                modified_func, info = preprocess_function(func, local_scope=local_scope)

                # FIXME we should check if is truly modified

                # this new function is not defined in this scope
                # so we need to create a new name not in the scope to use
                # this global value should also not be a functiondef args/keywarg
                # (since we are going to assign to a new variable in the beggining of functiondef, 
                # does not need to be different than follow up variables)

                if id(func) != id(modified_func):
                    # then we have a new function that is not in the scope of this function
                    new_unique_name = self.get_unique_name(base_name=func.__name__)
                    self.global_scope[new_unique_name] = modified_func
                    self._modified_scope_names[full_name] = new_unique_name

            else:
                # already processed just get info
                info = global_ids_processed[id(func)]

                if id(func) in global_id_to_function.keys(): # id(func) != id(modified_func)
                    # then we have a modified function that might not be in the scope
                    if full_name not in self._modified_scope_names.keys():
                        # then the modification is not yet in the scope
                        new_unique_name = self.get_unique_name(base_name=func.__name__)
                        self.global_scope[new_unique_name] = global_id_to_function[id(func)]
                        self._modified_scope_names[full_name] = new_unique_name
                    
                    # otherwise, it is already processed and already in the scope

            if 'key_arg_name' in info:
                # then function was modified to accept a key
                key_arg_name = info['key_arg_name']

        if key_arg_name is not None:
            # add details for future processing
            self._replace_function_node_list.append(node)
            node.parent = self.parent_stack[-1]
            node.full_name = full_name
            node.key_arg_name = key_arg_name 
            node.jaxpy_random_function = hasattr(func, '__jaxpy_random_function__') # either to call .get_next() or not
            self._full_name_to_node_dict[full_name] = node # needed for going through each full_name later
            self.modified = True


# FIXME local_scope, where is going to be used? 1st call should be None?
# this is not a public interface
def preprocess_function(func, local_scope=None):
    """
    FIXME it needs to also change scope with function calls that were modified

    This will also be called everytime we find a function call, while processing the AST.

    returns: 
    + compiled function
    + info dictionary, currently will have key_arg_name if it was added
    """
    # FIXME we probably need more info like key argument name.
    source = inspect.getsource(func)
    dedented_source = textwrap.dedent(source) # remove leading whitespace, specially inside functionDefs
    tree = ast.parse(dedented_source)

    print("Textwrap")
    print(source)
    print(dedented_source)
    # Create a transformer instance
    global_scope = func.__globals__.copy()

    if local_scope is None:
        # this is necessary to obtain local functiondefs from where preprocessed is called
        # WARNING: if used in jit code, this should be done in jit function... not here
        local_scope = inspect.currentframe().f_back.f_locals


    transformer = SomethingTransformer(global_scope, local_scope)

    # Transform the AST
    transformed_tree = transformer.visit(tree)
    ast.fix_missing_locations(transformed_tree)

    

    if transformer.modified:
        # DEBUG
        source_code = ast.unparse(transformed_tree)
        print(f"Modified source code for {func.__name__}:\n")
        print(source_code)
        print("\n")

        # merge scopes
        global_scope.update(local_scope)

        # Compile the modified AST back to code
        compiled = compile(transformed_tree, filename="<ast>", mode="exec")
        exec(compiled, global_scope)

        modified_function = global_scope[func.__name__] # in the function scope will always just be a name
        global_id_to_function[id(func)] = modified_function
        global_ids_processed[id(func)]=transformer.info

        return modified_function, transformer.info
    else:
        # If no modifications were made, return the original function and an empty info dict
        global_ids_processed[id(func)] = {}
        return func, {}
