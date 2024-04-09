class UndefinedMnemonic(Exception):
	mnemonic: str
	file: str 
	line_number: int
	line: str
	
	def __init__(self, mnemonic: str, file: str, line_number: int, line: str, *args: object) -> None:
		super().__init__(*args)
		self.mnemonic = mnemonic
		self.file = file
		self.line_number = line_number
		self.line = line
	
	def __str__(self) -> str:
		return f"ERROR: Undefined Mnemonic({self.mnemonic})\tIn file({self.file}) at line({self.line_number})\t\t{self.line}"

class InvalidSegmentContent(Exception):
	segment: str
	invalid_content: str
	
	def __init__(self, segment: str, invalid_content: str, *args: object) -> None:
		super().__init__(*args)
		self.segment = segment
		self.invalid_content = invalid_content
	
	def __str__(self) -> str:
		return f"ERROR: Invalid Segment Content In Segment `{self.segment}`\tInvalid Content: {self.invalid_content}"
