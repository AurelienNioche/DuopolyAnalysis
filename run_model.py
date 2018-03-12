import argparse


def main():




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Run simulations.')
    parser.add_argument('-p0', '--player0', action="store_true", default,
                        help="Re-run nalysis")
    parsed_args = parser.parse_args()

    main(force=parsed_args.force)
