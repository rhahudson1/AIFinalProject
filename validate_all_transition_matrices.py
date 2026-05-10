import subprocess
import sys


def main() -> None:
    reactors = (
        "SOURCE_TO_ADJUST/Reactors/R0.json",
        "SOURCE_TO_ADJUST/Reactors/R1.json",
        "SOURCE_TO_ADJUST/Reactors/R2.json",
        "SOURCE_TO_ADJUST/Reactors/R3.json",
    )

    for reactor_path in reactors:
        result = subprocess.run(
            [
                sys.executable,
                "SOURCE_TO_ADJUST/validate_transition_matrix.py",
                "-i",
                reactor_path,
            ],
            check=False,
        )
        if result.returncode != 0:
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()

