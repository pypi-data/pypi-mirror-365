from typing import overload

from typing import Callable, Any
from collections.abc import Sequence
from jax._src.typing import ArrayLike, DTypeLike, Array
RealArray = ArrayLike
IntegerArray = ArrayLike
# TODO: Import or define these to match
# https://github.com/numpy/numpy/blob/main/numpy/typing/_dtype_like.py.
DTypeLikeInt = DTypeLike
DTypeLikeUInt = DTypeLike
DTypeLikeFloat = DTypeLike
Shape = Sequence[int]

### overloads from tools/generate_jax_random_overloads.py
### Manually edited the docstrings to put key optional
@overload
def ball(d: int, p: float=2, shape: Shape=(), dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Any: 
  """Sample uniformly from the unit Lp ball.

  Reference: https://arxiv.org/abs/math/0503650.

  Args:
    d: a nonnegative int representing the dimensionality of the ball.
    p: a float representing the p parameter of the Lp norm.
    shape: optional, the batch dimensions of the result. Default ().
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array of shape `(*shape, d)` and specified dtype."""
  ...

@overload
def bernoulli(p: RealArray=0.5, shape: Shape | None=None, mode: str='low', key: ArrayLike = None) -> Array: 
  """Sample Bernoulli random values with given shape and mean.

  The values are distributed according to the probability mass function:

  .. math::
     f(k; p) = p^k(1 - p)^{1 - k}

  where :math:`k \in \{0, 1\}` and :math:`0 \le p \le 1`.

  Args:
    p: optional, a float or array of floats for the mean of the random
      variables. Must be broadcast-compatible with ``shape``. Default 0.5.
    shape: optional, a tuple of nonnegative integers representing the result
      shape. Must be broadcast-compatible with ``p.shape``. The default (None)
      produces a result shape equal to ``p.shape``.
    mode: optional, "high" or "low" for how many bits to use when sampling.
      default='low'. Set to "high" for correct sampling at small values of
      `p`. When sampling in float32, bernoulli samples with mode='low' produce
      incorrect results for p < ~1E-7. mode="high" approximately doubles the
      cost of sampling.
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with boolean dtype and shape given by ``shape`` if ``shape``
    is not None, or else ``p.shape``."""
  ...

@overload
def beta(a: RealArray, b: RealArray, shape: Shape | None=None, dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample Beta random values with given shape and float dtype.

  The values are distributed according to the probability density function:

  .. math::
     f(x;a,b) \propto x^{a - 1}(1 - x)^{b - 1}

  on the domain :math:`0 \le x \le 1`.

  Args:
    a: a float or array of floats broadcast-compatible with ``shape``
      representing the first parameter "alpha".
    b: a float or array of floats broadcast-compatible with ``shape``
      representing the second parameter "beta".
    shape: optional, a tuple of nonnegative integers specifying the result
      shape. Must be broadcast-compatible with ``a`` and ``b``. The default
      (None) produces a result shape by broadcasting ``a`` and ``b``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and shape given by ``shape`` if
    ``shape`` is not None, or else by broadcasting ``a`` and ``b``."""
  ...

@overload
def binomial(n: RealArray, p: RealArray, shape: Shape | None=None, dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample Binomial random values with given shape and float dtype.

  The values are returned according to the probability mass function:

  .. math::
      f(k;n,p) = \binom{n}{k}p^k(1-p)^{n-k}

  on the domain :math:`0 < p < 1`, and where :math:`n` is a nonnegative integer
  representing the number of trials and :math:`p` is a float representing the
  probability of success of an individual trial.

  Args:
    n: a float or array of floats broadcast-compatible with ``shape``
      representing the number of trials.
    p: a float or array of floats broadcast-compatible with ``shape``
      representing the probability of success of an individual trial.
    shape: optional, a tuple of nonnegative integers specifying the result
      shape. Must be broadcast-compatible with ``n`` and ``p``.
      The default (None) produces a result shape equal to ``np.broadcast(n, p).shape``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and with shape given by
    ``np.broadcast(n, p).shape``."""
  ...

@overload
def bits(shape: Shape=(), dtype: DTypeLikeUInt | None=None, out_sharding: Any=None, key: ArrayLike = None) -> Array: 
  """Sample uniform bits in the form of unsigned integers.

  Args:
    shape: optional, a tuple of nonnegative integers representing the result
      shape. Default ``()``.
    dtype: optional, an unsigned integer dtype for the returned values (default
      ``uint64`` if ``jax_enable_x64`` is true, otherwise ``uint32``).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified shape and dtype."""
  ...

@overload
def categorical(logits: RealArray, axis: int=-1, shape: Shape | None=None, replace: bool=True, mode: str | None=None, key: ArrayLike = None) -> Array: 
  """Sample random values from categorical distributions.

  Sampling with replacement uses the Gumbel max trick. Sampling without replacement uses
  the Gumbel top-k trick. See [1] for reference.

  Args:
    logits: Unnormalized log probabilities of the categorical distribution(s) to sample from,
      so that `softmax(logits, axis)` gives the corresponding probabilities.
    axis: Axis along which logits belong to the same categorical distribution.
    shape: Optional, a tuple of nonnegative integers representing the result shape.
      Must be broadcast-compatible with ``np.delete(logits.shape, axis)``.
      The default (None) produces a result shape equal to ``np.delete(logits.shape, axis)``.
    replace: If True (default), perform sampling with replacement. If False, perform
      sampling without replacement.
    mode: optional, "high" or "low" for how many bits to use in the gumbel sampler.
      The default is determined by the ``use_high_dynamic_range_gumbel`` config,
      which defaults to "low". With mode="low", in float32 sampling will be biased
      for events with probability less than about 1E-7; with mode="high" this limit
      is pushed down to about 1E-14. mode="high" approximately doubles the cost of
      sampling.
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with int dtype and shape given by ``shape`` if ``shape``
    is not None, or else ``np.delete(logits.shape, axis)``.

  References:
    .. [1] Wouter Kool, Herke van Hoof, Max Welling. "Stochastic Beams and Where to Find
      Them: The Gumbel-Top-k Trick for Sampling Sequences Without Replacement".
      Proceedings of the 36th International Conference on Machine Learning, PMLR
      97:3499-3508, 2019. https://proceedings.mlr.press/v97/kool19a.html."""
  ...

@overload
def cauchy(shape: Shape=(), dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample Cauchy random values with given shape and float dtype.

  The values are distributed according to the probability density function:

  .. math::
     f(x) \propto \frac{1}{x^2 + 1}

  on the domain :math:`-\infty < x < \infty`

  Args:
    shape: optional, a tuple of nonnegative integers representing the result
      shape. Default ().
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified shape and dtype."""
  ...

@overload
def chisquare(df: RealArray, shape: Shape | None=None, dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample Chisquare random values with given shape and float dtype.

  The values are distributed according to the probability density function:

  .. math::
     f(x; \nu) \propto x^{\nu/2 - 1}e^{-x/2}

  on the domain :math:`0 < x < \infty`, where :math:`\nu > 0` represents the
  degrees of freedom, given by the parameter ``df``.

  Args:
    df: a float or array of floats broadcast-compatible with ``shape``
      representing the parameter of the distribution.
    shape: optional, a tuple of nonnegative integers specifying the result
      shape. Must be broadcast-compatible with ``df``. The default (None)
      produces a result shape equal to ``df.shape``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and with shape given by ``shape`` if
    ``shape`` is not None, or else by ``df.shape``."""
  ...

@overload
def choice(a: int | ArrayLike, shape: Shape=(), replace: bool=True, p: RealArray | None=None, axis: int=0, mode: str | None=None, key: ArrayLike = None) -> Array: 
  """Generates a random sample from a given array.

  .. warning::
    If ``p`` has fewer non-zero elements than the requested number of samples,
    as specified in ``shape``, and ``replace=False``, the output of this
    function is ill-defined. Please make sure to use appropriate inputs.

  Args:
    a : array or int. If an ndarray, a random sample is generated from
      its elements. If an int, the random sample is generated as if a were
      arange(a).
    shape : tuple of ints, optional. Output shape.  If the given shape is,
      e.g., ``(m, n)``, then ``m * n`` samples are drawn.  Default is (),
      in which case a single value is returned.
    replace : boolean.  Whether the sample is with or without replacement.
      Default is True.
    p : 1-D array-like, The probabilities associated with each entry in a.
      If not given the sample assumes a uniform distribution over all
      entries in a.
    axis: int, optional. The axis along which the selection is performed.
      The default, 0, selects by row.
    mode: optional, "high" or "low" for how many bits to use in the gumbel sampler
      when `p is None` and `replace = False`. The default is determined by the
      ``use_high_dynamic_range_gumbel`` config, which defaults to "low". With mode="low",
      in float32 sampling will be biased for choices with probability less than about
      1E-7; with mode="high" this limit is pushed down to about 1E-14. mode="high"
      approximately doubles the cost of sampling.
    key: optional, a PRNG key used as the random key.

  Returns:
    An array of shape `shape` containing samples from `a`."""
  ...

@overload
def clone(key: ArrayLike = None) -> Any: 
  """Clone a key for reuse

  Outside the context of key reuse checking (see :mod:`jax.experimental.key_reuse`)
  this function operates as an identity.

  Examples:

    >>> import jax
    >>> key = jax.random.key(0)
    >>> data = jax.random.uniform(key)
    >>> cloned_key = jax.random.clone(key)
    >>> same_data = jax.random.uniform(cloned_key)
    >>> assert data == same_data"""
  ...

@overload
def dirichlet(alpha: RealArray, shape: Shape | None=None, dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample Dirichlet random values with given shape and float dtype.

  The values are distributed according to the probability density function:

  .. math::
     f(\{x_i\}; \{\alpha_i\}) \propto \prod_{i=1}^k x_i^{\alpha_i - 1}

  Where :math:`k` is the dimension, and :math:`\{x_i\}` satisfies

  .. math::
     \sum_{i=1}^k x_i = 1

  and :math:`0 \le x_i \le 1` for all :math:`x_i`.

  Args:
    alpha: an array of shape ``(..., n)`` used as the concentration
      parameter of the random variables.
    shape: optional, a tuple of nonnegative integers specifying the result
      batch shape; that is, the prefix of the result shape excluding the last
      element of value ``n``. Must be broadcast-compatible with
      ``alpha.shape[:-1]``. The default (None) produces a result shape equal to
      ``alpha.shape``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and shape given by
    ``shape + (alpha.shape[-1],)`` if ``shape`` is not None, or else
    ``alpha.shape``."""
  ...

@overload
def double_sided_maxwell(loc: RealArray, scale: RealArray, shape: Shape=(), dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample from a double sided Maxwell distribution.

  The values are distributed according to the probability density function:

  .. math::
     f(x;\mu,\sigma) \propto z^2 e^{-z^2 / 2}

  where :math:`z = (x - \mu) / \sigma`, with the center :math:`\mu` specified by
  ``loc`` and the scale :math:`\sigma` specified by ``scale``.

  Args:
    loc: The location parameter of the distribution.
    scale: The scale parameter of the distribution.
    shape: The shape added to the parameters loc and scale broadcastable shape.
    dtype: The type used for samples.
    key: optional, a PRNG key used as the random key.

  Returns:
    A jnp.array of samples."""
  ...

@overload
def exponential(shape: Shape=(), dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample Exponential random values with given shape and float dtype.

  The values are distributed according to the probability density function:

  .. math::
     f(x) = e^{-x}

  on the domain :math:`0 \le x < \infty`.

  Args:
    shape: optional, a tuple of nonnegative integers representing the result
      shape. Default ().
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified shape and dtype."""
  ...

@overload
def f(dfnum: RealArray, dfden: RealArray, shape: Shape | None=None, dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample F-distribution random values with given shape and float dtype.

  The values are distributed according to the probability density function:

  .. math::
     f(x; \nu_1, \nu_2) \propto x^{\nu_1/2 - 1}\left(1 + \frac{\nu_1}{\nu_2}x\right)^{
      -(\nu_1 + \nu_2) / 2}

  on the domain :math:`0 < x < \infty`. Here :math:`\nu_1` is the degrees of
  freedom of the numerator (``dfnum``), and :math:`\nu_2` is the degrees of
  freedom of the denominator (``dfden``).

  Args:
    dfnum: a float or array of floats broadcast-compatible with ``shape``
      representing the numerator's ``df`` of the distribution.
    dfden: a float or array of floats broadcast-compatible with ``shape``
      representing the denominator's ``df`` of the distribution.
    shape: optional, a tuple of nonnegative integers specifying the result
      shape. Must be broadcast-compatible with ``dfnum`` and ``dfden``.
      The default (None) produces a result shape equal to ``dfnum.shape``,
      and ``dfden.shape``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and with shape given by ``shape`` if
    ``shape`` is not None, or else by ``df.shape``."""
  ...

@overload
def fold_in(data: IntegerArray, key: ArrayLike = None) -> Array: 
  """Folds in data to a PRNG key to form a new PRNG key.

  Args:
    data: a 32-bit integer representing data to be folded into the key.
    key: optional, a PRNG key (from ``key``, ``split``, ``fold_in``).

  Returns:
    A new PRNG key that is a deterministic function of the inputs and is
    statistically safe for producing a stream of new pseudo-random values."""
  ...

@overload
def gamma(a: RealArray, shape: Shape | None=None, dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample Gamma random values with given shape and float dtype.

  The values are distributed according to the probability density function:

  .. math::
     f(x;a) \propto x^{a - 1} e^{-x}

  on the domain :math:`0 \le x < \infty`, with :math:`a > 0`.

  This is the standard gamma density, with a unit scale/rate parameter.
  Dividing the sample output by the rate is equivalent to sampling from
  *gamma(a, rate)*, and multiplying the sample output by the scale is equivalent
  to sampling from *gamma(a, scale)*.

  Args:
    a: a float or array of floats broadcast-compatible with ``shape``
      representing the parameter of the distribution.
    shape: optional, a tuple of nonnegative integers specifying the result
      shape. Must be broadcast-compatible with ``a``. The default (None)
      produces a result shape equal to ``a.shape``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and with shape given by ``shape`` if
    ``shape`` is not None, or else by ``a.shape``.

  See Also:
    loggamma : sample gamma values in log-space, which can provide improved
      accuracy for small values of ``a``."""
  ...

@overload
def generalized_normal(p: float, shape: Shape=(), dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample from the generalized normal distribution.

  The values are returned according to the probability density function:

  .. math::
     f(x;p) \propto e^{-|x|^p}

  on the domain :math:`-\infty < x < \infty`, where :math:`p > 0` is the
  shape parameter.

  Args:
    p: a float representing the shape parameter.
    shape: optional, the batch dimensions of the result. Default ().
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified shape and dtype."""
  ...

@overload
def geometric(p: RealArray, shape: Shape | None=None, dtype: DTypeLikeInt=int, key: ArrayLike = None) -> Array: 
  """Sample Geometric random values with given shape and float dtype.

  The values are returned according to the probability mass function:

  .. math::
      f(k;p) = p(1-p)^{k-1}

  on the domain :math:`0 < p < 1`.

  Args:
    p: a float or array of floats broadcast-compatible with ``shape``
      representing the probability of success of an individual trial.
    shape: optional, a tuple of nonnegative integers specifying the result
      shape. Must be broadcast-compatible with ``p``. The default
      (None) produces a result shape equal to ``np.shape(p)``.
    dtype: optional, a int dtype for the returned values (default int64 if
      jax_enable_x64 is true, otherwise int32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and with shape given by ``shape`` if
    ``shape`` is not None, or else by ``p.shape``."""
  ...

@overload
def gumbel(shape: Shape=(), dtype: DTypeLikeFloat=float, mode: str | None=None, key: ArrayLike = None) -> Array: 
  """Sample Gumbel random values with given shape and float dtype.

  The values are distributed according to the probability density function:

  .. math::
     f(x) = e^{-(x + e^{-x})}

  Args:
    shape: optional, a tuple of nonnegative integers representing the result
      shape. Default ().
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    mode: optional, "high" or "low" for how many bits to use when sampling.
      The default is determined by the ``use_high_dynamic_range_gumbel`` config,
      which defaults to "low". When drawing float32 samples, with mode="low" the
      uniform resolution is such that the largest possible gumbel logit is ~16;
      with mode="high" this is increased to ~32, at approximately double the
      computational cost.
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified shape and dtype."""
  ...

@overload
def laplace(shape: Shape=(), dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample Laplace random values with given shape and float dtype.

  The values are distributed according to the probability density function:

  .. math::
    f(x) = \frac{1}{2}e^{-|x|}

  Args:
    shape: optional, a tuple of nonnegative integers representing the result
      shape. Default ().
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified shape and dtype."""
  ...

@overload
def loggamma(a: RealArray, shape: Shape | None=None, dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample log-gamma random values with given shape and float dtype.

  This function is implemented such that the following will hold for a
  dtype-appropriate tolerance::

    np.testing.assert_allclose(jnp.exp(loggamma(*args)), gamma(*args), rtol=rtol)

  The benefit of log-gamma is that for samples very close to zero (which occur frequently
  when `a << 1`) sampling in log space provides better precision.

  Args:
    a: a float or array of floats broadcast-compatible with ``shape``
      representing the parameter of the distribution.
    shape: optional, a tuple of nonnegative integers specifying the result
      shape. Must be broadcast-compatible with ``a``. The default (None)
      produces a result shape equal to ``a.shape``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and with shape given by ``shape`` if
    ``shape`` is not None, or else by ``a.shape``.

  See Also:
    gamma : standard gamma sampler."""
  ...

@overload
def logistic(shape: Shape=(), dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample logistic random values with given shape and float dtype.

  The values are distributed according to the probability density function:

  .. math::
     f(x) = \frac{e^{-x}}{(1 + e^{-x})^2}

  Args:
    shape: optional, a tuple of nonnegative integers representing the result
      shape. Default ().
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified shape and dtype."""
  ...

@overload
def lognormal(sigma: RealArray=1.0, shape: Shape | None=None, dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample lognormal random values with given shape and float dtype.

  The values are distributed according to the probability density function:

  .. math::
      f(x) = \frac{1}{x\sqrt{2\pi\sigma^2}}\exp\left(-\frac{(\log x)^2}{2\sigma^2}\right)

  on the domain :math:`x > 0`.

  Args:
    sigma: a float or array of floats broadcast-compatible with ``shape`` representing
      the standard deviation of the underlying normal distribution. Default 1.
    shape: optional, a tuple of nonnegative integers specifying the result
      shape. The default (None) produces a result shape equal to ``()``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and with shape given by ``shape``."""
  ...

@overload
def maxwell(shape: Shape=(), dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample from a one sided Maxwell distribution.

  The values are distributed according to the probability density function:

  .. math::
     f(x) \propto x^2 e^{-x^2 / 2}

  on the domain :math:`0 \le x < \infty`.

  Args:
    shape: The shape of the returned samples.
    dtype: The type used for samples.
    key: optional, a PRNG key.

  Returns:
    A jnp.array of samples, of shape `shape`."""
  ...

@overload
def multinomial(n: RealArray, p: RealArray, shape: Shape | None=None, dtype: DTypeLikeFloat=float, unroll: int | bool=1, key: ArrayLike = None) -> Any: 
  """Sample from a multinomial distribution.

  The probability mass function is

  .. math::
      f(x;n,p) = \frac{n!}{x_1! \ldots x_k!} p_1^{x_1} \ldots p_k^{x_k}

  Args:
    n: number of trials. Should have shape broadcastable to ``p.shape[:-1]``.
    p: probability of each outcome, with outcomes along the last axis.
    shape: optional, a tuple of nonnegative integers specifying the result batch
      shape, that is, the prefix of the result shape excluding the last axis.
      Must be broadcast-compatible with ``p.shape[:-1]``. The default (None)
      produces a result shape equal to ``p.shape``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    unroll: optional, unroll parameter passed to :func:`jax.lax.scan` inside the
      implementation of this function.
    key: optional, a PRNG key used as the random key.

  Returns:
    An array of counts for each outcome with the specified dtype and with shape
      ``p.shape`` if ``shape`` is None, otherwise ``shape + (p.shape[-1],)``."""
  ...

@overload
def multivariate_normal(mean: RealArray, cov: RealArray, shape: Shape | None=None, dtype: DTypeLikeFloat | None=None, method: str='cholesky', key: ArrayLike = None) -> Array: 
  """Sample multivariate normal random values with given mean and covariance.

  The values are returned according to the probability density function:

  .. math::
     f(x;\mu, \Sigma) = (2\pi)^{-k/2} \det(\Sigma)^{-1}e^{-\frac{1}{2}(x - \mu)^T \Sigma^{-1} (x - \mu)}

  where :math:`k` is the dimension, :math:`\mu` is the mean (given by ``mean``) and
  :math:`\Sigma` is the covariance matrix (given by ``cov``).

  Args:
    mean: a mean vector of shape ``(..., n)``.
    cov: a positive definite covariance matrix of shape ``(..., n, n)``. The
      batch shape ``...`` must be broadcast-compatible with that of ``mean``.
    shape: optional, a tuple of nonnegative integers specifying the result
      batch shape; that is, the prefix of the result shape excluding the last
      axis. Must be broadcast-compatible with ``mean.shape[:-1]`` and
      ``cov.shape[:-2]``. The default (None) produces a result batch shape by
      broadcasting together the batch shapes of ``mean`` and ``cov``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    method: optional, a method to compute the factor of ``cov``.
      Must be one of 'svd', 'eigh', and 'cholesky'. Default 'cholesky'. For
      singular covariance matrices, use 'svd' or 'eigh'.
    key: optional, a PRNG key used as the random key.
  Returns:
    A random array with the specified dtype and shape given by
    ``shape + mean.shape[-1:]`` if ``shape`` is not None, or else
    ``broadcast_shapes(mean.shape[:-1], cov.shape[:-2]) + mean.shape[-1:]``."""
  ...

@overload
def normal(shape: Shape=(), dtype: DTypeLikeFloat=float, out_sharding: Any=None, key: ArrayLike = None) -> Array: 
  """Sample standard normal random values with given shape and float dtype.

  The values are returned according to the probability density function:

  .. math::
     f(x) = \frac{1}{\sqrt{2\pi}}e^{-x^2/2}

  on the domain :math:`-\infty < x < \infty`

  Args:
    shape: optional, a tuple of nonnegative integers representing the result
      shape. Default ().
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified shape and dtype."""
  ...

@overload
def orthogonal(n: int, shape: Shape=(), dtype: DTypeLikeFloat=float, m: int | None=None, key: ArrayLike = None) -> Array: 
  """Sample uniformly from the orthogonal group O(n).

  If the dtype is complex, sample uniformly from the unitary group U(n).

  For unequal rows and columns, this samples a semi-orthogonal matrix instead.
  That is, if :math:`A` is the resulting matrix and :math:`A^*` is its conjugate
  transpose, then:

  - If :math:`n \leq m`, the rows are mutually orthonormal: :math:`A A^* = I_n`.
  - If :math:`m \leq n`, the columns are mutually orthonormal: :math:`A^* A = I_m`.

  Args:
    n: an integer indicating the number of rows.
    shape: optional, the batch dimensions of the result. Default ().
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    m: an integer indicating the number of columns. Defaults to `n`.
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array of shape `(*shape, n, m)` and specified dtype.

  References:
    .. [1] Mezzadri, Francesco. (2007). "How to generate random matrices from
           the classical compact groups". Notices of the American Mathematical
           Society, 54(5), 592-604. https://arxiv.org/abs/math-ph/0609050."""
  ...

@overload
def pareto(b: RealArray, shape: Shape | None=None, dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample Pareto random values with given shape and float dtype.

  The values are distributed according to the probability density function:

  .. math::
     f(x; b) = b / x^{b + 1}

  on the domain :math:`1 \le x < \infty` with :math:`b > 0`

  Args:
    b: a float or array of floats broadcast-compatible with ``shape``
      representing the parameter of the distribution.
    shape: optional, a tuple of nonnegative integers specifying the result
      shape. Must be broadcast-compatible with ``b``. The default (None)
      produces a result shape equal to ``b.shape``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and with shape given by ``shape`` if
    ``shape`` is not None, or else by ``b.shape``."""
  ...

@overload
def permutation(x: int | ArrayLike, axis: int=0, independent: bool=False, out_sharding: Any=None, key: ArrayLike = None) -> Array: 
  """Returns a randomly permuted array or range.

  Args:
    x: int or array. If x is an integer, randomly shuffle np.arange(x).
      If x is an array, randomly shuffle its elements.
    axis: int, optional. The axis which x is shuffled along. Default is 0.
    independent: bool, optional. If set to True, each individual vector along
      the given axis is shuffled independently. Default is False.
    key: optional, a PRNG key used as the random key.

  Returns:
    A shuffled version of x or array range"""
  ...

@overload
def poisson(lam: RealArray, shape: Shape | None=None, dtype: DTypeLikeInt=int, key: ArrayLike = None) -> Array: 
  """Sample Poisson random values with given shape and integer dtype.

  The values are distributed according to the probability mass function:

  .. math::
     f(k; \lambda) = \frac{\lambda^k e^{-\lambda}}{k!}

  Where `k` is a non-negative integer and :math:`\lambda > 0`.

  Args:
    lam: rate parameter (mean of the distribution), must be >= 0. Must be broadcast-compatible with ``shape``
    shape: optional, a tuple of nonnegative integers representing the result
      shape. Default (None) produces a result shape equal to ``lam.shape``.
    dtype: optional, a integer dtype for the returned values (default int64 if
      jax_enable_x64 is true, otherwise int32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and with shape given by ``shape`` if
    ``shape is not None, or else by ``lam.shape``."""
  ...

@overload
def rademacher(shape: Shape=(), dtype: DTypeLikeInt=int, key: ArrayLike = None) -> Array: 
  """Sample from a Rademacher distribution.

  The values are distributed according to the probability mass function:

  .. math::
     f(k) = \frac{1}{2}(\delta(k - 1) + \delta(k + 1))

  on the domain :math:`k \in \{-1, 1\}`, where :math:`\delta(x)` is the dirac delta function.

  Args:
    shape: The shape of the returned samples. Default ().
    dtype: The type used for samples.
    key: optional, a PRNG key used as the random key.

  Returns:
    A jnp.array of samples, of shape `shape`. Each element in the output has
    a 50% change of being 1 or -1."""
  ...

@overload
def randint(shape: Shape, minval: IntegerArray, maxval: IntegerArray, dtype: DTypeLikeInt=int, out_sharding: Any=None, key: ArrayLike = None) -> Array: 
  """Sample uniform random values in [minval, maxval) with given shape/dtype.

  Args:
    shape: a tuple of nonnegative integers representing the shape.
    minval: int or array of ints broadcast-compatible with ``shape``, a minimum
      (inclusive) value for the range.
    maxval: int or array of ints broadcast-compatible with ``shape``, a maximum
      (exclusive) value for the range.
    dtype: optional, an int dtype for the returned values (default int64 if
      jax_enable_x64 is true, otherwise int32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified shape and dtype."""
  ...

@overload
def rayleigh(scale: RealArray, shape: Shape | None=None, dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample Rayleigh random values with given shape and float dtype.

  The values are returned according to the probability density function:

  .. math::
     f(x;\sigma) \propto xe^{-x^2/(2\sigma^2)}

  on the domain :math:`-\infty < x < \infty`, and where :math:`\sigma > 0` is the scale
  parameter of the distribution.

  Args:
    scale: a float or array of floats broadcast-compatible with ``shape``
      representing the parameter of the distribution.
    shape: optional, a tuple of nonnegative integers specifying the result
      shape. Must be broadcast-compatible with ``scale``. The default (None)
      produces a result shape equal to ``scale.shape``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and with shape given by ``shape`` if
    ``shape`` is not None, or else by ``scale.shape``."""
  ...

@overload
def split(num: int | tuple[int, ...]=2, key: ArrayLike = None) -> Array: 
  """Splits a PRNG key into `num` new keys by adding a leading axis.

  Args:
    num: optional, a positive integer (or tuple of integers) indicating
      the number (or shape) of keys to produce. Defaults to 2.
    key: optional, a PRNG key (from ``key``, ``split``, ``fold_in``).

  Returns:
    An array-like object of `num` new PRNG keys."""
  ...

@overload
def t(df: RealArray, shape: Shape=(), dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample Student's t random values with given shape and float dtype.

  The values are distributed according to the probability density function:

  .. math::
     f(t; \nu) \propto \left(1 + \frac{t^2}{\nu}\right)^{-(\nu + 1)/2}

  Where :math:`\nu > 0` is the degrees of freedom, given by the parameter ``df``.

  Args:
    df: a float or array of floats broadcast-compatible with ``shape``
      representing the degrees of freedom parameter of the distribution.
    shape: optional, a tuple of nonnegative integers specifying the result
      shape. Must be broadcast-compatible with ``df``. The default (None)
      produces a result shape equal to ``df.shape``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and with shape given by ``shape`` if
    ``shape`` is not None, or else by ``df.shape``."""
  ...

@overload
def triangular(left: RealArray, mode: RealArray, right: RealArray, shape: Shape | None=None, dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample Triangular random values with given shape and float dtype.

  The values are returned according to the probability density function:

  .. math::
      f(x; a, b, c) = \frac{2}{c-a} \left\{ \begin{array}{ll} \frac{x-a}{b-a} & a \leq x \leq b \\ \frac{c-x}{c-b} & b \leq x \leq c \end{array} \right.

  on the domain :math:`a \leq x \leq c`.

  Args:
    left: a float or array of floats broadcast-compatible with ``shape``
      representing the lower limit parameter of the distribution.
    mode: a float or array of floats broadcast-compatible with ``shape``
      representing the peak value parameter of the distribution, value must
      fulfill the condition ``left <= mode <= right``.
    right: a float or array of floats broadcast-compatible with ``shape``
      representing the upper limit parameter of the distribution, must be
      larger than ``left``.
    shape: optional, a tuple of nonnegative integers specifying the result
      shape. Must be broadcast-compatible with ``left``,``mode`` and ``right``.
      The default (None) produces a result shape equal to ``left.shape``, ``mode.shape``
      and ``right.shape``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and with shape given by ``shape`` if
    ``shape`` is not None, or else by ``left.shape``, ``mode.shape`` and ``right.shape``."""
  ...

@overload
def truncated_normal(lower: RealArray, upper: RealArray, shape: Shape | None=None, dtype: DTypeLikeFloat=float, out_sharding: Any=None, key: ArrayLike = None) -> Array: 
  """Sample truncated standard normal random values with given shape and dtype.

  The values are returned according to the probability density function:

  .. math::
     f(x) \propto e^{-x^2/2}

  on the domain :math:`\rm{lower} < x < \rm{upper}`.

  Args:
    lower: a float or array of floats representing the lower bound for
      truncation. Must be broadcast-compatible with ``upper``.
    upper: a float or array of floats representing the  upper bound for
      truncation. Must be broadcast-compatible with ``lower``.
    shape: optional, a tuple of nonnegative integers specifying the result
      shape. Must be broadcast-compatible with ``lower`` and ``upper``. The
      default (None) produces a result shape by broadcasting ``lower`` and
      ``upper``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and shape given by ``shape`` if
    ``shape`` is not None, or else by broadcasting ``lower`` and ``upper``.
    Returns values in the open interval ``(lower, upper)``."""
  ...

@overload
def uniform(shape: Shape=(), dtype: DTypeLikeFloat=float, minval: RealArray=0.0, maxval: RealArray=1.0, out_sharding: Any=None, key: ArrayLike = None) -> Array: 
  """Sample uniform random values in [minval, maxval) with given shape/dtype.

  Args:
    shape: optional, a tuple of nonnegative integers representing the result
      shape. Default ().
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    minval: optional, a minimum (inclusive) value broadcast-compatible with shape for the range (default 0).
    maxval: optional, a maximum (exclusive) value broadcast-compatible with shape for the range (default 1).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified shape and dtype."""
  ...

@overload
def wald(mean: RealArray, shape: Shape | None=None, dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample Wald random values with given shape and float dtype.

  The values are returned according to the probability density function:

  .. math::
     f(x;\mu) = \frac{1}{\sqrt{2\pi x^3}} \exp\left(-\frac{(x - \mu)^2}{2\mu^2 x}\right)

  on the domain :math:`-\infty < x < \infty`, and where :math:`\mu > 0` is the location
  parameter of the distribution.


  Args:
    mean: a float or array of floats broadcast-compatible with ``shape``
      representing the mean parameter of the distribution.
    shape: optional, a tuple of nonnegative integers specifying the result
      shape. Must be broadcast-compatible with ``mean``. The default
      (None) produces a result shape equal to ``np.shape(mean)``.
    dtype: optional, a float dtype for the returned values (default float64 if
      jax_enable_x64 is true, otherwise float32).
    key: optional, a PRNG key used as the random key.

  Returns:
    A random array with the specified dtype and with shape given by ``shape`` if
    ``shape`` is not None, or else by ``mean.shape``."""
  ...

@overload
def weibull_min(scale: RealArray, concentration: RealArray, shape: Shape=(), dtype: DTypeLikeFloat=float, key: ArrayLike = None) -> Array: 
  """Sample from a Weibull distribution.

  The values are distributed according to the probability density function:

  .. math::
     f(x;\sigma,c) \propto x^{c - 1} \exp(-(x / \sigma)^c)

  on the domain :math:`0 < x < \infty`, where :math:`c > 0` is the concentration
  parameter, and :math:`\sigma > 0` is the scale parameter.

  Args:
    scale: The scale parameter of the distribution.
    concentration: The concentration parameter of the distribution.
    shape: The shape added to the parameters loc and scale broadcastable shape.
    dtype: The type used for samples.
    key: optional, a PRNG key.

  Returns:
    A jnp.array of samples."""
  ...


__all__ = ['ball', 'bernoulli', 'beta', 'binomial', 'bits', 'categorical', 'cauchy', 'chisquare', 'choice', 'clone', 'dirichlet', 'double_sided_maxwell', 'exponential', 'f', 'fold_in', 'gamma', 'generalized_normal', 'geometric', 'gumbel', 'laplace', 'loggamma', 'logistic', 'lognormal', 'maxwell', 'multinomial', 'multivariate_normal', 'normal', 'orthogonal', 'pareto', 'permutation', 'poisson', 'rademacher', 'randint', 'rayleigh', 'split', 't', 'triangular', 'truncated_normal', 'uniform', 'wald', 'weibull_min']