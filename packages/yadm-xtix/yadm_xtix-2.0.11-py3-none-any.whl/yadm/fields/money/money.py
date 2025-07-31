""" Field for money.

Use :class:`yadm.fields.money.Money`, as value for money

.. code block: python

    class DocClass(Document):
        money = MoneyField()

    doc = DocClass()
    doc.money = Money('3.14', 'USD')

    db.insert_one(doc)

This code save to MongoDB document:

.. code block: javascript

    {
        id: ObjectId('534272984c78591787e1a964'),
        money: {v: 314, c: 'USD'}
    }
"""
from decimal import Decimal, Context, ROUND_UP, InvalidOperation
from functools import wraps
import random

from yadm.fields.base import Field, DefaultMixin, pass_null
from .currency import DEFAULT_CURRENCY_STORAGE
from yadm.markers import AttributeNotSet


def _checker(method):
    """ Decorator for check type of value.
    """
    @wraps(method)
    def wrapper(self, value):
        if not isinstance(value, Money):
            return NotImplemented

        if self.currency != value.currency:
            raise ValueError("Money {!r} and {!r} must be with the"
                             " same currencies".format(str(self), str(value)))
        return method(self, value)

    return wrapper


def _special_comparison(method):
    """ Decorator for special compression Money with other values.
    """
    @wraps(method)
    def wrapper(self, value):
        if isinstance(value, int):
            # This need to compare Money with 0 only integer
            if value:
                return NotImplemented
            else:
                return method(self.value, value)

        elif isinstance(value, Money):
            if self.currency != value.currency:
                raise ValueError("Money {!r} and {!r} must be with"
                                 " the same currencies".format(self, value))
            else:
                return method(self.value, value.value)

        else:  # pragma: no cover
            return NotImplemented

    return wrapper


class Money:
    _context = Context(rounding=ROUND_UP)

    def __init__(self, value, currency=None):
        if isinstance(value, Money):
            if currency is not None:
                raise TypeError("new Money from another Money not need"
                                " currency {!r} as parameter".format(currency))
            else:
                self._value = value.value
                self._currency = value.currency

        else:
            if currency is None:
                raise TypeError("Currency is not set.")
            else:
                self._currency = currency = DEFAULT_CURRENCY_STORAGE[currency]

            if not isinstance(value, Decimal):
                value = Decimal(value, context=self._context)

            self._value = self.round_decimal(value, currency.precision)

    @classmethod
    def from_cents(cls, cents: int, currency) -> 'Money':
        """ Return new Money object from cents.
        """
        _currency = DEFAULT_CURRENCY_STORAGE[currency]

        # In internal protocols we use cents, with precision 2.
        # Need to be careful with currency without precision or precision more than two
        precision = 2

        delimiter = Decimal(10 ** precision)
        return cls(cents / delimiter, _currency)

    @classmethod
    def from_string(cls, s):
        """
        Class method to create an instance from a formatted string.

        String format:
            "123 USD"
            "123.22 USD"
        """
        v, c = s.strip().split()

        try:
            value = cls(v, c)
        except (KeyError, InvalidOperation, ValueError, TypeError):
            raise ValueError(f"Can't create Money from string {s!r}")

        return value

    @property
    def value(self) -> Decimal:
        return self._value

    @property
    def currency(self):
        return self._currency

    @property
    def total_cents(self) -> int:
        """ Return total cents in this object.
        """

        rounded = self.round_decimal(self.value, self.currency.precision)

        # In internal protocols we use cents, with precision 2.
        # Need to be careful with currency without precision or precision more than two
        precision = 2
        return int(rounded * 10 ** precision)

    @classmethod
    def round_decimal(cls, value: Decimal, precision: int) -> Decimal:
        """
        Rounds a given Decimal value to specified precision.
        """
        precision_decimal = Decimal('1.' + '0' * precision)
        new_value = value.quantize(precision_decimal, cls._context.rounding)

        return new_value

    def __abs__(self):
        return self.__class__(abs(self._value), self.currency)

    @_checker
    def __add__(self, target):
        return self.__class__(self.value + target.value, self.currency)

    @_checker
    def __sub__(self, target):
        return self.__class__(self.value - target.value, self.currency)

    def __neg__(self):
        return Money(-self.value, self.currency)

    def __mul__(self, target):
        if isinstance(target, (int, Decimal)):
            return self.__class__(self.value * target, self.currency)
        else:
            return NotImplemented

    def __rmul__(self, target):
        return self.__mul__(target)

    def __truediv__(self, target):
        if isinstance(target, self.__class__):
            if self.currency == target.currency:
                return self.value / target.value
            else:
                raise ValueError("Money {!r} and {!r} must be with"
                                 " the same currencies".format(self, target))
        else:
            return self.__class__(self.value / target, self.currency)

    def __eq__(self, target):
        if isinstance(target, int) and target == 0:
            return self.value == target
        else:
            return (isinstance(target, self.__class__) and
                    self.value == target.value and
                    self.currency == target.currency)

    @_special_comparison
    def __gt__(self, other):
        return self > other

    @_special_comparison
    def __lt__(self, other):
        return self < other

    @_special_comparison
    def __ge__(self, other):
        return self > other or self == other

    @_special_comparison
    def __le__(self, other):
        return self < other or self == other

    def __bool__(self):
        return bool(self.value)

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        rounded = self.round_decimal(self.value, self.currency.precision)
        return '{} {}'.format(rounded, self._currency.string)

    def __repr__(self):
        return 'Money({!s})'.format(self)

    def to_mongo(self):
        # b/c
        return MoneyField.to_mongo(None, None, self)

    def is_positive(self):
        return self.value > 0

    def is_negative(self):
        return self.value < 0

    def is_zero(self):
        return self.value == 0


class MoneyField(DefaultMixin, Field):
    """ Field to storage money values.
    """
    def get_fake(self, document, faker, depth):  # pragma: no cover
        value = faker.pydecimal(left_digits=5, right_digits=2, positive=True)
        currency = random.choice(['USD', 'EUR', 'RUB', 'GBP', 'IDR'])
        return Money(value, currency)

    @pass_null
    def prepare_value(self, document, value):
        if isinstance(value, Money):
            return value
        else:
            raise TypeError("Only money is allowed for assigment to MoneyField.")

    @pass_null
    def to_mongo(self, document, value):
        return [value.total_cents, value.currency.code]

    @pass_null
    def from_mongo(self, document, data):
        if data is AttributeNotSet:  # pragma: no cover
            return AttributeNotSet

        elif isinstance(data, list):
            value, currency_key = data

            # In internal protocols we use cents, with precision 2.
            # Need to be careful with currency without precision or precision more than two
            return Money.from_cents(value, currency_key)
        else:  # pragma: no cover
            raise TypeError("Incorrect type of value {!r} for Money".format(type(data)))
