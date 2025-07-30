# DumPy: NumPy except it's OK if you're dum

DumPy is an interface for (Jax's version) NumPy that tries to avoid all the endless sharp corners.

Example usage:

```python
import dumpy as dp
A = dp.Array([0,1,2])
B = dp.Array([0,10])
C = dp.Slot()
C['i','j'] = A['i'] + B['j']
C
```

This results in

```
Slot([[ 0 10]
      [ 1 11]
      [ 2 12]], shape=(3, 2))
```

See [dynomight.net/dumpy](https://dynomight/dumpy) for full details.