cyquant
=======

simple, efficient dimensional analysis

## basics

```python
from cyquant import si, SIUnit

miles = SIUnit(1609.344) * si.meters
marathon_miles = 26 * miles
marathon_miles.quantity  # 26

marathon_meters = marathon_miles.cvt_to(si.meters)
marathon_meters.quantity  # 41842.944
marathon_meters.get_as(miles)  # 26
marathon_meters.get_as(si.newton_meters)  # ValueError
marathon_miles == marathon_meters  # True
```

## approximation & tolerances

```python
# absolute tolerance
marathon_miles.a_approx(marathon_meters, atol=1e-9)  # True

# relative tolerance
marathon_miles.r_approx(marathon_meters, rtol=1e-9)  # True

# quantity tolerance
marathon_miles.q_approx(marathon_meters, qtol=1 * si.millimeters)
```

## normalized string output

```python
from cyquant.format_quantity import show_quantity
show_quantity(marathon_miles)  # 4.184e+04 m
```

## with attrs

```python
from cyquant import si, converter
from cyquant import Quantity as Q
from attrs import define, field

@define
class Foo:
    mass: Q = field(converter=converter(si.kilograms, promotes=True))
    size: Q = field(converter=converter(si.meters ** 3))

    def liters(self):
        return self.size.get_as(si.liters)

foo1 = Foo(mass=10, size=1 * si.meters ** 3)
foo2 = Foo(mass=10 * si.kilograms, size=1000000000 * si.millimeters ** 3)
assert foo1 == foo2

foo3 = Foo(mass=10, size=10) # TypeError
```