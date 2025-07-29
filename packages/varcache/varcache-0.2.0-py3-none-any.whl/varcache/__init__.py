"""
A simple library that provides a way to store and synchronize Python objects on 
a disk. It can be a good alternative towards SQLite or other solutions that 
seem to be too complicated in your project. Inside `varcache` uses `pickle`.

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
"""

import os
import pickle
from typing import Callable, Any, Optional


class Varcache:
    """
    A cache storage class. It keeps the directory path to store the data and
    implements functions to synchronize the objects' states on the disk.
    """

    def __init__(self, dirpath: str):
        """
        Create a new Varcache instance.
        """
        self._dirpath = dirpath
        self._name_id_mapping = {}
        self._id_name_mapping = {}

    def load(self, name: str, default: Callable) -> Any:
        """
        Load object from the disk if it exists. Otherwise a default object
        will be created by `default` function.
        """
        if name in self._name_id_mapping:
            raise AlreadyLoadedError(name)

        path = self._get_object_path(name)

        if os.path.exists(path):
            with open(path, 'rb') as f:
                obj = pickle.load(f)
        else:
            obj = default()

        self.bind(obj, name)

        return obj

    def save(self, obj: Any, name: Optional[str] = None):
        """
        Save the object to the disk. If the object is not bound, `name` 
        parameter is required, the object will be bound automatically.
        """
        if name is not None:
            self.bind(obj, name)

        obj_id = id(obj)

        if obj_id in self._id_name_mapping:
            name = self._id_name_mapping[obj_id]
            path = self._get_object_path(name)

            with open(path, 'wb') as f:
                pickle.dump(obj, f)

        else:
            raise NotBoundError(obj_id)

    def bind(self, obj: Any, name: str):
        """
        Bind given object to its name in Varcache.
        """
        obj_id = id(obj)

        if name not in self._name_id_mapping:
            self._name_id_mapping[name] = obj_id

        if obj_id not in self._id_name_mapping:
            self._id_name_mapping[obj_id] = name

        if self._name_id_mapping[name] != obj_id:
            raise DuplicateNameError(name)

        if self._id_name_mapping[obj_id] != name:
            raise DuplicateObjectError(obj)

    def unbind(self, obj: Any):
        """
        Unbind the object. It will not be removed, so use `clear` for this
        purpose.
        """
        obj_id = id(obj)

        if obj_id not in self._id_name_mapping:
            raise NotBoundError(obj)

        name = self._id_name_mapping[obj_id]

        del self._id_name_mapping[obj_id]
        del self._name_id_mapping[name]

    def check_name(self, name: str) -> bool:
        """
        Check whether the name is bound.
        """
        return name in self._name_id_mapping

    def check_object(self, obj: Any) -> bool:
        """
        Check whether the object is bound.
        """
        return id(obj) in self._id_name_mapping

    def clear(self, name: str):
        """
        Remove the object from the disk.
        """
        path = self._get_object_path(name)
        if os.path.exists(path):
            os.remove(path)

    def clear_all(self):
        """
        Removes all objects from the disk.
        """
        for name in os.listdir(self._dirpath):
            path = self._get_object_path(name)
            os.remove(path)

        self._name_id_mapping.clear()
        self._id_name_mapping.clear()

    def _get_object_path(self, name):
        return os.path.join(self._dirpath, name)


class VarcacheError(Exception):
    """
    Base Varcache error.
    """
    pass


class DuplicateNameError(VarcacheError):
    """
    Duplicate name error.
    """
    pass


class DuplicateObjectError(VarcacheError):
    """
    Duplicate object error.
    """
    pass


class AlreadyLoadedError(VarcacheError):
    """
    Already loaded error.
    """
    pass


class NotBoundError(VarcacheError):
    """
    Not bound error.
    """
    pass
