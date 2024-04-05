import psycopg2
from psycopg2 import Error
from psycopg2 import IntegrityError
import re


class BaseClient:
    def __init__(self, user, password, database):
         self.user = user
         self.password = password
         self.database = database

    def is_valid_email(self, email):
        pattern = re.compile(r'^[\w.\-]+@[\w.\-]+\.\w+$')
        return bool(pattern.match(email))

    def create_table_client(self):
        try:
            with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
                with conn.cursor() as cur:
                    sql = """CREATE TABLE IF NOT EXISTS client(
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        surname VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL
                    )"""
                    cur.execute(sql)
                    print("Таблица client успешно создана")
        except Error as e:
            print("ОШИБКА" %e)

    def create_table_phones(self):
        try:
            with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
                with conn.cursor() as cur:
                    sql = """CREATE TABLE IF NOT EXISTS phones(
                            id SERIAL PRIMARY KEY,
                            client_id INTEGER REFERENCES client(id),
                            number VARCHAR(20) NOT NULL
                        )"""
                    cur.execute(sql)
                    print("Таблица phones успешно создана")
        except Error as e:
            print("ОШИБКА" %e)
    
    def email_count(self):
        email = input(f"Введите ваш email осталось попыток {count_email}: ")
        return email

    def create_client(self, name, surname, email):
        global count_email
        count_email = 3
        if self.is_valid_email(email):
            print('Верный email')
            try:
                with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
                    with conn.cursor() as cur:
                        cur.execute ("""INSERT INTO client (name, surname, email)
                                VALUES (%s, %s, %s);
                            """, (name.title(), surname.title(), email))
                        conn.commit()
                        print("Данные сохранены")
            except Error as e:
                print("ОШИБКА" %e)

        else:
            print(f'К сожалению, введенный вами email некорректен. Пожалуйста, попробуйте еще раз')
            while count_email > 0:
                count_email -= 1
                self.email_count()

    def create_phones(self, client_id, number):
        try:
            with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
                    with conn.cursor() as cur:
                        cur.execute (
                            """INSERT INTO phones (client_id, number)
                               VALUES (%s, %s);
                            """, (client_id, number))
                        conn.commit()
                        print("Данные сохранены")
        except Error as e:
            print("ОШИБКА" %e)

    
    def update_name(self, examination):
        name = input("Введите новое имя: ")
        try:
            with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE client SET name = %s WHERE id = %s", (name.title(), examination))
                    print("Имя изменино")
                    conn.commit()
        except IntegrityError as e:
            print("ОШИБКА: ", e)   
                   
    def update_surname(self, examination):
        surname = input("Введите другую фамилию: ")
        try:
            with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE client SET surname = %s WHERE id = %s", (surname.title(), examination))
                    print("Фамилия изменена")
                    conn.commit()
        except IntegrityError as e:
            print("ОШИБКА: ", e)

    def update_email(self, examination):
        email = input("Введите новый email: ")
        global count_email
        count_email = 3
        if self.is_valid_email(email):
            try:
                with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
                    with conn.cursor() as cur:
                        cur.execute("UPDATE client SET email = %s WHERE id = %s", (email, examination))
                        print("email изменён")
                        conn.commit()
            except IntegrityError as e:
                print("ОШИБКА: ", e)
        else:  
            print(f'К сожалению, введенный вами email некорректен. Пожалуйста, попробуйте еще раз')
            while count_email > 0:
                count_email -= 1
                self.email_count()        

    def examination_id(self, examination):
        try:
            with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                            SELECT EXISTS (SELECT 1 FROM client WHERE id = %s)""", (examination,))
                    result = cur.fetchone()[0]
                    if result:
                        print("Верный id")
                        self.change(examination)
                        return result
                    else:
                        print("Такого Id не существует")
        except IntegrityError as e:
            print("ОШИБКА: ", e)

    def change(self, examination):
        choose = input("Что вы хотите поменять 1- Имя, 2-Фамилию, 3-email, 4-удалить телефон, 5-удалить клиента ")
        if choose == "1":
            self.update_name(examination)
        elif choose =="2":
            self.update_surname(examination)
        elif choose == "3":
            self.update_email(examination)
        elif choose =="4":
            self.delete_phone(examination)
        elif choose == "5":
            self.delete_client(examination)
        else:
            print("Еще нет такой команды")

    def delete_phone(self, examination):
        try:
            with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                            SELECT id, number FROM phones WHERE client_id = %s""",(examination,))
                    phone_numbers = cur.fetchall()
                    print(phone_numbers)
                    delit = input('Какой номер удалить по id?: ')
                    cur.execute(
                        """DELETE FROM phones WHERE id = %s""",(delit))
                    print("Номер успешно удален")
        except IntegrityError as e:
            print("ОШИБКА: ", e)

    def delete_client(self, examination):
        try:
            with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """DELETE FROM client WHERE id = %s """,(examination,))
                    print("Клиент удален")
                conn.commit()
        except IntegrityError as e:
            print("ОШИБКА: ", e)

    def find_client(self):
        data = input("Найти клиента: 0-По id, 1-Имени, 2-Фамилии, 3-email, 4-По номеру телефона: ")
        with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
                with conn.cursor() as cur:
                    if data =="0":
                        id = input("Введите id:")
                        cur.execute("""
                                SELECT * FROM client
                                WHERE id = %s""", (id,))
                        id_info = cur.fetchall()
                        print(id_info)

                    elif data == "1":
                        name = input("Введите имя: ").title()
                        cur.execute("""
                                SELECT * FROM client
                                WHERE name = %s""", (name,))
                        name_info = cur.fetchall()
                        print(name_info)

                    elif data == "2":
                        surname = input("Введите фамилию: ").title()
                        cur.execute("""
                                SELECT * FROM client
                                WHERE surname = %s""", (surname,))
                        surname_info = cur.fetchall()
                        print(surname_info)
                    
                    elif data == "3":
                        email = input("Введите email: ")
                        cur.execute("""
                                SELECT * FROM client
                                WHERE email = %s""", (email,))
                        email_info = cur.fetchall()
                        print(email_info)

                    elif data == "4":
                        number = input("Введите номер телефона: ")
                        cur.execute("""
                                SELECT * FROM client
                                WHERE id IN (SELECT client_id FROM phones WHERE number = %s)""", (number,))
                        number_info = cur.fetchall()
                        print(number_info)
                    else:
                        print("Пока нет такой функции")


        
if __name__ == '__main__':
    users = ' '
    passwords = ' '
    databases = ' '
    base_client = BaseClient(users, passwords, databases)
    base_client.create_table_client()
    base_client.create_table_phones()
    base_client.create_client(name = input("Введите имя: "), surname = input("Введите фамилию: "), email = input("Введите email : "))
    base_client.create_phones(client_id=int(input('Введите id клиента: ')), number=input("Введите номер телефона: "))
    base_client.examination_id(examination = str(input("Введите id в котором хотите сделать изменения: ")))
    base_client.find_client()
