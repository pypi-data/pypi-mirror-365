import jax.random as _random_jax
import importlib
import inspect

overloads_str = ""
alls_list = []

def get_annotation(annotation):
    if annotation is inspect._empty:
        return 'Any'
    elif hasattr(annotation, '__name__'): # If it's a type, get its name
        return annotation.__name__
    else:
        return str(annotation)
    

def get_default(default):
    if default is inspect._empty:
        return inspect._empty
    elif hasattr(default, '__name__'): # If it's a type, get its name
        return default.__name__
    elif isinstance(default, str): # If it's a string, return it as is
        return f"'{default}'"
    else:
        return str(default)

# Iterate over all attributes in the module
for name in dir(_random_jax):
    attr = getattr(_random_jax, name)
    if callable(attr):  # Import only functions and callable object
        # if first argument is key, then we generate an overload
        sig = inspect.signature(attr)
        doc = attr.__doc__ or ""
        if len(sig.parameters) > 0 and list(sig.parameters.keys())[0] == 'key':
            # obtain parameters names, annotations and defaults
            params = []
            for k, a in list(sig.parameters.items())[1:]:  # Skip the first parameter (key)
                annotation = get_annotation(a.annotation)
                default = get_default(a.default)
                if default is inspect._empty:
                    default = ''
                else:
                    default = f"={default}"
                params.append(f"{k}: {annotation}{default}")

            # add key parameter at end as optional
            params.append("key: ArrayLike = None")
            
            # obtain return annotation
            return_annotation = get_annotation(sig.return_annotation)

            # create overload string
            overloads_str += "@overload\n"
            overloads_str += f"def {name}({', '.join(params)}) -> {return_annotation}: \n"
            overloads_str += f'  """{doc.strip()}"""\n'
            overloads_str += "  ...\n\n"
            alls_list.append(name)

print(overloads_str)

print(f"__all__ = {alls_list}")
            



        
        
        # globals()[name] = attr  # Inject into global scope