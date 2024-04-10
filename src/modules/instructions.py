COMMENT_SYMBOL = '#'

class Instruction:
  def __init__(self, line):
    self.label, self.mnemonic, self.operands, self.comment = self.__tokenize(line)

  def get_tokens(self):
    return self.label, self.mnemonic, self.operands, self.comment

  # Splits the line in 4 fields: Label, Mnemonic, Operands and Comment
	# Label: String, Mnemonic: String, Operands: List(String), Comment: String
	# In case of a field that is not present in the line it would asign `None` to it
  def __tokenize(self, line):
    label = None

    # Extract the comment of the tokens
    raw_tokens = line.split(COMMENT_SYMBOL, 1)
    comment = raw_tokens[1] if len(raw_tokens) > 1 else None

    # Handle the Tokens (Excluding the comment)
    tokens = raw_tokens[0].replace(',',' ').split()
    # Optional label
    if len(tokens) > 0 and tokens[0].endswith(":"):
      label = tokens[0]
      # Deleting the label makes the tokens[0] the next field, 
      # this way whether the label exists or not is irrelevant 
      # to the next steps
      del tokens[0]

    mnemonic = tokens[0]  if len(tokens) > 0 else None
    operands = tokens[1:] if len(tokens) > 1 else []

    return label, mnemonic, operands, comment
