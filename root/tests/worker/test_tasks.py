import pytest
from worker.tasks import add

def test_add_task():
    result = add.delay(2, 3)
    assert result.get(timeout=10) == 5  # add task adds two numbers
