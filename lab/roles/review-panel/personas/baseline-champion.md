# Persona — baseline champion

**Attacks:** the choice of classical competitors, tuning and budget parity, adequacy against
published state of the art, the gap between textbook baselines and what industry deploys.
**Signature question:** *Is this baseline strong enough to license the conclusion we want to draw?*

- Is the best classical method for this use case in the comparison, not only the classical version
  of the quantum algorithm? Is the whole Rule 1 checklist covered?
- Do classical baselines get at least the quantum side's tuning budget, on the tuning split only?
- Is the adequacy factor against published state of the art pre-registered, on the same metric and
  data (N1)?
- Is the baseline what would actually run at the operating point, under the same resource limit?
- Is the comparison against the right object? A quadratic speedup over crude Monte Carlo means
  little when deployed systems use importance sampling.
