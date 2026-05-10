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
                    R[a, s, ns] = 1.0 -cost

        return R


    @staticmethod
    def control_iteration(demand_t: float, current_state: int, P: np.ndarray, gamma: float) -> np.int32:
        # Safety check to make sure the library is installed
        if mdptoolbox is None:
            raise ImportError("The pymdptoolbox library is missing. Run: pip install pymdptoolbox")
        # Generate the R matrix
        R = ControlModule.generate_R(demand_t)

        # Setup and run the value iteration algorithm
        vi = mdptoolbox.mdp.ValueIteration(P, R, discount=gamma, epsilon=0.0001) # We set a small epsilon to ensure the solver is precise
        vi.run()

        # Extract optimal policy
        optimal_action = vi.policy[current_state]

        return np.int32(optimal_action) # Return it as an integer

    @staticmethod
    def control_loop(demand: np.ndarray, 
                     probs: np.ndarray,
                     n_states: np.int32, 
                     n_actions: np.int32,
                     gamma: np.float64) -> np.ndarray:
        # Setup the MDP foundation
        ControlModule.set_probabilities(probs, n_states)
        P = ControlModule.generate_P()

        # Prepare the response array
        response = np.zeros_like(demand, dtype=np.float64)

        # Start the simulation at state 0
        current_state = 0

        # Iterate through the demand curve
        for t in range(len(demand)):
            demand_t = float(demand[t])

            # Get the optimal action for this step
            action = ControlModule.control_iteration(demand_t, current_state, P, float(gamma))

            # Use random.choice to simulate reactor uncertainty
            # We pick the next state based on the probabilities in P matrix
            next_state = np.random.choice(int(n_states), p=P[action, current_state, :])

            # Update current state for the next second
            current_state = next_state

            # Store the resulting power level (0.0 to 1.0)
            response[t] = current_state / float(n_states)

        return response
