# Завдання
# У цьому домашньому завданні вам треба:
#
# Додати функціонал збереження адресної книги на диск та відновлення з диска. Для цього ви можете вибрати будь-який
# зручний для вас протокол серіалізації/десеріалізації даних та реалізувати методи, які дозволять зберегти всі дані у
# файл і завантажити їх із файлу.
#
# Додати користувачеві можливість пошуку вмісту книги контактів, щоб можна було знайти всю інформацію про одного або
# кількох користувачів за кількома цифрами номера телефону або літерами імені тощо.
#
# Критерії прийому:
# Програма не втрачає дані після виходу з програми та відновлює їх з файлу.
# Програма виводить список користувачів, які мають в імені або номері телефону є збіги із введеним рядком.

from collections import UserDict
import datetime
import re
import pickle
import os


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name] = record

    def iterator(self, count: int):
        for key, value in self:
            i = 1
            temp_dict = {}
            while i <= count:
                temp_dict[key] = value
                i += 1
            yield temp_dict

    def __iter__(self):
        for key, value in self.data.items():
            yield key, value


class Field:
    def __init__(self, value=None):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Birthday(Field):
    def days_to_birthday(self):
        birthday = self._value
        today = datetime.date.today()
        next_birthday = datetime.date(year=today.year, month=birthday.month, day=birthday.day)
        if next_birthday < today:
            next_birthday = datetime.date(year=today.year + 1, month=birthday.month, day=birthday.day)

        delta = next_birthday - today

        if delta.days == 0:
            return "Today birthday"
        else:
            return f"{delta.days} days to next birthday"

    @Field.value.setter
    def value(self, value):
        try:
            super(Birthday, self.__class__).value.fset(self, datetime.datetime.strptime(value, '%d-%m-%Y'))
        except ValueError:
            print("Incorrect data format, should be DD-MM-YYYY")


class Name(Field):
    pass


class PhoneFormatError(Exception):
    pass

class Phone(Field):

    def __init__(self, value):
        self.value = Phone.check_phone(value)

    @classmethod
    def check_phone(cls, value):
        regex = r"\([0-9]{3}\)[0-9]{3}-[0-9]{2}-[0-9]{2}"
        if len(re.findall(regex, value)) == 0:
            raise PhoneFormatError
        return value


    @Field.value.setter
    def value(self, value):
        super(Phone, self.__class__).value.fset(self, Phone.check_phone(value))


class Record:

    def __init__(self, name, phone=None, birthday=None):
        self.name = Name(name)
        self.birthday = Birthday()
        if phone:
            self.phones = [Phone(phone)]
        else:
            self.phones = []

        if birthday:
            self.birthday.value = birthday

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def delete_phone(self, phone):
        for elem in self.phones:
            if elem.value == phone:
                self.phones.remove(elem)

    def delete_phone_index(self, index):
        self.phones.pop(index)

    def edit_phone(self, old_phone, new_phone):
        for elem in self.phones:
            if elem.value == old_phone:
                elem.value = new_phone


if os.path.isfile('dump.pickle'):
    with open('dump.pickle', 'rb') as file:
        RECORDS = pickle.load(file)
else:
    RECORDS = AddressBook()


# Decorators


def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except KeyError:
            print("Wrong command")
        except IndexError:
            print("Wrong command")
        except PhoneFormatError:
            print("Incorrect phone format, (NNN)NNN-NN-NN")
    return wrapper


# Procedures

def hello():
    print("How can I help you?")


@input_error
def add(*args):
    command_list = args[0]
    if len(command_list) < 2:
        print("Give me name and phone please")
        return

    contact_name = command_list[0]
    contact_phone = command_list[1]
    contact_birthday = None
    if len(command_list) > 2:
        contact_birthday = command_list[2]
    if not RECORDS.get(contact_name):
        new_record = Record(contact_name, contact_phone, contact_birthday)
        RECORDS.add_record(new_record)
    else:
        RECORDS[contact_name].add_phone(contact_phone)


@input_error
def change_phone(*args):
    command_list = args[0]
    if not len(command_list) == 3:
        print("Give me name, old and new phone please")
        return

    contact_name = command_list[0]
    contact_old_phone = command_list[1]
    contact_new_phone = command_list[2]
    RECORDS[contact_name].edit_phone(contact_old_phone, contact_new_phone)


@input_error
def delete_phone(*args):
    command_list = args[0]
    if not len(command_list) == 2:
        print("Give me name and phone please")
        return

    contact_name = command_list[0]
    contact_phone = command_list[1]
    RECORDS[contact_name].delete_phone(contact_phone)


@input_error
def phone(*args):
    command_list = args[0]
    if not len(command_list) == 1:
        print("Enter user name")
        return

    contact_name = args[0][0]
    print(RECORDS[contact_name])

@input_error
def search(*args):
    command_list = args[0]
    if len(command_list) == 0:
        print("Give me text for search")
        return

    search_text = command_list[0]

    for elem in RECORDS:
        data = elem[1]
        show_this_elem = data.name.value.lower().find(search_text) >= 0
        for phone in data.phones:
            if ''.join(filter(str.isdigit, phone.value)).find(search_text) >= 0:
                show_this_elem = True

        if show_this_elem:
            print(f"""Name: {data.name.value} {f" - Birthday: {data.birthday.value.strftime('%d-%m-%Y')} ({data.birthday.days_to_birthday()})" if data.birthday.value else ''}\nPhone: {', '.join(phone.value for phone in data.phones)}""")

@input_error
def show():
    for elem in RECORDS.iterator(10):
        for key, data in elem.items():
            print(f"""Name: {key.value} {f" - Birthday: {data.birthday.value.strftime('%d-%m-%Y')} ({data.birthday.days_to_birthday()})" if data.birthday.value else ''}\nPhone: {', '.join(phone.value for phone in data.phones)}""")


def stop():
    with open('dump.pickle', 'wb') as file:
        pickle.dump(RECORDS, file)
    print("Good bye!")
    quit()


@input_error
def get_handler(command_list):
    return read_command_list(command_list)


def read_command_list(command_list: list):
    command = OPERATIONS[command_list.pop(0).lower()]
    command = read_command_list(command_list) if command == read_command_list else command
    return command


OPERATIONS = {
    'hello': hello,
    'add': add,
    'change': change_phone,
    'phone': phone,
    'show': read_command_list,
    'all': show,
    'good': read_command_list,
    'bye': stop,
    'close': stop,
    'exit': stop,
    'delete': delete_phone,
    'search': search
}


def bot():
    while True:
        command = input("Enter command: ")
        command_list = command.split(sep=" ")
        handler = get_handler(command_list)
        if handler is not None:
            if not command_list:
                handler()
            else:
                handler(command_list)


if __name__ == '__main__':
    bot()
