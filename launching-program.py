# This program launches the other main programs for easier use.
import os

print('''
==============================
Welcome to the Bot-programs.py
==============================

''')


while true:
  cmd = input('Enter the name of the program you want to do, dont forget the .py! ')

# Make it failsafe
  try:
    # Run fil3 in terminal
    os.system(f"python3 {cmd}")
  except Exception as e:
    print("Error: " + e)
    continue
