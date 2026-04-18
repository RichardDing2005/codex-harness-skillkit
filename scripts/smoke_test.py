#!/usr/bin/env python3
import runpy
runpy.run_path(__file__.replace("smoke_test.py", "self_check.py"), run_name="__main__")
