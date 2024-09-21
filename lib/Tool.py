from typing import Self

class Vector2:
	@staticmethod
	def fromTuple(tup: tuple[float, float]) -> Self:
		return Vector2(tup[0], tup[1])
	
	def	__init__(self, x: float = 0, y: float = 0) -> None:
		self.x = x
		self.y = y
	
	def __add__(self, v2: Self) -> Self: # 向量+
		if isinstance(v2, Vector2): return Vector2(self.x + v2.x, self.y + v2.y)
		return NotImplemented
	
	def __sub__(self, v2: Self) -> Self: # 向量-
		if isinstance(v2, Vector2): return Vector2(self.x - v2.x, self.y - v2.y)
		return NotImplemented
	
	def __mul__(self, c: float) -> Self: # 向量*
		return Vector2(self.x * c, self.y * c)
	
	def __truediv__(self, c: float) -> Self: # 向量/
		return Vector2(self.x / c, self.y / c)
	
	def tup(self) -> tuple[float, float]: # 轉 tuple
		return (self.x, self.y)

def inRange(value: float, start: float, end: float) -> bool: # value 是否介於 start 和 end 之間
	if start <= end: return value >= start and value <= end
	return value >= end and value <= start
