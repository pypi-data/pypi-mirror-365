# from flax.nnx import Rngs

# # _global_rng = Rngs(0)


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
#         self.key = Rngs(0)

#     def get_next(self):
#         return self.key.get_next()
    
#     def set_seed(self, seed):
#         self.key = Rngs(seed)

# _global_rng = _Global_RNG()
