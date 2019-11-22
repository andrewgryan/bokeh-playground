# Infinite recursion

It's easily done to modify data in a callback that
is listening for the modification of such data

```python

def callback(attr, old, new):
    source.data = ... # Trigger change

source.on_change("data", callback)
```

In simple scripts this is easily avoidable but in
larger systems with multiple moving parts it becomes
more tricky to guard against
