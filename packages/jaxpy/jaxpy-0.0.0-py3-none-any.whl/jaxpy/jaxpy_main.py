from jax import *
from jax.numpy import *


### FIXME import cycles would need to be resolved
# These submodules are separate because they are in an import cycle with
# jax and rely on the names imported above.
from jax import custom_derivatives as custom_derivatives
from jax import custom_batching as custom_batching
from jax import custom_transpose as custom_transpose
from jax import api_util as api_util
from jax import distributed as distributed
from jax import debug as debug
from jax import dlpack as dlpack
from jax import dtypes as dtypes
from jax import errors as errors
from jax import ffi as ffi
from jax import image as image
from jax import lax as lax
from jax import monitoring as monitoring
from jax import nn as nn
# from jax import numpy as numpy
from jax import ops as ops
from jax import profiler as profiler
# from jax import random as random # FIXME
from jax import scipy as scipy
from jax import sharding as sharding
from jax import stages as stages
from jax import tree_util as tree_util
from jax import util as util


def enable_performance_warnings():
    raise NotImplementedError


def print_jit_source(func, *args, **kwargs):
    raise NotImplementedError


# use global_rng from _random_jax module, so only 1 place
from jaxpy import random
from jaxpy._random_jax import _global_rng


# useful ops isto faria parte de outro ficheiro

# # not from import?
# from collections.abc import Callable, Sequence
# from jax._src.typing import (
#   Array, ArrayLike,
#   DType, DTypeLike, DeprecatedArg, DimSize, DuckTypedArray, Shape, StaticScalar,
# )
# import numpy as np
# def cat(xs: np.ndarray | Array | Sequence[ArrayLike],
#                 axis: int | None = 0, dtype: DTypeLike | None = None) -> Array:
#     return concatenate(xs, axis=axis, dtype=dtype)



import functools
import builtins


# not sure if should also allow function names, but want to make it such that it works
# even if jax deprecates suddently some function
def make_alias(func_name: str, new_name: str, namespace=None):
    if namespace is None:
        namespace = globals()
    
    # Look up the function by name in the namespace
    original_func = namespace.get(func_name) or getattr(builtins, func_name, None)
    
    #FIXME what todo if alias not available do nothing?
    if not callable(original_func):
        raise ValueError(f"{func_name!r} is not a callable in the given namespace.")
    
    @functools.wraps(original_func)
    def wrapper(*args, **kwargs):
        return original_func(*args, **kwargs)
    
    wrapper.__name__ = new_name
    wrapper.__qualname__ = new_name
    namespace[new_name] = wrapper
    return wrapper

make_alias("concatenate","cat")



### seed dev

# class _SingletonMeta(type):
#     _instances = {}
    
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             # This creates the actual instance
#             cls._instances[cls] = super().__call__(*args, **kwargs)
#         return cls._instances[cls]

# class _Singleton(metaclass=_SingletonMeta):
#     pass

# class _Global_RNG(_Singleton):
#     def __init__(self):
#         self.key = random.key(0)

#     def get_next(self):
#         self.key, new_key = random.split(self.key, 2)
        
#         return new_key
    
#     def set_seed(self, seed):
#         self.key = random.key(seed)

# _global_rng = _Global_RNG()



# def get_global_rng():
#     return _global_rng.key

# def set_seed(seed):
#     _global_rng.set_seed(seed)

# FIXME key...
def randn(shape,dtype=float,out_sharding=None, key=None):
    return random.normal(shape,dtype,out_sharding=out_sharding, key=key)

# # why like this?? make it more like numpy always... numpy is an api by now, will follow numpy by default...
def randint(minval,maxval,shape,dtype=int, out_sharding=None, key=None):
    return random.randint(shape, minval, maxval, dtype, out_sharding=out_sharding, key=key)


import jax


# vamos tentar dar replace do jit principalmente
# preciso tb perceber se grad precisa
from flax.nnx import grad, pmap, vmap
from flax.nnx import jit as _nnx_jit
from flax.nnx import Rngs

from jax import jit as _jax_jit
# vjg, jvp, hessian, not defined. usam jax por default. nao vou mudar

import typing as tp

# FIXME this makes no sense for now
def jit(
  fun: tp.Callable, /, *,
  in_shardings: tp.Any = None,
  out_shardings: tp.Any = None,
  static_argnums: int | tp.Sequence[int] | None = None,
  static_argnames: str | tp.Iterable[str] | None = None,
  donate_argnums: int | tp.Sequence[int] | None = None,
  donate_argnames: str | tp.Iterable[str] | None = None,
  keep_unused: bool = False,
  device: tp.Optional[jax.Device] | None = None,
  backend: str | None = None,
  inline: bool = False,
  abstracted_axes: tp.Any | None = None,
): #-> pjit.JitWrapped:
    '''
    jaxpy version, it preprocesses the function before sending it to jax
    '''

    # Check if the function is already a JIT function
    if hasattr(fun, 'jaxpy_jit'):
        # If it is, we can just return it
        return fun
    
    if not callable(fun):
        raise TypeError(f"Expected a callable, got {type(fun).__name__}")
    
    


    return _nnx_jit(fun, in_shardings=in_shardings, out_shardings=out_shardings,
                    static_argnums=static_argnums, static_argnames=static_argnames,
                    donate_argnums=donate_argnums, donate_argnames=donate_argnames,
                    keep_unused=keep_unused, device=device, backend=backend,
                    inline=inline, abstracted_axes=abstracted_axes)


######3 todo
'''

we need a lexer to process all globals e remover los dos returns puros.
lexer para todas as variaveis e funcoes usadas?

definir que novas variaveis dentro de bloco, ficaram locais excepto se for definido como return manualmente?
+ returnar tudo talvez seja uma boa opcao, visto que pode ser usado. Acho que e' mais simples. (menos eficiente again argumento, mas n muito em principio)
+ every assigment e' retornado

---------------------

Exemplo do que acharia um possivel erro de usar funcaoes
Non-jax function with dependencies? provokes a split on compiled graph in line:
previous dependence: b=jp.array([1,2,3])

previous line: b=jp.array([1,2,3])
-> line_nr: a = np.array([1,2,3])+b

further dependence: return a @ c


claro isto requer fazer track do uso das variaveis, e calls para funcoes not jittable
-----


a=2
d=None
e=None

@jp.jit
def impure():
    global e                                ## vars - e, global(e)     
    b=jp.array([1,2,3])                     ## FUNC - jp.array  ,assigment(b)                      
    temp=np.array([1,2,3])                  ## FUNC - np.array , assigment(temp) . suportamos todos os basic data types por isso ignoramos  
    temp2 = jax.array(np.array([1,2,3]))    ## FUNC - jax.array, np.array , assigment(temp2)
    b=b+temp                                ## vars - b, temp, assigment(b)
                                            ##
    c=a+b                                   ## vars - a, b, assigment(c)             
    print(c)                                ## vars - c, FUNC - print
                                            ##     
    d=a-b                                   ## vars - a, b, assigment(d)
    e=2*a-b                                 ## vars - a, b, assigment(e)
    return c                                ## return(c)     


# importante distinguir variavel na expressao a ser assign vs usada  (mas acho que e' simples, e' so todas as expressoes antes do =, confirmar com python syntax)

globals = [e]
func_args=[]
func_returns=[c]


variables=[a, np.array, jp.array, jax.array] # variáveis usadas antes de qualquer assignment 

in_variables = [a,] # variavel usada antes de qualquer assigment (mesmo que sejam incompatíveis, se não der para fazer fora Taíse error jax)
in_variables_static = [ np.array, jp.array, jax.array] #calables são automaticamente estaticos, ou mais que possamos definir manualmente

Proceed to jit callables first.





# transformed pure
def pure():
    global e

    temp=np.array([1,2,3])
    temp2 = jax.array(np.array([1,2,3])) # full expression out? so pk tem funcao nao jax, parece me bem

    @jp.jax.jit # algo assim
    def func(a,temp): #np array is supported as input, na verdade acho que devemos tentar sempre por arg, deixar jax dar erro se incorreto
        b=jp.array([1,2,3])
        b=b+temp
        c=a+b

        e=2*a-b
        return c, e

    # run jitted function
    c, e = func(a)
    
    # execute unjittable code
    print(c)

    return c


@jp.jit
def impure2():
    a=jp.array([1,2,3])
    b=jp.array([1,2,3])
    c=jp.array([1,2,3])
    temp=np.array(b)
    b=b+jp.array(temp)
    return b+a

# transformed pure
def pure():
    @jp.jax.jit 
    def func1(a,temp):
        a=jp.array([1,2,3])
        b=jp.array([1,2,3])
        c=jp.array([1,2,3]) # but dont return is not used
        return a, b

    a,b = func1()
    
    # execute unjittable code, raise WARNING
    temp=np.array(b)

    @jp.jax.jit 
    def func2(a, b, temp):
        b=b+jp.array(temp)
        return b+a
    
    outs = func2(a,b,temp)

    return outs



quero ter uma especie de funcao se jax jitable function. ou algo assim. um check inicial rapido, que por exemplo diz que jax functional calls sao jitable, 
funcoes python simples tambem mas que outras que chamem C code nao.

. get all variables used in function. Separar objectos, de funcoes, de classes (por enquanto nao sei se devia pensar em mais objectos)

comecar com apenas funcoes e a variaveis. coisas que tem que fazer
+ globals define valores que a jitted function deve retornar para dar set global

'''