# flexfail

**Flexible failures collector with different collecting strategies.**

`flexfail` provides a consistent and reusable way to collect, and handle failures.
Useful in data processing, form validation, and other contexts where soft-failing logic is needed.

---

## Justification

Why? Imagine you're processing a batch of data sent from a user and want to return a meaningful error description
if something goes wrong. Suppose the data contains 3 different errors in separate places. In a naive implementation,
you might return only one error per request. This would force the user to resubmit the request multiple times
to fix everything.

This library aims to make error collection simpler, clearer, and more flexible.

It allows you to collect **all errors in the data at once**, if needed - or just return the **first encountered error**.
You may even choose to **skip invalid values silently**. This behavior is controlled by **predefined error collection
strategies** (see examples below).

Moreover, in our example, user may choose what strategy is more suitable for them.

---

## Installation

```shell
pip install flexfail
```

---

## Examples

### Prerequisites before strategies overview

Below is a simple example of how `flexfail` can be used to wrap a function and
handle failures using different strategies:

```python
from flexfail import ErrorCollector, ErrorCollectorStrategy
from flexfail.exceptions import FlexFailException, FailFastException


# Let's assume, negative values are impossible to process, as the values are checkouts, for instance.
checkouts = [10, 20, -30, -40, 50, 'spam']


def process_check(value: float):
    if not isinstance(value, (float, int)):
        raise FlexFailException(data={'description': 'Checkout value is not a number!', 'value': value})
    if value < 0:
        raise FlexFailException(data={'description': 'Checkout value was below zero!', 'value': value})
    print(f'Check with amount {value}$ was successfully processed!')


def process_all_with_strategy(strategy: ErrorCollectorStrategy):
    error_collector = ErrorCollector(process_check, strategy)
    try:
        for _ in checkouts:
            error_collector.call(_)
    except FailFastException:
        pass
    print(f'Collected errors:')
    for error in error_collector.errors:
        print(error.data)
```

Please, note, only `FlexFailException` is safe to raise. If you need any other exception to be collected, just wrap it,
using the `data`. You'll be able to access it later. Example:

```python
raise FlexFailException(data={'my_wrapped_exception': RuntimeError('Some custom error!')})
```

### Strategy `skip`

Force bypass all the errors and not even collect them.

```python
process_all_with_strategy(ErrorCollectorStrategy.skip)
```

Results into:

```txt
Check with amount 10$ was successfully processed!
Check with amount 20$ was successfully processed!
Check with amount 50$ was successfully processed!
Collected errors:
```

### Strategy `fail_fast`

Raise on first error occurs and collect only it.

```python
process_all_with_strategy(ErrorCollectorStrategy.fail_fast)
```

Results into:

```txt
Check with amount 10$ was successfully processed!
Check with amount 20$ was successfully processed!
Collected errors:
{'description': 'Checkout value was below zero!', 'value': -30}
```

### Strategy `try_all`

Collect all the errors.

```python
process_all_with_strategy(ErrorCollectorStrategy.try_all)
```

Results into:

```txt
Collected errors:
{'description': 'Checkout value was below zero!', 'value': -30}
{'description': 'Checkout value was below zero!', 'value': -40}
{'description': 'Checkout value is not a number!', 'value': 'spam'}
```
