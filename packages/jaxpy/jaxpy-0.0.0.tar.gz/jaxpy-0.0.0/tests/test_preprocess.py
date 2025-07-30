import jaxpy as jp
import jaxpy.random as random

from jaxpy._preprocess import preprocess_function

# def test_simple():
#     seed = jp.Rngs(10)
#     seed_ = jp.Rngs(10)

#     def simple():
#         return random.normal((2, 3))
    
#     target = random.normal((2, 3), key=seed_.get_next())
    
#     f, info = preprocess_function(simple)
#     key_arg_name = info['key_arg_name']

#     test = f(**{key_arg_name: seed})

#     assert jp.all(target==test)

# def test_simple2():
#     seed = jp.Rngs(10)
#     seed_ = jp.Rngs(10)

#     def simple():
#         return random.normal((2, 3))
    
#     def other():
#         return simple()
    
#     target = random.normal((2, 3), key=seed_.get_next())

#     print(locals())
#     print(globals())

#     f, info = preprocess_function(other)
#     key_arg_name = info['key_arg_name']


#     test = f(**{key_arg_name: seed})

#     assert jp.all(target==test)

# def test_simple3():
#     '''
#     Ok so basically the problem is the following,
#     if we send other to preprocess, simple is not in scope,
#     so we can obtain the locals of the caller by inspect (obtain simple)

#     so when processing other, inner will not be processed, simple will,
#     and simple will search on globals+locals (should we join? yes for compilation)

#     '''
#     seed = jp.Rngs(10)
#     seed_ = jp.Rngs(10)

#     def simple():
#         return random.normal((2, 3))
    
#     def other():
#         def inner():
#             return simple()
        
#         return inner()
    
#     target = random.normal((2, 3), key=seed_.get_next())

#     f, info = preprocess_function(other)
#     key_arg_name = info['key_arg_name']

#     test = f(**{key_arg_name: seed})

#     assert jp.all(target==test)

def test_dynamic_defs():
    seed = jp.Rngs(10)
    seed_ = jp.Rngs(10)

    f_random=random.normal

    def other():
        def inner():
            b = (lambda: 1) if False else a
            return b()
        
        return inner()
    
    # in this case simple also needs the locals
    def simple():
        return f_random((2, 3))
    
    a = simple
    

    target = random.normal((2, 3), key=seed_.get_next())

    f, info = preprocess_function(other)
    key_arg_name = info['key_arg_name']

    test = f(**{key_arg_name: seed})

    assert jp.all(target==test)


# def test_simple_attr_error():
#     try:

#         def simple():
#             return random.normal_unexistant((2, 3))
        
#         f, info = preprocess_function(simple)
#         assert "key_arg_name" not in info

#         test = f()
#     except AttributeError as e:
#         assert "normal_unexistant" in str(e)

# def test_simple_attr_error_2():
#     try:

#         def simple():
#             return random.normal_unexistant((2, 3))
        
#         def other():
#             return simple()
        
#         f, info = preprocess_function(other)
#         assert "key_arg_name" not in info

#         test = f()
#     except AttributeError as e:
#         assert "normal_unexistant" in str(e)


# def test_simple_attr_error_3():
#     try:
#         def other():
#             def simple():
#                 return random.normal_unexistant((2, 3))
        

#             return simple()
        
#         f, info = preprocess_function(other)
#         assert "key_arg_name" not in info

#         test = f()
#     except AttributeError as e:
#         assert "normal_unexistant" in str(e)



# ## Class inside fixing..
# # this works
# def test_simple2_jit():
#     seed = jp.Rngs(10)
#     seed_ = jp.Rngs(20)

#     def simple():
#         return random.normal((2, 3), key=jp.Rngs(20).get_next())
    
#     target = random.normal((2, 3), key=seed_.get_next())
    
#     f = jp.jit(simple)

#     test = f()

#     assert jp.all(target==test)

def test_simple2():
    seed = jp.Rngs(10)
    seed_ = jp.Rngs(20)

    """
    This one is very intersting, because we do a call, and then
    atrr and call. We cannot preprocess the latter call, as we do not know the return 
    of previous call.

    The class thing is also interesting, because it works differently than function (no global scope)
    # it could help us know the attributes, but I need to think about it better.
    """

    def simple():
        # return random.normal((2, 3), key=jp.Rngs(20).get_next()) #
        k=jp.Rngs(20)
        return random.normal((2, 3), key=k()) # error
    
    target = random.normal((2, 3), key=seed_.get_next())
    
    f, info = preprocess_function(simple)
    key_arg_name = info['key_arg_name']

    test = f(**{key_arg_name: seed})

    assert jp.all(target==test)

