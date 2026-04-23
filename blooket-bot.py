from seleniumbase import SB
gamepin = input("Enter the game pin: ")

with SB(headless=True) as sb:
    while True:
       sb.open("https://www.blooketflooder.com")
       sb.type("[name='gamePin']", gamepin)
       sb.click('[type="submit"]')
