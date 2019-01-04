import os

import behavior.demographics


def demographics_figs():

    # Will create violin plots for gender and scatter plot for age
    behavior.demographics.run(force=False)


def main():

    os.makedirs('fig', exist_ok=True)
    demographics_figs()


if __name__ == "__main__":
    main()
