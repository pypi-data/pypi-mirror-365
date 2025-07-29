# Theme utilities (optional customization)
def dark_mode():
    import seaborn as sns
    import matplotlib.pyplot as plt
    sns.set_theme(style="darkgrid")
    plt.style.use("dark_background")

def light_mode():
    import seaborn as sns
    import matplotlib.pyplot as plt
    sns.set_theme(style="whitegrid")
    plt.style.use("default")
