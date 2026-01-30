import pickle
from datetime import datetime, timedelta
from collections import UserDict

# --- КЛАСИ ПОЛІВ ---
class Field:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not (len(value) == 10 and value.isdigit()):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

# --- КЛАС ЗАПИСУ ТА КНИГИ ---
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone).value
                return True
        return False

    def add_birthday(self, birthday_string):
        self.birthday = Birthday(birthday_string)

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        bday_str = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{bday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        upcoming = []
        today = datetime.today().date()
        for user in self.data.values():
            if not user.birthday: continue
            bday = user.birthday.value.replace(year=today.year)
            if bday < today: bday = bday.replace(year=today.year + 1)
            if 0 <= (bday - today).days <= 7:
                congrats_date = bday
                if congrats_date.weekday() == 5: congrats_date += timedelta(days=2)
                elif congrats_date.weekday() == 6: congrats_date += timedelta(days=1)
                upcoming.append({"name": user.name.value, "birthday": congrats_date.strftime("%d.%m.%Y")})
        return upcoming

# --- ФУНКЦІЇ ОБРОБНИКИ ---
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError) as e:
            return str(e) if str(e) else "Give me name and data please."
        except KeyError:
            return "Contact not found."
    return inner

@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
        return "Phone added to existing contact."
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return "Contact added."

@input_error
def change_phone(args, book):
    name, old_p, new_p = args
    record = book.find(name)
    if record and record.edit_phone(old_p, new_p):
        return "Phone updated."
    return "Contact or old phone not found."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    return "; ".join(p.value for p in record.phones) if record else "Not found."

@input_error
def add_birthday(args, book):
    name, bday = args
    record = book.find(name)
    if record:
        record.add_birthday(bday)
        return "Birthday added."
    return "Contact not found."

@input_error
def show_birthday(args, book):
    record = book.find(args[0])
    return record.birthday.value.strftime("%d.%m.%Y") if record and record.birthday else "No birthday set."

def get_birthdays(book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming: return "No upcoming birthdays."
    return "\n".join([f"{u['name']}: {u['birthday']}" for u in upcoming])

# --- ПЕРСИСТЕНТНІСТЬ ---
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

# --- ГОЛОВНИЙ ЦИКЛ ---
def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input: continue
        
        parts = user_input.split()
        cmd, args = parts[0].lower(), parts[1:]

        if cmd in ["close", "exit"]:
            save_data(book)
            print("Good bye!"); break
        elif cmd == "hello": print("How can I help you?")
        elif cmd == "add": print(add_contact(args, book))
        elif cmd == "change": print(change_phone(args, book))
        elif cmd == "phone": print(show_phone(args, book))
        elif cmd == "all":
            for r in book.values(): print(r)
        elif cmd == "add-birthday": print(add_birthday(args, book))
        elif cmd == "show-birthday": print(show_birthday(args, book))
        elif cmd == "birthdays": print(get_birthdays(book))
        else: print("Invalid command.")

if __name__ == "__main__":
    main()