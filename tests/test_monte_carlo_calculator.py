from lib import monte_carlo_calculator

def monte_carlo_paths(S_0, T, r, q, sigma, steps, N):
    dt = T / steps
    logS_T = np.log(S_0) + np.cumsum(
        (
            (r - q - sigma ** 2 / 2) * dt
            + sigma * np.sqrt(dt) * np.random.normal(size=(steps, N))
        ),
        axis=0,
    )
    return np.exp(logS_T)

def test_monte_carlo_paths():
    S_0 = 148.19
    T = 1
    r = 0.05
    q = 0.0056
    sigma = 0.4676
    steps = 100
    N = 10000

    #assert [[0]] == monte_carlo_calculator.monte_carlo_paths(S_0, T, r, q, sigma, steps, N)

