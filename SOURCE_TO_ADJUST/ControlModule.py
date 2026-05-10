import numpy as np
try:
    import mdptoolbox
except ModuleNotFoundError:
    mdptoolbox = None

class ControlModule:
    _probs: np.ndarray | None = None
    _n_states: int = 100

    def __init__(self):
        pass

    @staticmethod
    def set_probabilities(probs: np.ndarray, n_states: np.int32 = 100) -> None:
        ControlModule._probs = np.asarray(probs, dtype=np.float64)
        ControlModule._n_states = int(n_states)

    @staticmethod
    def generate_P() -> np.ndarray:
        if ControlModule._probs is None:
            raise ValueError("Probabilities not set. Call ControlModule.set_probabilities(probs, n_states) first.")
        probs = ControlModule._probs
        n_states = ControlModule._n_states

        P = np.zeros((3, int(n_states), int(n_states)), dtype=np.float64)

        movements = (
            (-2, -1, 0),
            (-1, 0, 1),
            (0, 1, 2),
        )

        for a in range(3):
            for s in range(int(n_states)):
                for i in range(3):
                    ns = s + movements[a][i]
                    if ns < 0:
                        ns = 0
                    elif ns > int(n_states) - 1:
                        ns = int(n_states) - 1
                    P[a, s, ns] += float(probs[a][i])

        return P

    @staticmethod
    def generate_R(demand_t: float) -> np.ndarray:
        n_states = ControlModule._n_states
        # R matrix with dimensions (Actions, States, States)
        R = np.zeros((3, n_states, n_states), dtype=np.float64)

        #Calculate lower bound power of current state
        for a in range(3):
            for s in range(n_states):
                power_s = s / float(n_states)

                #Check if the action moves us away from target
                penalize = False
                if a == 0 and demand_t > power_s:       # When demand is above decrease power
                    penalize = True
                elif a == 2 and demand_t < power_s:     # When demand is bellow increase power
                    penalize = True

                for ns in range(n_states):
                    #Power lvl of the destination state
                    power_ns = ns / float(n_states)
                    #Absolute distance between demand and destination lvl
                    distance = abs(demand_t - power_ns)
                    # If the action moves away from the target x2 penalty
                    cost = distance * 2.0 if penalize else distance
                    # pymdptoolbox maximizes, so we use negative cost
                    R[a, s, ns] = -cost

        return R


    @staticmethod
    def control_iteration() -> np.int32:
        ...

    @staticmethod
    def control_loop(demand: np.ndarray, 
                     probs: np.ndarray,
                     n_states: np.int32, 
                     n_actions: np.int32,
                     gamma: np.float64) -> np.ndarray:
        return np.zeros_like(a=demand, dtype=np.float64)
