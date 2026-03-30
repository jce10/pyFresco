from pathlib import Path
from pyfresco.pyfresco import main


if __name__ == "__main__":
    run_dir = Path.cwd()
    main(run_dir=run_dir)