import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from jax import jit, lax
from jax.nn import softmax
from numpyro.contrib.control_flow import scan

from .model_spec import ModelSpec
from .renewal_model.basis_functions import Spline, SplineDeriv


def compute_diffusion(freq, Ne):
    sigma = -jnp.sqrt((freq * freq[:, None]) * jnp.reciprocal(Ne))
    sigma = jnp.fill_diagonal(
        sigma, jnp.sqrt(freq * (1 - freq) * jnp.reciprocal(Ne)), inplace=False
    )
    return sigma


# @jit
# def simulate_frequency(beta, freq0, Ne, noise):
#     def _freq_step(freq, xs):
#         Ne, noise = xs
#         diffusion = compute_diffusion(freq, Ne)
#         drift = jnp.dot(beta[:, None] - beta, freq) * freq
#         freq_next = freq + drift + diffusion @ noise
#         freq_next = jnp.clip(freq_next, 1e-12, 1.0 - 1e-12)
#         freq_next = freq_next / freq_next.sum()
#         return freq_next, freq_next
#
#     _, freq = lax.scan(_freq_step, xs=(Ne, noise), init=freq0)
#     return jnp.vstack((freq0[None, :], freq))


def simulate_frequency(beta, freq0, Ne, noise):
    def transition(freq, xs):
        Ne, noise = xs
        drift = jnp.dot(beta[:, None] - beta, freq) * freq
        freq_next = freq + drift
        # freq_next = numpyro.sample("freq", dist.Dirichlet(freq * jnp.sqrt(Ne)))
        diffusion = compute_diffusion(freq, Ne)
        freq_next = numpyro.sample("freq", dist.Normal(freq, diffusion))

        # Normalize
        freq_next = jnp.clip(freq_next, 1e-12, 1.0 - 1e-12)
        freq_next = freq_next / freq_next.sum()

        return freq_next, freq_next

    _, freq = scan(transition, xs=(Ne, noise), init=freq0)
    return freq


def MLR_Ne_numpyro(seq_counts, N, X, X_deriv, tau=None, pred=False, var_names=None):
    N_time, N_variants = seq_counts.shape
    _, N_features = X.shape

    # Sampling parameters
    def sample_normal_parameters(group, dim_1, dim_2, append_zero=True):
        raw_beta = numpyro.sample(
            f"raw_beta_{group}",
            dist.Normal(0.0, 1.0),
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

    # Sample initial frequency and relative fitness
    raw_alpha_variant = numpyro.sample(
        "raw_alpha_variant", dist.Normal(0.0, 5.0), sample_shape=(N_variants - 1,)
    )
    alpha_variant = jnp.append(raw_alpha_variant, 0.0)
    freq0 = softmax(alpha_variant)
    # freq0 = numpyro.sample("freq0", dist.Dirichlet(jnp.ones(N_variants)))

    raw_beta_variant = numpyro.sample(
        "raw_beta_variant", dist.Normal(0.0, 3.0), sample_shape=(N_variants - 1,)
    )
    beta_variant = jnp.append(raw_beta_variant, 0.0)

    # Sampling Ne
    base_Ne = jnp.log(1e4)
    beta_Ne = sample_normal_parameters("Ne", N_features, 1, append_zero=False)
    lnNe = numpyro.deterministic("lnNe", jnp.dot(X, beta_Ne).squeeze(-1))
    Ne = numpyro.deterministic("Ne", base_Ne * jnp.exp(lnNe))
    dlnNe = jnp.dot(X_deriv, beta_Ne).squeeze(-1)
    numpyro.deterministic("growth_rate", dlnNe * Ne)

    # Simulating frequency
    # noise = numpyro.sample(
    #     "noise", dist.Normal(0.0, 1.0), sample_shape=(N_time, N_variants)
    # )
    noise = jnp.zeros((N_time - 1, N_variants))

    # freq = numpyro.deterministic(
    #     "freq", simulate_frequency(beta_variant, freq0, Ne[1:], noise)
    # )
    freq = simulate_frequency(beta_variant, freq0, Ne, noise)
    freq = freq / freq.sum(axis=-1, keepdims=True)
    # print(freq.sum(axis=-1))
    # print(jnp.isnan(freq).mean())
    # print((freq < 0).sum())
    # print((freq == 0).sum())
    # print(jnp.sum(freq, axis=-1))

    # Evaluate likelihood
    obs = None if pred else np.nan_to_num(seq_counts)
    numpyro.sample(
        "seq_counts",
        dist.Multinomial(probs=freq, total_count=np.nan_to_num(N)),
        obs=obs,
    )

    # numpyro.sample(
    #     "seq_counts",
    #     dist.DirichletMultinomial(
    #         freq * jnp.sqrt(Ne[:, None]), total_count=np.nan_to_num(N)
    #     ),
    #     obs=obs,
    # )

    # Compute growth advantage from model
    if tau is not None:
        delta = numpyro.deterministic("delta", beta_variant)
        numpyro.deterministic(
            "ga", jnp.exp(delta[:-1] * tau)
        )  # Last row corresponds to linear predictor / growth advantage


class MLR_Ne_2(ModelSpec):
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
