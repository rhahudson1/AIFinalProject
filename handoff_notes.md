# Handoff notes (project foundation: transition matrix P)

## What was completed

- Implemented the MDP transition probability tensor \(P\) (NumPy) for the reactor control problem.
- Added a standalone validation script to sanity-check \(P\) for each provided reactor JSON.
- Wrote an MDP modeling draft section for the report: `mdp_modeling_draft.md`.

## Where the transition matrix is implemented

- File: `SOURCE_TO_ADJUST/ControlModule.py`
- API:
  - `ControlModule.set_probabilities(probs, n_states=100) -> None`
  - `ControlModule.generate_P() -> np.ndarray`

Usage is two-step: set the probabilities once (from the reactor JSON), then generate \(P\).

## Action order and mapping

Action index order used in \(P[a, s, s']\):

- \(a=0\): decrease
- \(a=1\): maintain
- \(a=2\): increase

Outcome (movement) mapping used:

- decrease: \((-2, -1, 0)\)
- maintain: \((-1, 0, +1)\)
- increase: \((0, +1, +2)\)

Probability order is read from the reactor JSON and must match the movement order above for each action.

In `main.py`, the probabilities are assembled as:

- `probs[0] = reactor.probabilities["decrease"]`
- `probs[1] = reactor.probabilities["maintain"]`
- `probs[2] = reactor.probabilities["increase"]`

So `ControlModule.set_probabilities` expects `probs.shape == (3, 3)`.

## Correct API usage (exact)

1. Build the probabilities array from the reactor JSON in this order:
   - decrease
   - maintain
   - increase

Example:

```python
probs = np.array([
    reactor["probabilities"]["decrease"],
    reactor["probabilities"]["maintain"],
    reactor["probabilities"]["increase"],
], dtype=np.float64)
```

2. Initialize `ControlModule` probabilities:

```python
ControlModule.set_probabilities(probs, n_states=100)
```

3. Generate the transition matrix:

```python
P = ControlModule.generate_P()
```

## Shape of P

- `P.shape == (3, 100, 100)`

Interpretation:

- `P[a, s, s_next]` is the probability of moving to `s_next` when taking action `a` in current state `s`.

## Boundary handling (states 0 and 99)

Boundary clipping is enforced so next states never go below 0 or above 99:

- If `s + movement < 0`, the probability mass is added into next state 0.
- If `s + movement > 99`, the probability mass is added into next state 99.

Because multiple outcomes can clip into the same boundary state, probabilities are accumulated with `+=` rather than assigned.

## Validation added

Validator script:

- File: `SOURCE_TO_ADJUST/validate_transition_matrix.py`

Checks performed:

- `P.shape == (3, 100, 100)`
- No NaNs
- No negative probabilities
- Every row `P[a, s, :]` sums to 1 within \(1e-8\)
- Manual edge cases are exercised (non-zero pattern retrieval):
  - decrease from state 0
  - decrease from state 1
  - maintain from state 0
  - maintain from state 99
  - increase from state 98
  - increase from state 99

## How to run/validate

From `SOURCE_TO_ADJUST/`:

```bash
python validate_transition_matrix.py -i Reactors/R0.json
python validate_transition_matrix.py -i Reactors/R1.json
python validate_transition_matrix.py -i Reactors/R2.json
python validate_transition_matrix.py -i Reactors/R3.json
```

Successful validation produces no output and exits with code 0. Any failure raises an `AssertionError`.

## How to validate my part

From the project root:

```bash
python "SOURCE_TO_ADJUST/validate_transition_matrix.py" -i "SOURCE_TO_ADJUST/Reactors/R0.json"
python "SOURCE_TO_ADJUST/validate_transition_matrix.py" -i "SOURCE_TO_ADJUST/Reactors/R1.json"
python "SOURCE_TO_ADJUST/validate_transition_matrix.py" -i "SOURCE_TO_ADJUST/Reactors/R2.json"
python "SOURCE_TO_ADJUST/validate_transition_matrix.py" -i "SOURCE_TO_ADJUST/Reactors/R3.json"
```

Expected behavior:

- no output
- exit code 0
- if an assertion fails, transition matrix validation failed

## What partners still need to implement

- Cost/reward definition and matrix/tensor \(C\) / \(R\)
- Value Iteration (or other MDP solver) integration into the control logic
- Full control loop that uses demand at each timestep
- Evaluation metrics and experiment scripts
- Experiments/results and final report writeup
- Additional reactor JSONs (e.g., `R4.json`) if required by the assignment

