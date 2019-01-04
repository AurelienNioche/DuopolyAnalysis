import os

import behavior.demographics
from make_figs import simulation_fig


def demographics_figs():

    # Will create violin plots for gender and scatter plot for age
    behavior.demographics.run(force=False)


def simulation_random_fig():
    simulation_fig(
        force=True,
        # pool simulations are simulations where
        # where vary r
        span_pool=0.33,
        t_max_pool=100,
        t_max_xp=25,
        random_params=True,
        force_params=False,
        fig_name="fig/supplementary_simulation_random.pdf"
    )


def simulation_full_span_fig():
    simulation_fig(
        force=True,
        # pool simulations are simulations where
        # where vary r
        span_pool=1,
        t_max_pool=100,
        t_max_xp=25,
        random_params=False,
        force_params=False,
        fig_name="fig/supplementary_simulation_full_span.pdf"
    )


def main():

    os.makedirs('fig', exist_ok=True)
    demographics_figs()
    simulation_random_fig()
    simulation_full_span_fig()


if __name__ == "__main__":
    main()
