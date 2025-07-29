import pytest
from classendar.decorator import classendar_base
from datetime import date


class ParentClass:
    def __init__(self, foo_arg=None, **kwargs):
        self.foo_arg = foo_arg
        print(f"Foo initialized with foo_arg={foo_arg}")


@classendar_base
class Foo(ParentClass):
    async def get(self, **kwargs):
        return "Base Foo result"


class Foo_20250701(Foo):
    async def get(self, **kwargs):
        return "Foo_20250701 result"


class Foo_20250801(Foo_20250701):
    async def get(self, **kwargs):
        return "Foo_20250801 result"


class Foo_20250901(Foo_20250801):
    async def get(self, **kwargs):
        result = await super().get(**kwargs)
        return f"Foo_20250801 result + {result}"


@pytest.mark.asyncio
async def test_base_class():
    foo = Foo(foo_arg="test")
    result = await foo.get(version_date=date(2025, 6, 15))  
    assert result == 'Base Foo result'    


@pytest.mark.asyncio
async def test_2nd_layer():
    foo = Foo(foo_arg="test")
    result = await foo.get(version_date=date(2025, 7, 15))  
    assert result == 'Foo_20250701 result'


@pytest.mark.asyncio
async def test_3rd_layer():
    foo = Foo(foo_arg="test")
    result = await foo.get(version_date=date(2025, 8, 1))  
    assert result == 'Foo_20250801 result'


@pytest.mark.asyncio
async def test_reference_base():
    foo = Foo(foo_arg="test")
    result = await foo.get(version_date=date(2025, 9, 1))  
    assert result == 'Foo_20250801 result + Foo_20250801 result'
