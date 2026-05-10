# Import required dependencies
import numpy as np

class Reactor:
    def __init__(self,
                 model: str,
                 effective_section: np.float64,
                 neutron_flux: np.float64,
                 core_volume: np.float64,
                 fision_energy: np.float64,
                 probabilities: dict):
        """ Constructor of the Reactor class """
        self.model             = model
        self.effective_section = effective_section
        self.neutron_flux      = neutron_flux
        self.core_volume       = core_volume
        self.fision_energy     = fision_energy
        self.probabilities     = probabilities
        self.max_power         = self.compute_max_power()
        self.k                 = self.compute_k()

    def __str__(self) -> str:
        """ Overloading of the native __str__ function to print the class instances """
        _str  = f"Model: {self.model}\n"
        _str += f"Effective section: {self.effective_section} cm^-1\n"
        _str += f"Neutron flux: {self.neutron_flux} neutrons / (cm^2 · s)\n"
        _str += f"Core volume: {self.core_volume} cm^3\n"
        _str += f"Fision energy: {self.fision_energy} J\n"
        _str += f"Probabilities: {self.probabilities}"
        return _str

    def compute_max_power(self) -> np.float64:
        """ Computes the maximum power of a reactor based on its physical features """
        # P_max = Sigma_f * Flux * Volume * Energy_per_fission
        return np.float64(self.effective_section * self.neutron_flux * self.core_volume * self.fision_energy)
    
    def compute_k(self) -> np.float64:
        """ Computes the value of the k-constant """
        # The constant k is defined so that at maximum insertion (B=1) the power is 1 Watt
        # k = ln(P_max)
        return np.float64(np.log(self.max_power))
    
    def compute_power(self, control_bars_insertion: np.float64) -> np.float64:
        """ Computes the power delivered (%) by the reactor based on the % of control-bars inserted """
        # P = P_max * exp(-k * B)
        # We return the percentage relative to max power (0.0 to 1.0)
        p_watts = self.max_power * np.exp(-self.k * control_bars_insertion)
        return np.float64(p_watts / self.max_power)
    
    def compute_control_bars_insertion(self, power: np.float64) -> np.float64:
        """ Computes the % of controls-bars inserted based on the % of power delivered by the reactor """
        # This is the inverse of the power formula. If P = P_max * exp(-k*B)
        # Then B = -ln(P_actual / P_max) / k
        # Since 'power' passed here is already the percentage (0.0 to 1.0),
        # P_actual / P_max is simply the 'power' variable.

        # Protect against log(0)
        p_safe = max(power, 1e-12)
        insertion = -np.log(p_safe) / self.k
        return np.float64(np.clip(insertion, 0.0, 1.0))
