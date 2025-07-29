import saftig
from icecream import ic
import matplotlib.pyplot as plt
import numpy as np
import scipy
import cProfile
import timeit

# settings
N = int(1e4)
N_filter = 128
N_channel = 1

PROFILE = True

A = np.random.rand(N_filter, N_filter)

if __name__ == "__main__":

    w, t = saftig.TestDataGenerator([0.1] * N_channel).generate(N)

    # filt = saftig.WienerFilter(N_filter, 0, N_channel)
    # filt = saftig.UpdatingWienerFilter(N_filter, 0, N_channel, 20*N_filter, 20*N_filter)
    # filt = saftig.LMSFilter(N_filter, 0, N_channel, step_scale=0.1)
    filt = saftig.PolynomialLMSFilter(
        N_filter, 0, N_channel, step_scale=0.1, order=3, coefficient_clipping=5
    )
    # filt = saftig.LMSFilterC(N_filter, 0, N_channel, step_scale=0.1)
    # filt = saftig.external.SpicypyWienerFilter(N_filter, 0, N_channel)

    filt.condition(w, t)
    fs_before = np.array(filt.filter_state)
    if PROFILE:
        cProfile.run(
            "pred = filt.apply(w, t, pad=True, update_state=True)", sort="tottime"
        )
        exit()
    else:
        pred = filt.apply(w, t, pad=True, update_state=True)
    fs_after = np.array(filt.filter_state)

    ic((fs_before == fs_after).all())

    ic(filt.filter_state.shape)
    ic(pred.shape)
    ic(pred.shape[0] - t.shape[0])

    ic(saftig.RMS(t[2000:]))
    ic(saftig.RMS((t - pred)[2000:]))
    ic(saftig.residual_amplitude_ratio(t, pred, start=2000))

    plt.figure()
    plt.plot(t, label="target")
    plt.plot(pred, label="prediction")
    plt.plot(pred - t, label="residual")
    plt.legend()

    plt.show()
