#!/usr/bin/env python3

import sys
import doctest

sys.setrecursionlimit(10_000)

# NO ADDITIONAL IMPORTS!

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(x):
  """
  Helper function: given a string, convert it to an integer or a float if
  possible; otherwise, return the string itself

  >>> number_or_symbol('8')
  8
  >>> number_or_symbol('-5.32')
  -5.32
  >>> number_or_symbol('1.2.3.4')
  '1.2.3.4'
  >>> number_or_symbol('x')
  'x'
  """
  try:
    return int(x)
  except ValueError:
    try:
      return float(x)
    except ValueError:
      return x


def tokenize(source):
  """
  Splits an input string into meaningful tokens (left parens, right parens,
  other whitespace-separated values).  Returns a list of strings.

  Arguments:
      source (str): a string containing the source code of a Scheme
                    expression
  """
  results_list = []

  row_list = source.split('\n')

  for row in row_list:
    str_frag = ''
    for i in range(len(row)):
      if row[i] == '(' or row[i] == ')' or row[i] == ';' or row[i] == ' ':
        if len(str_frag) != 0:
          results_list.append(str_frag)
          str_frag = ''
        if row[i] == '(':
          results_list.append('(')          
        if row[i] == ')':
          results_list.append(')')
        if row[i] == ';':
          break

      else:
        str_frag = str_frag + row[i]
        if i == len(row) - 1:
          results_list.append(str_frag)

  return results_list               

def parse(tokens):
  """
  Parses a list of tokens, constructing a representation where:
      * symbols are represented as Python strings
      * numbers are represented as Python ints or floats
      * S-expressions are represented as Python lists

  Arguments:
      tokens (list): a list of strings representing tokens
  """
  if tokens[0] == ')' or tokens.count('(') != tokens.count(')') or (len(tokens) > 1 and '(' not in tokens):
    raise SchemeSyntaxError

  def parse_expression(index):
    token = tokens[index]
    if token == '(':
      sub_list = []
      #count number of open parantheses
      open_p = 1 
      sub_idx = index

      if tokens[index+1] == ")":
        return [], index + 2

      while index < len(tokens) - 1:
          
        if tokens[index+1] == ")":
          open_p -=1
        elif tokens[index+1] == "(":
          open_p +=1
        #if we finally close the parantheses, we stop the list
        if open_p == 0:
          break
        
        try:
          subcomponent,sub_idx = parse_expression(index + 1)
        except:
          sub_idx +=1
          break
        if subcomponent != ')': 
          sub_list.append(subcomponent)
        if subcomponent == ')' and tokens[index] == '(':
          sub_list.append([])
        index = sub_idx - 1  
      return sub_list, sub_idx

    else:    
      return number_or_symbol(token), index + 1
    
  #return parsed_expression
  parsed_expression, start = parse_expression(0)
  return parsed_expression

######################
# Built-in Functions #
######################

def islist(arg):
  if arg == 'nil':
    return '#t'
  if isinstance(arg, Pair):
    return islist(arg.cdr)
  return '#f'

def list_length(cons_list):
  if islist(cons_list) == '#f':
    raise SchemeEvaluationError
  if cons_list == 'nil':
    return 0
  else:
    return 1 + list_length(cons_list.cdr)

def list_ref(cons_list, index):
  if cons_list == 'nil':
    raise SchemeEvaluationError

  if islist(cons_list) == '#f':
    if isinstance(cons_list, Pair) and index == 0:
      return cons_list.car
    else:
      raise SchemeEvaluationError
  
  else:
    if index == 0:
      return cons_list.car
    else:
      return list_ref(cons_list.cdr, index - 1)

def list_concat(tons_of_list):
  
  if tons_of_list == 'nil' or len(tons_of_list) == 0:
    return 'nil'
  if len(tons_of_list) == 1:
    if islist(tons_of_list[0]) == '#f':
      raise SchemeEvaluationError
    else:
      return create_copy(tons_of_list[0])
  else:
    last = tons_of_list[len(tons_of_list) - 1]
    sec_last = tons_of_list[len(tons_of_list) - 2]
    
    if islist(last) == '#t' and islist(sec_last) == '#t':
      last = create_copy(last)
      sec_last = create_copy(sec_last)
      if last =="nil":
        cat_list = sec_last
      elif sec_last =="nil":
        cat_list = last
      else:
        cat_list = concat_two_list(sec_last, last)
      if len(tons_of_list) == 2:
        return cat_list
      else:
        
        return list_concat(tons_of_list[:(len(tons_of_list) - 2)] + [cat_list])
    else:
      raise SchemeEvaluationError

# append helper functions
def create_copy(cons):
# create a copy of the list instance
  if cons == 'nil':
    return 'nil'
  elif cons.cdr == 'nil':
    return Pair(cons.car, cons.cdr)
  else:
    return Pair(cons.car, create_copy(cons.cdr))

def concat_two_list(cons1, cons2):
  # cons1 + cons2
  if cons1 == 'nil' and cons2 == 'nil':
    return 'nil'
  if cons1 == 'nil':
    return Pair('nil', cons2)
  elif cons1.cdr == 'nil':
    return Pair(cons1.car, cons2)
  else:
    return Pair(cons1.car, concat_two_list(cons1.cdr, cons2))

scheme_builtins = {
  "+": sum,
  "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
  '*': lambda args: args[0] if len(args) == 1 else (args[0] * scheme_builtins['*'](args[1:])),
  '/': lambda args: args[0] if len(args) == 1 else (args[0] / scheme_builtins['*'](args[1:])),
  'equal?': lambda args: '#t' if False not in [args[i] == args[i + 1] for i in range(len(args) - 1)] else '#f',
  '>': lambda args: '#t' if False not in [args[i] > args[i + 1] for i in range(len(args) - 1)] else '#f',
  '>=': lambda args: '#t' if False not in [args[i] >= args[i + 1] for i in range(len(args) - 1)] else '#f',
  '<': lambda args: '#t' if False not in [args[i] < args[i + 1] for i in range(len(args) - 1)] else '#f',
  '<=': lambda args: '#t' if False not in [args[i] <= args[i + 1] for i in range(len(args) - 1)] else '#f',
  'not': lambda args: '#t' if (args == '#f') else '#f',
  'car': lambda arg: arg.car,
  'cdr': lambda arg: arg.cdr,
  'list?': islist,
  'length': list_length,
  'list-ref': list_ref,
  'append': list_concat,
}

################################
# Classes and Helper Functions #
################################

class Frame():
  def __init__(self, parent=None):

    self.variables = {}
    self.parent = parent
  
  def look_up(self, variable):
    try:
      return self.variables[variable]
    except:
      if self.parent is not None:
        return self.parent.look_up(variable)
      else:
        return None
  
  def frame_look_up(self, variable):
    try:
      self.variables[variable]
      return self
    except:
      if self.parent is not None:
        return self.parent.frame_look_up(variable)
      else:
        return None

builtins = Frame()
builtins.variables = scheme_builtins

class Functions():
  def __init__(self, variables, expression, enc_frame):
    self.variables = variables
    self.expression = expression
    self.enc_frame = enc_frame

def function_evaluator(func, variable_assignment):
  # given a function frame and respective variable assignment, return an expression parsable by evaluate
  if isinstance(func.variables, str):
    func.variables = [func.variables]
  if len(func.variables) != len(variable_assignment):
    raise SchemeEvaluationError
  variable_dict = {}
  for i in range(len(variable_assignment)):
    variable_dict[func.variables[i]] = variable_assignment[i]
  try:
    result = func.expression[:]
  except:
    result = func.expression
  return change_variable_to_assignment(result, variable_dict)

def change_variable_to_assignment(expression1, variable_dict):
  # recurse through an expression list to change all variables to their given assignment
  if not isinstance(expression1, list):
    try:
      return number_or_symbol(expression1)
    except:
      return expression1
  expression = expression1.copy()
  for i, variable in enumerate(expression):
    if not isinstance(variable, list):
      if variable in variable_dict and expression[0] != 'begin':
        expression[i] = variable_dict[variable]
    else:
      try:
        if variable[0] == "del" and variable[1] not in expression[i-1]:
          pass
        elif variable[0] == 'set!' and variable[1] in variable_dict:
          break
        else:
          expression[i] = change_variable_to_assignment(expression[i], variable_dict)
      except:
        expression[i] = change_variable_to_assignment(expression[i], variable_dict)
        
  if len(expression) == 1:
    return expression[0]
  return expression

def translate_user_defined_funcs(input):
  # translate shorter syntax into lambda syntax
  if not isinstance(input[1], list):
    return input
  return ['define', input[1][0], ['lambda', input[1][1:], input[2]]]

class Pair:
  def __init__(self, car, cdr):
    self.car = car
    self.cdr = cdr

def translate_list_to_cons(list_exp):
  # change (list) expression to (cons car cdr) expression
  if not list_exp:
    return 'nil'
  else:
    return ['cons', list_exp[0], translate_list_to_cons(list_exp[1:])]

##############
# Evaluation #
##############

def evaluate(tree, frame=None):
  """
  Evaluate the given syntax tree according to the rules of the Scheme
  language. 

  Arguments:
      tree (type varies): a fully parsed expression, as the output from the
                          parse function
  """
  if frame is None:
    frame = Frame(builtins)

  # if tree is a number or variable
  if not isinstance(tree, list):
    term_val = frame.look_up(tree)
    if term_val is not None:
      return term_val
    else:
      if isinstance(tree, str):
        
        if tree in {'#t', '#f', 'nil'}:
          return tree
        else:
          raise SchemeNameError
    return tree

  # if tree represents a special form or function
  else:
    if tree == [] or (len(tree) == 2 and tree[0] == tree[1]):
      raise SchemeEvaluationError
    if tree[0] == 'define':
      tree = translate_user_defined_funcs(tree)
      frame.variables[tree[1]] = evaluate(tree[2], frame)
      if isinstance(frame.variables[tree[1]], Functions):
        return 'SOMETHING'
      else:
        return frame.variables[tree[1]]
    
    elif tree[0] == 'begin':
      if 'args' in frame.variables or 'args' in frame.parent.variables:
        nframe = Frame(frame)
      else:
        nframe = frame
      for i in range(1, len(tree)):
        if i == len(tree) - 1:
          return evaluate(tree[i], nframe)
        else:
          evaluate(tree[i], nframe)

    # variable-binding manipulation
    elif tree[0] == 'del' or tree[0] == 'let' or tree[0] == 'set!':

      if tree[0] == 'del':
        
        if len(tree) != 2:
          raise SchemeEvaluationError
        
        if isinstance(tree[1], int) or isinstance(tree[1], float):
            return tree[1]
        elif tree[1] not in frame.variables:
          if 'args' in frame.variables:
            if tree[1] not in frame.variables['args']:
              raise SchemeNameError
          elif 'args' in frame.parent.variables:
            if tree[1] in frame.parent.variables['args']:
              return tree[1]
          raise SchemeNameError
        else:
          return frame.variables.pop(tree[1])
      
      if tree[0] == 'let':
        if len(tree) != 3:
          raise SchemeEvaluationError
        new_frame = Frame(frame)
        for lvd in tree[1]:
          new_frame.variables[lvd[0]] = evaluate(lvd[1], frame) 
        return evaluate(tree[2], new_frame)

      if tree[0] == 'set!':
        if len(tree) != 3:
          raise SchemeEvaluationError
        if frame.frame_look_up(tree[1]) is None:
          raise SchemeNameError
        try:
          var_frame = frame.frame_look_up(tree[1])
          value = evaluate(tree[2], frame)
          frame.variables[tree[1]] = value
          frame.parent.variables[tree[1]] = value
          return value
        except:
          return evaluate(Functions(tree[1], tree[2], frame), frame)
        #var_frame = frame.frame_look_up(tree[1])
        #var_frame.variables[tree[1]] = evaluate(tree[2], frame)

    # conditional
    elif tree[0] == 'if':
      if evaluate(tree[1], frame) == '#t':
        return evaluate(tree[2], frame)
      else:
        return evaluate(tree[3], frame)
    
    # linked lists
    elif tree[0] == 'cons' or tree[0] == 'list':
      if tree[0] == 'cons' and len(tree) != 3:
        raise SchemeEvaluationError
      if tree[0] == 'list':
        if len(tree) == 1:
          return 'nil'
        tree1 = translate_list_to_cons(tree[1:])
      else:
        tree1 = tree
      
      return Pair(evaluate(tree1[1], frame), evaluate(tree1[2], frame))

    # and & or
    elif tree[0] == 'and' or tree[0] == 'or':
      if tree[0] == 'and':
        for exp in tree[1:]:
          if evaluate(exp, frame) == '#f':
            return '#f'
        return '#t'
      if tree[0] == 'or':
        for exp in tree[1:]:
          if evaluate(exp, frame) == '#t':
            return '#t'
        return '#f'

    # implicit function calling
    elif isinstance(tree[0], list):
      func = evaluate(tree[0], frame)
      try: 
        if isinstance(func.expression, list) and func.expression[0] == 'set!':
          updated_ex = function_evaluator(func, tree[1:])
          evaluate(updated_ex, func.enc_frame)
          return func.enc_frame.look_up(updated_ex[1])
      except:
        pass
      try:
        if "<lambda>" in func.__code__.co_name:
          return func(tree[1:])       
      except:
        pass
      variable_assignment = [evaluate(tree[i], frame) for i in range(1, len(tree))]
      
      return evaluate(function_evaluator(func, variable_assignment), func.enc_frame)

    elif tree[0] == 'lambda':
      newframe = Frame(frame)
      try:
        newframe.variables['args'] = tree[1]
      except:
        pass
      return Functions(tree[1], tree[2], newframe)

    # built-in functions (arithmetic and comparisons)
    elif frame.look_up(tree[0]) in scheme_builtins.values():
      op = frame.look_up(tree[0])

      if op != scheme_builtins['not']: 
        if tree[0] == 'list-ref':
          if len(tree) != 3:
            raise SchemeEvaluationError
          return op(evaluate(tree[1], frame), evaluate(tree[2], frame))

        elif tree[0] not in {'car', 'cdr', 'length', 'list?'}:
          return op([evaluate(tree[i], frame) for i in range(1, len(tree))])
        else:
          if len(tree) == 2:
            try:
              return op(evaluate(tree[1],frame))
            except:
              raise SchemeEvaluationError
          raise SchemeEvaluationError

      else:
        if len(tree[1:]) > 1:
          raise SchemeEvaluationError
        else:
          try:
            return op(evaluate(tree[1], frame))
          except:
            raise SchemeEvaluationError

    # explicit function call
    elif isinstance(frame.look_up(tree[0]), Functions):
      func_frame = Frame(frame)
      re = evaluate(function_evaluator(frame.look_up(tree[0]), [evaluate(tree[i], frame) for i in range(1, len(tree))]), func_frame)
      if isinstance(re, Functions):
        if len(re.variables) == 0:
          re = evaluate(function_evaluator(re, []),func_frame)
      return re

    # calling something that is not a function or not define in the frame
    elif isinstance(tree[0], str) and frame.look_up(tree[0]) is None:
      raise SchemeNameError
    else:
      raise SchemeEvaluationError

def result_and_frame(tree, frame=None):
  if frame is None:
    frame = Frame(builtins)
  return evaluate(tree, frame), frame

def evaluate_file(file_name, frame=None):
  if frame is None:
    frame = Frame(builtins)
  exp = open(file_name)
  exp_str = exp.read()
  expression = parse(tokenize(exp_str))

  return evaluate(expression, frame)

def repl(raise_all=False):
  global_frame = Frame(builtins)
  for file in sys.argv[1:]:
    evaluate_file(file, global_frame)
  while True:
    # read the input.  pressing ctrl+d exits, as does typing "EXIT" at the
    # prompt.  pressing ctrl+c moves on to the next prompt, ignoring
    # current input
    try:
      inp = input("in> ")
      if inp.strip().lower() == "exit":
        print("  bye bye!")
        return
    except EOFError:
      print()
      print("  bye bye!")
      return
    except KeyboardInterrupt:
      print()
      continue

    try:
      # tokenize and parse the input
      tokens = tokenize(inp)
      ast = parse(tokens)
      # if global_frame has not been set, we want to call
      # result_and_frame without it (which will give us our new frame).
      # if it has been set, though, we want to provide that value
      # explicitly.
      args = [ast]
      if global_frame is not None:
        args.append(global_frame)
      result, global_frame = result_and_frame(*args)
      # finally, print the result
      print("  out> ", result)
    except SchemeError as e:
      # if raise_all was given as True, then we want to raise the
      # exception so we see a full traceback.  if not, just print some
      # information about it and move on to the next step.
      #
      # regardless, all Python exceptions will be raised.
      if raise_all:
        raise
      print(f"{e.__class__.__name__}:", *e.args)
    print()


if __name__ == "__main__":
  # code in this block will only be executed if lab.py is the main file being
  # run (not when this module is imported)

  # uncommenting the following line will run doctests from above
  # doctest.testmod()

  repl()
