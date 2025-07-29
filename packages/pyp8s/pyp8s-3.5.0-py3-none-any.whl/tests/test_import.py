#!/usr/bin/env python3
# pylint: disable=line-too-long, missing-function-docstring, logging-fstring-interpolation
# pylint: disable=too-many-locals, broad-except, too-many-arguments, raise-missing-from
"""
    pyp8s module
"""

import pytest

from pyp8s import MetricsHandler


def test_init():
    MetricsHandler.init("calls", "counter", "Number of calls I've received")
    MetricsHandler.init("doorbells", "counter", "Number of doorbells I've answered")
    MetricsHandler.init("yawns", "counter", "Quite self-explanatory")

def test_inc_simple():
    MetricsHandler.inc("calls", 1)


def test_inc_multilabel():
    MetricsHandler.inc("calls", 1, more="labels", mooore="mooooore")


def test_inc_and_get_metrics():
    MetricsHandler.inc("calls", 1, go="labels", labels="rule")
    excepted_metric_key = "calls"
    metrics = MetricsHandler.get_metrics()

    print(metrics)

    assert excepted_metric_key in metrics


def test_set_and_get_metrics():
    MetricsHandler.set("doorbells", 18, kg="yes", lbs="no")
    excepted_metric_key = "kg_yes_lbs_no"
    metrics = MetricsHandler.get_metrics()
    labelsets = metrics['doorbells'].get_labelsets()

    assert excepted_metric_key in labelsets


@pytest.mark.xfail()
def test_double_start():
    MetricsHandler.serve()
    MetricsHandler.serve()
