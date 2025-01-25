from abc import ABC, abstractmethod
from collections import UserDict
from datetime import datetime, timedelta
import pickle
class Field:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)
class Name(Field):
    pass
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)
class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            self.value = value
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    def add_phone(self, phone):
        self.phones.append(Phone(phone))
    def remove_phone(self, phone):
        phone_to_remove = self.find_phone(phone)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
        else:
            raise ValueError("Phone not found.")
    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit:
            self.add_phone(new_phone)
            self.remove_phone(old_phone)
        else:
            raise ValueError("Phone not found.")
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = self.birthday.value if self.birthday else "N/A"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    def find(self, name):
        return self.data.get(name, None)
    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError("Contact not found.")
    def get_upcoming_birthdays(self):
        today = datetime.today()
        next_week = today + timedelta(days=7)
        birthdays = []
        for record in self.data.values():
            if record.birthday:
                bday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y")
                bday_this_year = bday_date.replace(year=today.year)
                if today <= bday_this_year <= next_week:
                    birthdays.append({"name": record.name.value, "birthday": bday_this_year.strftime("%d.%m.%Y")})
        return birthdays
    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())
class View(ABC):
    @abstractmethod
    def display(self, message):
        pass
    @abstractmethod
    def get_input(self, prompt):
        pass
class ConsoleView(View):
    def display(self, message):
        print(message)
    def get_input(self, prompt):
        return input(prompt)
class Assistant:
    def __init__(self, view: View):
        self.book = self.load_data()
        self.view = view
        self.commands = {
            "add": self.add_contact,
            "change": self.change_contact,
            "phone": self.show_phone,
            "add-birthday": self.add_birthday,
            "show-birthday": self.show_birthday,
            "birthdays": self.upcoming_birthdays,
            "all": self.list_all
        }
    def save_data(self, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.book, f)
    def load_data(self, filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook()
    def add_contact(self, args):
        name, phone, *_ = args.split()
        record = self.book.find(name)
        message = "Contact updated."
        if record is None:
            record = Record(name)
            self.book.add_record(record)
            message = "Contact added."
        if phone:
            record.add_phone(phone)
        self.view.display(message)
    def change_contact(self, args):
        name, old_phone, new_phone = args.split()
        record = self.book.find(name)
        if record:
            record.edit_phone(old_phone, new_phone)
            self.view.display("Contact updated.")
        else:
            self.view.display("Contact not found.")
    def show_phone(self, args):
        name, *_ = args.split()
        record = self.book.find(name)
        if record:
            self.view.display(str(record))
        else:
            self.view.display("Contact not found.")
    def add_birthday(self, args):
        name, birthday = args.split()
        record = self.book.find(name)
        if record:
            record.add_birthday(birthday)
            self.view.display("Birthday added.")
        else:
            self.view.display("Contact not found.")
    def show_birthday(self, args):
        name, *_ = args.split()
        record = self.book.find(name)
        if record and record.birthday:
            self.view.display(f"Birthday: {record.birthday.value}")
        else:
            self.view.display("Birthday not found.")
    def upcoming_birthdays(self, _):
        birthdays = self.book.get_upcoming_birthdays()
        if birthdays:
            self.view.display("\n".join(f"{b['name']}: {b['birthday']}" for b in birthdays))
        else:
            self.view.display("No upcoming birthdays.")
    def list_all(self, _):
        self.view.display(str(self.book) if self.book.data else "No contacts found.")
    def run(self):
        self.view.display("Welcome to the assistant bot!")
        while True:
            user_input = self.view.get_input("Enter a command: ")
            parts = user_input.split(maxsplit=1)
            command = parts[0]
            args = parts[1] if len(parts) > 1 else ""

            if command in ["close", "exit"]:
                self.save_data()
                self.view.display("Good bye!")
                break

            handler = self.commands.get(command)
            if handler:
                handler(args)
            else:
                self.view.display("Invalid command.")
if __name__ == "__main__":
    console_view = ConsoleView()
    assistant = Assistant(console_view)
    assistant.run()
