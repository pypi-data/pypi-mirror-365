import jaxpy as jp
import jaxpy.random as random

import jax



def test_simple():
    # Test randn
    # FIXME randn and others in jp
    a=jp.randn((2, 3))
    # Test randint
    a=jp.randint(0, 10, (2, 3))

    a= random.normal((2,3))

    nnx_key = jp.Rngs(0)
    a = random.normal((2,3), key=nnx_key.get_next())

    jax_key = random.key(0)
    a = random.normal((2,3), key=jax_key)

    assert random.normal.__doc__

    # # Test jit with a simple function
    # @jp.jit
    # def simple_function(x):
    #     return x * random.normal((2, 3))

    # print("Testing jit:")
    # print(simple_function(5))

# ## preprocessor tests

# def test_name_error():
#     call()

# def test_name_error2():
#     def test():
#         call()
    
#     test()

# # I consider this success since function is not called
# # should it be????
# def test_name_success():
#     def test():
#         call()

# # the implementation with call would lead to error here...
# # which would be incoherent...
# def test_name_error3():
#     def test():
#         def inner():
#             call()
#         inner()

# # calling on end mainnodeDef would lead to weird successes
# # this would be preprocessed as a success
# def weird_success():
#     def inner1():
#         inner2()
    
#     def innerm():
#         print("Inner m called")

#     inner1()

#     def inner2():
#         print("Inner 2 called")
#         innerm()
    
#     inner1()

# # other problem is redefinitions
# # redefinitions is a hard problem
# def problems_success():
#     def inner1():
#         inner2()
    
#     def innerm():
#         print("Inner m called")
#     def interest_f():
#         print("interest_f called")

#     def inner2():
#         print("Inner 2 called")
#         innerm()

#     inner1()
#     def inner2():
#         print("Inner 2 called")
#         interest_f()

    
#     inner1()


# def test_name_error4():
#     def test():
#         call()
    
#     def inner():
#         test()
    
