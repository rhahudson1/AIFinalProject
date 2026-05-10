# Import required dependencies
import numpy as np

def MAE(y_true: np.ndarray, y_pred: np.ndarray) -> np.float64:
    """ Implementation of the Mean Absolute Error (MAE) """
    # Mean of the absolute differences
    return np.float64(np.mean(np.abs(y_true - y_pred)))

def MSE(y_true: np.ndarray, y_pred: np.ndarray) -> np.float64:
    """ Implementation of the Mean Squared Error (MSE) """
    # Mean of the squared differences
    return np.float64(np.mean((y_true - y_pred) ** 2))

def R2(y_true: np.ndarray, y_pred: np.ndarray) -> np.float64:
    """ Implementation of the R2 metric """
    # Numerator: SUm of squared errors
    ss_res = np.sum((y_true - y_pred) ** 2)
    #Denominator: Total variance of the actual data
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)

    # Protect against division by zero in case y_true is constant
    if ss_tot == 0:
        return np.float64(0.0)

    return np.float64(1 - (ss_res / ss_tot))

def Corr(y_true: np.ndarray, y_pred: np.ndarray) -> np.float64:
    """ Implementation of the Pearson's Correlation Coefficient """
    # np.corrcoef return a 2x2 correlation matrix
    # The correlation value between y_true and y_pred is at position [0, 1] or [1, 0]
    # Protect the calculation to avoid division by zero or constant identical arrays
    if np.std(y_true) == 0 or np.std(y_pred) == 0:
        return np.float64(0.0)

    correlation_matrix = np.corrcoef(y_true, y_pred)
    return np.float64(correlation_matrix[0, 1])