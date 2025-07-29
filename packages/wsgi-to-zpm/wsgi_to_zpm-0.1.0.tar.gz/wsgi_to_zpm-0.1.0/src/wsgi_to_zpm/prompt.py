# stdlib imports
from pathlib import Path
import readline

PROMPT_WIDTH = 50

def fmt_prompt(prompt1, prompt2=None, end=' : ', width=PROMPT_WIDTH):
  prompt2 = prompt2 or ''

  total_len = len(prompt1) + len(prompt2)

  spaces = width - total_len
  if spaces <= 0:
    spaces = 1

  return prompt1 + (' '*spaces) + prompt2 + end

def pause(prompt = 'Hit <Enter> to continue...'):
  input(prompt)

def ask_yes_no(prompt="Please type 'y' or 'n'" , prompt2='[Yn]'):
  prompt = fmt_prompt(prompt, prompt2)

  while True:
    resp = (input(prompt).strip().lower() + ' ')[0]

    if resp == 'y':
      return True
    
    if resp == 'n':
      return False

    # Else, ask again
    print("Invalid response. Please type 'y' or 'n'")

def update_field(name, current_value=None, suggestion=None, validation_re=None, allow_blank_response=False):
  if current_value or suggestion:
    cv = f'[{current_value or suggestion}]'
  else:
    cv = ''

  prompt = fmt_prompt(name, cv)

  valid = False
  while not valid:
    value = input(prompt).strip()
    value = value or suggestion or current_value

    if value == None:
      valid = False

    elif not allow_blank_response and value == '':
      valid = False
    
    elif validation_re and not validation_re.match(value):
      valid = False

    else:
      valid = True

    if not valid:
      print("Invalid response.  Try again.")

  return value, value != current_value

def choose(*args, **kargs):
  return list(_choose(*args, **kargs))

def _choose(prompt, choices, multichoice=False, only_once=True, display_choices=True, blank_to_finish=False, allow_freetext=False, exit_on_interupt=False):
  num_choices = len(choices)

  if num_choices == 0:
    return

  if prompt:
    print(prompt)

  if display_choices:
    print("")
    for (idx, choice) in enumerate(choices):
      print(f'  {idx + 1:3d}. {choice}')

  print("")
  if blank_to_finish:
    choose_prompt = fmt_prompt('Enter a choice (blank to finish)')
  else:
    choose_prompt = fmt_prompt('Enter a choice')

  chosen = set()

  while len(chosen) < num_choices:
    try:
      resp = input(choose_prompt).strip()

      if resp == '' and blank_to_finish:
        return

      idx = int(resp)

    except KeyboardInterrupt as e:
      # Ctrl-C => Return
      if exit_on_interupt:
        print("")
        return
      
      raise e

    except:
      if not allow_freetext:
        print("Invalid input. Try again.")
        continue

      if len(resp) == 0:
        print("Invalid input. Try again.")
        continue

      yield (resp, None)

      if not multichoice:
        return
      else:
        continue

    if idx < 1 or idx > num_choices:
      print(f"Please choose between 1 and {num_choices}.")
      continue

    if only_once and idx in chosen:
      print(f"You've already chosen #{idx}. Try again.")
      continue
    
    chosen.add(idx)
    yield (choices[idx-1], idx-1)

    if not multichoice:
      return

def prompt_list(prompt, unique_values=False, validation_re=None):
  print("")
  choose_prompt = fmt_prompt(f'{prompt}', '(blank to finish)')

  responses = []

  while True:
    try:
      resp = input(choose_prompt).strip()

      if resp == '':
        break

    except KeyboardInterrupt:
      # Ctrl-C => Return
      print("")
      break

    except:
      print("Invalid input. Try again.")
      continue
    
    if validation_re and not validation_re.match(resp):
      print("Invalid input. Try again.")
      continue

    responses.append(resp)

  if unique_values:
    return set(responses)

  return responses

def mkdir(d, prompt='Make directory? '):
  p = Path(d)

  if p.exists():
    return

  if ask_yes_no(prompt):
    p.mkdir(parents=True)
