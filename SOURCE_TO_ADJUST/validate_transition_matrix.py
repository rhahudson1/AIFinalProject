import argparse
import json
import numpy as np

from Reactor import Reactor
from ControlModule import ControlModule


def validate_P(P: np.ndarray, n_states: int = 100, n_actions: int = 3) -> None:
    assert isinstance(P, np.ndarray)
    assert P.shape == (n_actions, n_states, n_states), P.shape
    assert not np.isnan(P).any()
    assert np.all(P >= 0.0)

    for a in range(n_actions):
        for s in range(n_states):
            total = float(P[a, s, :].sum())
            assert abs(total - 1.0) < 1e-8, (a, s, total)

    return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-reactor", "-i", required=True, type=str)
    args = parser.parse_args()

    with open(args.input_reactor, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    reactor = Reactor(
        model=json_data["model"],
        effective_section=float(json_data["effective_section"]),
        neutron_flux=float(json_data["neutron_flux"]),
        core_volume=float(json_data["core_volume"]),
        fision_energy=float(json_data["fision_energy"]),
        probabilities=dict(json_data["probabilities"]),
    )

    probs = np.array(
        [
            reactor.probabilities["decrease"],
            reactor.probabilities["maintain"],
            reactor.probabilities["increase"],
        ],
        dtype=np.float64,
    )

    ControlModule.set_probabilities(probs=probs, n_states=np.int32(100))
    P = ControlModule.generate_P()
    validate_P(P)

    def only_expected_nonzero(a: int, s: int, expected: dict[int, float]) -> None:
        expected_nz = {k: v for k, v in expected.items() if float(v) > 0.0}
        row = P[a, s, :]
        idx = np.where(row > 0.0)[0]
        assert set(int(i) for i in idx) == set(expected_nz.keys()), (a, s, idx, expected)
        for k, v in expected_nz.items():
            assert abs(float(row[k]) - float(v)) < 1e-12, (a, s, k, float(row[k]), float(v))

    dec = probs[0]
    mai = probs[1]
    inc = probs[2]

    only_expected_nonzero(0, 0, {0: float(dec[0] + dec[1] + dec[2])})
    only_expected_nonzero(0, 1, {0: float(dec[0] + dec[1]), 1: float(dec[2])})

    only_expected_nonzero(1, 0, {0: float(mai[0] + mai[1]), 1: float(mai[2])})
    only_expected_nonzero(1, 99, {98: float(mai[0]), 99: float(mai[1] + mai[2])})

    only_expected_nonzero(2, 98, {98: float(inc[0]), 99: float(inc[1] + inc[2])})
    only_expected_nonzero(2, 99, {99: float(inc[0] + inc[1] + inc[2])})


if __name__ == "__main__":
    main()

