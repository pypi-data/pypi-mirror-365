import numpy


class StructureOfArrays:
    """
    Group multiple arrays together and allow operations on all arrays
    simultaneously. Supports numpy operations as if it were a 1-d array.

    Avoid using instance member variables that are not listed as array members,
    since they will not be copied during operations. Instead, use class member
    variables.
    """

    def __init__(self, n=1):
        self._n = n

    @classmethod
    def _get_array_member_names(cls):
        raise NotImplementedError()

    def __len__(self):
        return self._n

    @property
    def size(self):
        return self._n

    @property
    def ndim(self):
        return 1

    @property
    def shape(self):
        return (self._n,)

    def __setattr__(self, name, value):
        cls = type(self)
        if hasattr(cls, name):
            # Static member
            return super().__setattr__(name, value)

        if hasattr(self, name):
            # Only set once
            raise AttributeError("Member already initialized!")
        if name in ["_n"]:
            # Special members
            return super().__setattr__(name, value)
        if name not in self._get_array_member_names():
            # Check member
            raise AttributeError(
                "Member `" + name + "` not listed in `_get_array_member_names`!"
            )
        return super().__setattr__(name, value)

    @classmethod
    def get_common_names(cls, other):
        """Returns array member names common to both classes."""
        return list(
            set(cls._get_array_member_names()) & set(other._get_array_member_names())
        )

    def update(self, other, names=None):
        """Copy fields from other."""
        if names is None:
            names = self.get_common_names(other)
        for name in names:
            getattr(self, name)[...] = getattr(other, name)

    @classmethod
    def convert(cls, other, **kwargs):
        """Create from other class."""
        self = cls(len(other))
        self.update(other, **kwargs)
        return self

    def _get_indices(self, key):
        indices = numpy.arange(len(self))[key]
        indices = numpy.reshape(indices, [-1])
        return indices

    def __getitem__(self, key):
        """Supports numpy style indexing as if object were 1-d array."""
        assert not isinstance(key, tuple), "Key must be 1-d."

        cls = type(self)
        result = cls(numpy.arange(len(self))[key].size)
        names = self._get_array_member_names()
        for name in names:
            getattr(result, name)[:] = getattr(self, name)[key]
        return result

    def __setitem__(self, key, other):
        """Supports numpy style assignment as if object were 1-d array."""
        assert not isinstance(key, tuple), "Key must be 1-d."

        names = self.get_common_names(other)
        for name in names:
            getattr(self, name)[key] = getattr(other, name)

    def assign(self, key, other, other_key):
        """
        Equivalent to
            self[key] = other[other_key]
        """
        assert not isinstance(key, tuple), "Key must be 1-d."
        assert not isinstance(other_key, tuple), "Key must be 1-d."

        names = self.get_common_names(other)
        for name in names:
            getattr(self, name)[key] = getattr(other, name)[other_key]

    @classmethod
    def combine(cls, other_list):
        """Combine list of objects into single object.

        Concatenates all member variables along first dimension.
        """
        other_list = list(other_list)
        if len(other_list) == 0:
            return cls(0)
        n = numpy.sum([len(x) for x in other_list])
        self = cls(n)
        offset = 0
        for i in range(len(other_list)):
            other = other_list[i]
            self[offset : offset + len(other)] = other
            offset += len(other)
        return self
