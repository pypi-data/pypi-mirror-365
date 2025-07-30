# time_measure
A tiny helper to measure execution time of a callable to ease your performance checks.

# Usage examples

Decorate your function or method with `async_measure_time` and see logs for execution time 
measures after your function is fnished:

```
from measure_decorator import async_measure_time

@async_measure_time
async def coro_that_runs_long(*args, **kwargs):
    ...
```

Whenever the `coro_that_runs_long` is done, you can see the following in your app logs:

`Func: coro_that_runs_long. Elapsed time in seconds: 0.10037329500482883`

Happy debugging!
