// Bayesian mixed-effects logistic regression for cooperation decisions.
//
// cooperation ~ opponent_type + communication + opponent_type:communication
//             + game_type + (1 + game_type | pair)
//
// Random effects: correlated random intercept and random slope for game_type
// at the pair level (non-centered parameterization for sampling efficiency).

data {
  int<lower=1> N;                    // total observations
  int<lower=1> J;                    // number of pairs
  array[N] int<lower=0, upper=1> y;  // cooperation decision (0/1)
  vector[N] opponent_type;           // 0 = human, 1 = AI
  vector[N] communication;           // 0 = none, 1 = free-text
  vector[N] game_type;               // 0 = PD, 1 = SH
  array[N] int<lower=1, upper=J> pair_id;  // pair identifier
}

parameters {
  real alpha;                // intercept (log-odds)
  real beta_opp;             // opponent type
  real beta_comm;            // communication
  real beta_inter;           // opponent_type x communication interaction
  real beta_game;            // game type (SH vs PD)

  // Non-centered random effects
  matrix[2, J] z;            // standardized random effects (2 x J)
  vector<lower=0>[2] tau;    // SDs: tau[1] = intercept, tau[2] = slope
  cholesky_factor_corr[2] L_Omega;  // Cholesky of correlation matrix
}

transformed parameters {
  matrix[J, 2] u;            // pair-level random effects: [intercept, slope]
  // Non-centered: u = (diag(tau) * L_Omega * z)'
  u = (diag_pre_multiply(tau, L_Omega) * z)';
}

model {
  // Priors on fixed effects (weakly informative)
  alpha ~ normal(0, 2.5);
  beta_opp ~ normal(0, 2.5);
  beta_comm ~ normal(0, 2.5);
  beta_inter ~ normal(0, 2.5);
  beta_game ~ normal(0, 2.5);

  // Priors on random-effects structure
  tau ~ exponential(1);
  L_Omega ~ lkj_corr_cholesky(2);
  to_vector(z) ~ std_normal();

  // Likelihood
  {
    vector[N] eta;
    for (n in 1:N) {
      int j = pair_id[n];
      eta[n] = alpha + u[j, 1]
             + beta_opp * opponent_type[n]
             + beta_comm * communication[n]
             + beta_inter * opponent_type[n] * communication[n]
             + (beta_game + u[j, 2]) * game_type[n];
    }
    y ~ bernoulli_logit(eta);
  }
}

generated quantities {
  // Recover correlation matrix for reporting
  corr_matrix[2] Omega;
  Omega = multiply_lower_tri_self_transpose(L_Omega);
}
