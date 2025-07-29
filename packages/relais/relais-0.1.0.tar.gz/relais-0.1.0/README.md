# relais

A practical tool for managing async pipelines.

# usage

```py
import relais as r

pipeline = range(10) | r.Map(lambda x: x * 2) | r.Filter(lambda x: x % 2 == 0) | list
await pipeline.run()
```
