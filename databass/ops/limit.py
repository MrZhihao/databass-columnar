from ..baseops import *
from ..exprs import *
from ..db import Database
from ..schema import *
from ..tuples import *
from ..util import cache, OBTuple
from itertools import chain
from ..columns import ListColumns
from pyarrow import compute

class Limit(UnaryOp):
  def __init__(self, c, limit, offset=0):
    """
    @c            child operator
    @limit        number of tuples to return
    """
    super(Limit, self).__init__(c)
    self.limit = limit
    if isinstance(self.limit, numbers.Number):
      self.limit = Literal(self.limit)

    self._limit = int(self.limit(None).as_py())
    if self._limit < 0:
      raise Exception("LIMIT must not be negative: %d" % l)

    self.offset = offset or 0
    if isinstance(self.offset, numbers.Number):
      self.offset = Literal(self.offset)

    self._offset = int(self.offset(None).as_py())
    if self._offset < 0:
      raise Exception("OFFSET must not be negative: %d" % o)

  def get_col_up_needed(self, info=None):
    return self.p.get_col_up_needed()

  def hand_in_result(self):
    handin_res = self.c.hand_in_result()
    if handin_res.is_terminate() or self._limit == 0:
      return ListColumns(self.schema, None)
    return ListColumns(self.schema, [col.slice(offset=self._offset,length=self._limit) for col in handin_res])

  def __str__(self):
    return "LIMIT(%s OFFSET %s)" % (self.limit, self.offset)


