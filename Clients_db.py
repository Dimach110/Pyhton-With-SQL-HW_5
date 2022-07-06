# Программа для создания и работы с базой данных клиентов

import psycopg2

def create_db():
    with psycopg2.connect(database='client_db_hw', user='user1', password='psqluser1') as conn:
        with conn.cursor() as cur:

            cur.execute("""
            CREATE TABLE IF NOT EXISTS profile_client ( 
            id SERIAL PRIMARY KEY, 
            first_name VARCHAR(20) NOT NULL,
            second_name VARCHAR(30) NOT NULL,
            email VARCHAR(60) UNIQUE NOT NULL,
            CONSTRAINT pk UNIQUE (first_name, second_name));
            
            CREATE TABLE IF NOT EXISTS phone_numbers (
            id SERIAL PRIMARY KEY, 
            number_ph VARCHAR(11),
            id_profile INTEGER NOT NULL REFERENCES profile_client(id) ON DELETE CASCADE
            ); """)
            conn.commit()
            print("Базы данных созданы")


def drop_db():
    question = input("Вы уверены что хотите удалить базы данных, их восстановление не возможно: ")
    if question.lower() == 'да' or 'yes':
        with psycopg2.connect(database='client_db_hw', user='user1', password='psqluser1') as conn:
            with conn.cursor() as cur:
                cur.execute("""
                DROP TABLE phone_numbers;
                DROP TABLE profile_client;                  
                """)
                conn.commit()
                print("Базы данных удалены")

def conn_db (value, fetch=' '):
    '''
    :param value: Указать значение передаваемое в базу данных.
    :param fetch: Если возврат не требуется, то не указывать.
                  Если необходимо вернуть параметр, то указать 'one' или 'all'.
                  Если требуется вернуть n строк, то просто указать количество строк в формате 'n'.
    :return: Возвращает полученное значение в виде кортежа
    '''
    with psycopg2.connect(database='client_db_hw', user='user1', password='psqluser1') as conn:
        with conn.cursor() as cur:
            cur.execute(value)
            if fetch == 'one':
                result = cur.fetchone()
            elif fetch == 'all':
                result = cur.fetchall()
            elif fetch.isdigit():
                result = cur.fetchmany(int(fetch))
            else:
                result = "NONE"
    return result

# функция создания нового клиента
def new_client( first_name, second_name, email, tel=None):
    result = conn_db(f"""INSERT INTO profile_client (first_name, second_name, email)  
            VALUES ('{first_name}','{second_name}','{email}') RETURNING id;""", 'one')
    print(result[0])
    if tel == None:
        conn_db(f"INSERT INTO phone_numbers (id_profile) VALUES ('{result[0]}');")
    else:
        conn_db(f"INSERT INTO phone_numbers (number_ph, id_profile) VALUES ('{tel}', '{result[0]}');")

def add_phone_number( first_name, second_name, number):
    try:
        id = conn_db((f"""SELECT id FROM profile_client 
        WHERE first_name = '{first_name}' and second_name = '{second_name}'"""), 'one')
        result = conn_db(f"""INSERT INTO phone_numbers (number_ph, id_profile)
                          VALUES ({number}, {id[0]}) RETURNING * """, 'all')
        return result
    except TypeError:
        print("Такой учётной записи не найдено")
    # except psycopg2.errors.UniqueViolation:
    #     prof = conn_db(f"""SELECT first_name, second_name FROM profile_client pc
    #     JOIN phone_numbers pn ON pc.id = id_profile WHERE pn.number_ph = {number};""", 'one')
    #     print(f"Номер телефона уже зарегистрирован за {prof[0]} {prof[1]}")

def search_phone_number(first_name, second_name):
    result = conn_db(f"""SELECT pn.id, pn.number_ph FROM phone_numbers pn
    JOIN profile_client pc ON id_profile = pc.id 
    WHERE pc.first_name = '{first_name}' AND pc.second_name = '{second_name}';""", 'all')
    for res in result:
        print(f'ID:{res[0]} - номер телефона {res[1]}')

def del_number_phone(id):
    conn_db(f"DELETE FROM phone_numbers WHERE id = {id} ")

def update_profile(id, first_name, second_name, email):
    conn_db(f"""UPDATE profile_client SET first_name = '{first_name}', 
    second_name = '{second_name}', email = '{email}' WHERE id = '{id}';""")

def del_profile(id):
    try:    #на тот случай если у абонента не было номера телефона
        conn_db(f"DELETE FROM phone_numbers WHERE id_profile = {id};")
    except:
        print()
    conn_db(f"DELETE FROM profile_client WHERE id = {id};")

def print_res(result):
    for res in result:
            print(f'Имя: {res[0]} Фамилия: {res[1]} Email: {res[2]} Номер телефона: {res[3]}')

def search_profile(first_name, second_name, email, phone):
    if first_name != None and second_name != None:
        result = conn_db(f"""SELECT pc.first_name, pc.second_name, pc.email, pn.number_ph FROM profile_client pc
                JOIN phone_numbers pn ON pc.id = pn.id_profile
                WHERE pc.first_name = '{first_name}' and pc.second_name = '{second_name}' ;""", 'all')
        print_res(result)
    elif email != None:
        result = conn_db(f"""SELECT pc.first_name, pc.second_name, pc.email, pn.number_ph FROM profile_client pc
                JOIN phone_numbers pn ON pc.id = pn.id_profile WHERE pc.email = '{email}';""", 'all')
        print_res(result)
    elif phone != None:
        result = conn_db(f"""SELECT pc.first_name, pc.second_name, pc.email, pn.number_ph FROM profile_client pc
                JOIN phone_numbers pn ON pc.id = pn.id_profile WHERE pn.number_ph = '{phone}';""", 'all')
        print_res(result)
    elif second_name != None:
        result = conn_db(f"""SELECT pc.first_name, pc.second_name, pc.email, pn.number_ph FROM profile_client pc
                        JOIN phone_numbers pn ON pc.id = pn.id_profile
                        WHERE pc.second_name = '{second_name}';""", 'all')
        print_res(result)
    elif first_name != None:
        result = conn_db(f"""SELECT pc.first_name, pc.second_name, pc.email, pn.number_ph FROM profile_client pc
                        JOIN phone_numbers pn ON pc.id = pn.id_profile
                        WHERE pc.first_name = '{first_name}';""", 'all')
        print_res(result)
    else:
        print('Вы ввели не корректные данные, повторите ввод.')

def input_val():
    f_name = input('Введите имя: ') or None
    s_name = input('Введите фамилию: ') or None
    email = input('Введите email: ') or None
    phone = input('Введите номер телефона: ') or None
    return f_name, s_name, email, phone

if __name__ == '__main__':

    while True:
        enter = input('''Выберите действие, которое вы хотите осуществить:
        1 - Создать базу данных
        2 - Добавить в БД нового клиента
        3 - Добавить телефон для существующего клиента
        4 - Изменить данные о клиенте
        5 - Удалить телефон для существующего клиента
        6 - Удалить УЗ существующего клиента
        7 - Найти клиента по его данным (имени, фамилии, email-у или телефону)
        8 - Удалить Базу Данных
        Ввод: ''')
        if enter == '1':
            create_db()
        elif enter == '2':
            print('Введите Имя, Фамилию, Email и Телефон, если телефона нет, нажмите Enter и пропустите параметр.')
            result = input_val()
            new_client(result[0], result[1], result[2], result[3])
        elif enter == '3':
            print('Введите Имя, Фамилию и Телефон который вы хотите добавить. Email можно пропустить, нажав Enter.')
            result = input_val()
            add_phone_number(result[0], result[1], result[3])
        elif enter == '4':
            print('Введите ID клиента, и новые данные для этой УЗ (Имя, Фамилию и Email).'
                  'Ввод номера телефона можно пропустить, нажав Enter.')
            id_profile = input("ВВедите ID клиента: ")
            result = input_val()
            update_profile(id_profile, result[0], result[1], result[2])
        elif enter == '5':
            print('Введите Имя, Фамилию абонента, чей телефон вы хотите удалить')
            result = input_val()
            search_phone_number(result[0], result[1])
            id_phone = input('Введите ID телефонной записи, которую вы хотите удалить: ')
            del_number_phone(id_phone)
        elif enter == '6':
            id = input('Введите ID учётной записи клиента, которого вы хотите удалить из базы: ')
            del_profile(id)
        elif enter == '7':
            print('Введите Имя и Фамилию, Email или телефон для поиска УЗ клиента. '
                  'При нажатии Enter в пустое поле ввода вы пропускаете параметр.')
            result = input_val()
            search_profile(result[0], result[1], result[2], result[3])
        elif enter == '8':
            drop_db()
        else:
            print()
        q = input("Хотите выйти из меню?: ")
        if q.lower() == 'да' or q.lower() == 'yes':
            break

    # new_client('Д', 'Ч', 'd@m.ru')
    # new_client('d', 'c', 'd@c')
    # new_client('Д1', 'Ч1', 'd1@mail.ru', '79161111111')
    # new_client('Д2', 'Ч', 'd2@mail.ru', '79161111112')
    # new_client('Д3', 'Ч', 'd3@mail.ru', '79161111113')
    # new_client('Д4', 'Ч', 'd4@mail.ru', '79161111114')
    # add_phone_number('Д3', 'Ч', '11245')
    # add_phone_number('Д3', 'Ч', '1234567890')
    #
    # new_client('Дмитрий', 'Чугунов', 'd5@mail.ru', '79161111115' )
    # update_profile('5','Дмитрий5', 'Чугунов', 'd5@mail.ru')
    # search_phone_number('Дмитрий3', 'Чугунов')
    # del_number_phone(6)
    # del_profile(3)
    #
    # create_db()
    #
    # iv = input_val()
    # search_profile(iv[0], iv[1], iv[2], iv[3])
    #
    # with psycopg2.connect(database='client_db_hw', user='user1', password='psqluser1') as conn:
    #     with conn.cursor() as cur:
    #         cur.execute(f"INSERT INTO phone_numbers (id_profile) VALUES ('1');")
    #         conn.commit()
    #
