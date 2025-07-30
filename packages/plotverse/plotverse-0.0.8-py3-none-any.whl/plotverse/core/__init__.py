import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Re-export all pandas functions and classes
__all__ = pd.__all__ if hasattr(pd, '__all__') else dir(pd)
globals().update({k: getattr(pd, k) for k in __all__})

# Prefix matplotlib.pyplot functions with 'plt_'
for fn in dir(plt):
    if not fn.startswith("_"):
        globals()[f"plt_{fn}"] = getattr(plt, fn)
        __all__.append(f"plt_{fn}")

# Prefix seaborn functions with 'sns_'
for fn in dir(sns):
    if not fn.startswith("_"):
        globals()[f"sns_{fn}"] = getattr(sns, fn)
        __all__.append(f"sns_{fn}")
