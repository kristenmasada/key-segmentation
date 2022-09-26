#! /usr/bin/env python3
import sys
import os

sys.path.append(os.path.abspath("../"))

from frog.preprocessing.create_tfrecords_kristen import main

if __name__ == "__main__":
    main(sys.argv[1:])
