import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from jax.nn import softmax

from .model_spec import ModelSpec
from .renewal_model.basis_functions import Spline, SplineDeriv


def MLR_Ne_numpyro(seq_counts, N, X, X_deriv, tau=None, pred=False, var_names=None):
    _, N_variants = seq_counts.shape
    _, N_features = X.shape

    # Sampling parameters
    def spline_parameters(group, dim_1, dim_2, append_zero=True):
        raw_beta = numpyro.sample(
            f"raw_beta_{group}",
            dist.Normal(0.0, 3.0),
            sample_shape=(dim_1, dim_2),
        )
        if append_zero:
            beta = numpyro.deterministic(
                f"beta_{group}",
                jnp.column_stack(
                    (raw_beta, jnp.zeros(dim_1))
                ),  # All parameters are relative to last column / variant
            )
        else:
            beta = numpyro.deterministic(f"beta_{group}", raw_beta)
        return beta

    beta_variant = spline_parameters(
        "variant", N_features, N_variants - 1, append_zero=True
    )
    beta_Ne = spline_parameters("Ne", N_features, 1, append_zero=False)

    logits = jnp.dot(X, beta_variant)  # Logit frequencies by variant
    freq = numpyro.deterministic("freq", softmax(logits, axis=-1))
    lnNe = numpyro.deterministic("lnNe", jnp.dot(X, beta_Ne).squeeze(-1))
    Ne = numpyro.deterministic("Ne", jnp.exp(lnNe))
    dlnNe = jnp.dot(X_deriv, beta_Ne).squeeze(-1)
    numpyro.deterministic("growth_rate", dlnNe * Ne)

    # Evaluate likelihood
    obs = None if pred else np.nan_to_num(seq_counts)
    # numpyro.sample(
    #     "seq_counts",
    #     dist.DirichletMultinomial(freq / Ne[:, None], total_count=np.nan_to_num(N)),
    #     obs=obs,
    # )

    numpyro.sample(
        "seq_counts",
        dist.DirichletMultinomial(
            freq * jnp.sqrt(Ne[:, None]), total_count=np.nan_to_num(N)
        ),
        obs=obs,
    )

    # Can simplify by taking 0.5 ( jnp.dot(...))

    # Compute growth advantage from model
    if tau is not None:
        delta = numpyro.deterministic("delta", jnp.dot(X_deriv, beta_variant))
        numpyro.deterministic(
            "ga", jnp.exp(delta[:, :-1] * tau)
        )  # Last row corresponds to linear predictor / growth advantage


class MLR_Ne(ModelSpec):
    def __init__(self, tau, s=None, k=None, order=None, ne_model=None):
        # self.ne_model = base_ne_model if ne_model is None else new_model

        self.tau = tau
        self.s = s
        self.k = 10 if k is None or s is not None else k
        self.order = 4 if order is None else order
        self.basis_fn = Spline(s=self.s, order=self.order, k=self.k)
        self.basis_fn_deriv = SplineDeriv(s=self.s, order=self.order, k=self.k)

        self.model_fn = MLR_Ne_numpyro

    def augment_data(self, data: dict) -> None:
        data["X"] = self.basis_fn.make_features(data)
        data["X_deriv"] = self.basis_fn_deriv.make_features(data)
        data["tau"] = self.tau
