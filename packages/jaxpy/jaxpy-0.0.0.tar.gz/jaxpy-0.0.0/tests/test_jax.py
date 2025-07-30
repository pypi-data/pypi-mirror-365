import jax
import jax.numpy as jnp
from flax import nnx

import os

e=0
def non_pure_func(x):
    global e

    e+=1
    return (x*2).sum()


def test1():
    global e
    x = jnp.ones(2)

    e=0

    non_pure_func(x)
    assert e==1

    jax.vmap(non_pure_func)(x)
    assert e==2

    f2=jax.vmap(non_pure_func)
    f2(x)
    f2(x)

    assert e==4
    out = f2(jnp.ones(100))
    assert e==5 # chama apenas uma vez, nice
    assert out.shape == (100,)

    grad_f = jax.grad(non_pure_func)
    grad = grad_f(x)
    assert grad[0]==2
    assert e==6
    
    e=10
    grad_f(jnp.zeros(10))
    grad_f(x)
    assert e==12

    f_jit = jax.jit(non_pure_func)
    e=0
    f_jit(x)
    assert e==1
    f_jit(x)
    f_jit(x)
    assert e==1


class Jax_test_class:
    def __init__(self):
        self.x = jnp.ones(10)
        self.y = jnp.ones(10)
        self.z = 0
    
    def non_pure_func(self, x):
        self.z+=1
        self.x +=self.y

        return self.y.sum() + x

def f(test_class: Jax_test_class, x: jnp.array):
    x = test_class.non_pure_func(x)
    return x.sum()



def test_class_args():
    t = Jax_test_class()
    x=jnp.ones(10)
    f(t,x)
    assert t.z==1
    assert jnp.all(t.x == t.y*2)

    g=jax.grad(f,argnums=1)(t,x)
    assert t.z==2
    assert jnp.all(t.x == t.y*3)

    try:
        f_jit = jax.jit(f)
        f_jit(t,x)
        assert t.z==3
        assert jnp.all(t.x == t.y*4)
    except TypeError as e:
        # print(e)
        # problem on test class, only array arguments,
        # with non array marked as static args on jax.jit
        pass

    f_jit = jax.jit(f, static_argnums=0)
    f_jit(t,x)
    assert t.z==3
    # this gives error as it detects side effects
    # assert jnp.all(t.x == t.y*4)

    

def test_static_args():
    jax.config.update("jax_log_compiles", True)


    @jax.jit
    def f(x, use_relu: bool):
        return jax.nn.relu(x) if use_relu else x



    def f2(x, use_relu: bool):
        return jax.nn.relu(x) if use_relu else x

    def f3(x, use_relu: bool):
        return jax.nn.relu(x).sum() if use_relu else x.sum()

    # error because bool passa para jax array, que nao podemos fazer if..
    # print("try f")
    # x=jnp.array((10,-10,-1,1))
    # print(f(x,True))
    # print(f(x,False))

    print("try f2")
    f2=nnx.jit(f2,static_argnames=['use_relu'])

    x=jnp.array((10,-10,-1,1)).astype(float)
    print(f2(x,True))
    print(f2(x,False))
    print("try grad f2")
    grad_f2 =nnx.grad(nnx.jit( (f3),static_argnames=['use_relu']))
    print(grad_f2(x,True))
    print(grad_f2(x,False))


# class Dataloader(nnx.Module):
#     def __init__(self,data):
#         self.data=data
#         self.lenght = len(data)
#         self.count
#  I think we should not jit dataloaders, at least not in this way....
#  at most a pattern for scan?
#  but I mean, what is a dataloader, more than a list of a list with permutation indexes right?
#  this is jitable 

def test_classes():
    # this works great! it means dataloaders or other modules would work fine

    class Test(nnx.Module):
        def __init__(self):
            self.a = 1
            self.b = jnp.array(1)

        def __call__(self):
            self.a+=1
            self.b +=1

            return self.a, self.b

    t=Test()
    print(t())
    print(t())
    print(t())

    def jit_test(c):
        return c(),c(),c()

    print(jit_test(t))

    f = nnx.jit(jit_test)
    print(jit_test(t))
    print(jit_test(t))
    print(jit_test(t))
    print(jit_test(t))
    print(jit_test(t))

    print(t)



# FIXME error since RngStream comes from another context
# jp.grad does not like this, works well with jax key
# def test_grad_with_random_eager():
#     import jaxpy as jp

#     print(jp.randn((10,1)))
#     print("now build test")
#     def test():
#         return jp.sum(jp.randn((10,10)) @ jp.randn((10,1)))

#     print(test())
#     print(test())

#     print("now jit")

#     #fails
#     # jtest = jp.jit(test)

#     # print(jtest())
#     # print(jtest())

#     def test2(x):
#         return jp.sum(x @ jp.randn((10,1)))

#     print("other version")

#     print(test2(jp.ones((10,10))))
#     print(test2(jp.ones((10,10))))

#     # works fine what is nice. so just jit!
#     grad_test = jp.grad(test2)
#     print(grad_test(jp.ones((10,10))))
#     print(grad_test(jp.ones((10,10))))


# nnx.Module

# nnx.jit