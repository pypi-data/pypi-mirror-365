import random
import string
import colorama
import pyperclip as py
colorama.init()

def password_new(n=12, typepass="all"):
    a = list(string.printable)
    b = list(string.digits)
    if typepass == "all":
        p = "".join(random.choice(a) for _ in range(n))
        print(colorama.Fore.GREEN, p)
        py.copy(p)
        print("copied")
    elif typepass == "number":
        p = "".join(random.choice(b) for _ in range(n))
        print(colorama.Fore.GREEN, p)
        py.copy(p)
        print("copied")

if __name__ == "__main__":
    password_new()