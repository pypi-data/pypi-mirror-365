# varcache

A simple library that provides a way to store and synchronize Python objects on a disk. It can be a good alternative towards SQLite or other solutions that seem to be too complicated in your project. Inside `varcache` uses `pickle`.

## Installation

```
pip install varcache
```

## Basic example

```python
from varcache import Varcache

# Configure the drectory to save
vcache = Varcache(dirpath='./storage')

# Load and save example
obj1 = vcache.load(name='obj1', default=dict)
obj1['x'] = 25
vcache.save(obj1)

# Binding example
obj2 = []
vcache.bind(obj2, name='obj2')
obj2.append(36)
vcache.save(obj2)

# Plain save
obj3 = {2, 3, 5, 7}
vcache.save(obj3, name='obj3')
```
