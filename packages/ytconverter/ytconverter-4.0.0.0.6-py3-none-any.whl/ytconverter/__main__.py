import os
import sys
from pathlib import Path

# Allow running as script or module
sys.path.insert(0, str(Path(__file__).parent.parent))
def main():
  from ytconverter.cli.menu import main_loop
  main_loop()

if __name__ == "__main__":
  main()
