#!/usr/bin/env -S uv run --script

from edc_test_settings.func_main import func_main2

if __name__ == "__main__":
    func_main2("tests.test_settings", "edc_form_describer.tests")
