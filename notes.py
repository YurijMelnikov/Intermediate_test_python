import sqlite3
import easygui
import datetime

#Подключаем базу данных, создаём переменную cursor
try:
    connection = sqlite3.connect('notes.db')
    cursor = connection.cursor()
    print("Файл заметок успешно открыт")
except:
    pass

#Создаём таблицу с заметками, с полями - id, имя заметки, тело заметки, дата создания/редактирования если таблица создана, пропускаем исключение
try:
    notes_table = '''CREATE TABLE "notes"(
                            note_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,                        
                            note_name TEXT NOT NULL UNIQUE,
                            note_body TEXT,
                            note_date timestamp NOT NULL);'''

    cursor.execute(notes_table)
except:
    pass


#Стартовый экран в easygui
def start_screen():
    choices = ["Добавить заметку",
               "Редактировать заметку",             
               "Удалить заметки",
               "Вывести все заметки в хронологическом порядке",
               "Вывести определённые заметки",
               "Вывести заметки за определённый период",                              
               "Закрыть и сохранить заметки"]
    msg = ""
    title = "Заметки"
    choice = easygui.choicebox(msg, title, choices)
    if choice == "Добавить заметку":
        return 1
    elif choice == "Редактировать заметку":
        return 2
    elif choice == "Удалить заметки":
        return 3
    elif choice == "Вывести все заметки в хронологическом порядке":
        return 4
    elif choice == "Вывести определённые заметки":
        return 5
    elif choice == "Вывести заметки за определённый период":
        return 6
    elif choice == "Закрыть и сохранить заметки":
        return 0

#Блок с запросами в базу данных

#Добавляем данные в таблицу с заметками, на вход принимает список значений
def inset_note(values: list):
    try:
        note_insert = '''INSERT INTO "notes"
                            (note_name, note_body, note_date)
                            VALUES (?,?,?);'''
        cursor.execute(note_insert, values)
        connection.commit()
    except sqlite3.IntegrityError:
        easygui.msgbox("ОШИБКА, заметка с таким именем уже существует")
        return
    else:
        easygui.msgbox(f"Заметка {values[0]} успешно добавлена в файл")


#Select запрос на все данные из таблицы с заметками
def request_notes():
    request_note_list = '''SELECT note_id,\
                                note_name,\
                                note_body,\
                                note_date\
                                from "notes"'''
    cursor.execute(request_note_list)
    request_notes_list = cursor.fetchall()
    return request_notes_list

#Запрос на выборку заметок с определёнными ID, которые функция принимает в виде списка
def request_selected_notes (note_id_list: list):    
    selected_notes_list = list()
    for i in range (len(note_id_list)):
        request_single_note = f'''SELECT note_id,\
                                    note_name,\
                                    note_body,\
                                    note_date\
                                    from "notes"
                                    WHERE note_id = {note_id_list[i]}'''
        selected_notes_list.extend(cursor.execute(request_single_note))
    return selected_notes_list


#Запрос на удаление выбранных заметок, id заметок в списке, если id заметки одиночный int, в запросе это обрабатывается
def request_delete_note(note_id_list: list):
    if type(note_id_list) == list:
        for i in range(len(note_id_list)):
            delete_request_note = f'''DELETE from "notes"\
                                    WHERE note_id = {note_id_list[i]}'''
            cursor.execute(delete_request_note)
    else:
        delete_request_note = f'''DELETE from "notes"\
                                WHERE note_id = {note_id_list}'''
        cursor.execute(delete_request_note)
    connection.commit()

#Изменение заметки, на вход принимается id заметки и список значений для обновления 

def request_update_note(note_id: int, values: list):
    try:  
        note_update = f'''UPDATE "notes"\
                            SET\
                                note_name = ?,\
                                note_body = ?,\
                                note_date = ?\
                            WHERE note_id = {note_id};'''
        cursor.execute(note_update, values)
        connection.commit()
    except sqlite3.IntegrityError:
        easygui.msgbox("ОШИБКА, заметка с таким именем уже существует")
    else:
        easygui.msgbox(f"Заметка успешно изменена")


#Добавление новой заметки
def add_note():
    while True:
        msg = "Добавление заметки"
        title = "Введите заголовок заметки"
        note_fields = ["Заголовок заметки", "Текст заметки"]
        note = easygui.multenterbox(msg, title, note_fields)
        if note == None:
            return
        elif note[0] == "":
            selection = question_yes_no(
                "Поле заголовок заметки не должно быть пустым, желаете повторить ввод?")
            if not selection:
                return
        elif note[0] != "":
            break
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    note.append(time)    
    for i in range(len(note)):
        if note[i] == "":
            note[i] = None  
    inset_note(note)

    


#Редактирование заметки
def change_note():
    request_note_tuple = request_notes()    
    request_note_list = get_list_of_choice(request_note_tuple)
    choice_list = list()
    for i in range (len(request_note_list)):
        choice_list.append(request_note_list[i][1])    
    if len(choice_list) == 0:
        easygui.msgbox("Нет ни одной заметки в файле")
        return
    elif len(choice_list) == 1:
        choice = choice_list[0]
        check = question_yes_no(f"В файле только одна заметка {choice}\n\
                        Изменить её?")
        if not check:
            return
    else:
        choice = easygui.choicebox(
            "Изменить заметку", "Выберите заметку", choice_list)
        if choice == None:
            return
    note_id = get_id(request_note_tuple, choice)
    while True:
        msg = f"Изменение заметки {choice}"
        title = "Внесите изменения, заголовок заметки не должен быть пустым"
        note_fields = ["Заголовок заметки", "Текст заметки"]
        note_values = easygui.multenterbox(
            msg, title, note_fields)
        if note_values == None:
            return
        elif note_values[0] == "":
            selection = question_yes_no(
                "Поле \"Заголовок заметки не должен быть пустым\", желаете повторить ввод?")
            if not selection:
                return
        elif note_values[0] != "":
            break
    for i in range(len(note_values)):
        if note_values[i] == "":
            note_values[i] = None
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    note_values.append(time)
    request_update_note(note_id, note_values)


#Удаление заметки
def delete_notes():
    request_notes_tuple = request_notes()
    request_note_list = get_list_of_choice(request_notes_tuple)
    choice_list = list()
    for i in range (len(request_note_list)):
        choice_list.append(request_note_list[i][1])      
    if len(choice_list) == 0:
        easygui.msgbox("Нет ни одной заметки в файле")
        return
    elif len(choice_list) == 1:
        choice = choice_list[0]
        check = question_yes_no(f"В файле только одна заметка {choice}\n\
                        Удалить её?")
        if not check:
            return
        note_id = get_id(request_notes_tuple, choice)
        request_delete_note(note_id)
        easygui.msgbox("Заметка успешно удалена")
    else:
        choice = easygui.multchoicebox(
            "Выберите заметки для удаления", "Удаление заметок", choice_list)
        if choice == None:
            return
        check = question_yes_no(
            "Вы уверены, что хотите удалить выбранные заметки?")
        if check:
            note_id_list = get_id_list(
                request_notes_tuple, choice)
            request_delete_note(note_id_list)
            easygui.msgbox("Выбранные заметки успешно удалены")


#Функция формирования строки для вывода в textbox на основе сортированного по дате списка из базы данных заметок 
def print_table(request_notes_list:list):
    final_string = str()
    for i in range (len(request_notes_list)):
        final_string+=request_notes_list[i][1]+"\n"+"       "+request_notes_list[i][2]+"\n"*2       
    easygui.textbox("", "", final_string)

#Вывод всех заметок в хронологическом порядке
def print_all_notes():
    request_notes_tuple = request_notes()

    if request_notes_tuple == []:
        easygui.msgbox("В файле нет ни одной заметки")
        return
    request_notes_list = get_list_of_choice(request_notes_tuple)
    print_table(request_notes_list)


#Вывод указанных заметок
def print_specified_notes():
    request_notes_tuple = request_notes()
    request_note_list = get_list_of_choice(request_notes_tuple)
    choice_list = list()
    for i in range (len(request_note_list)):
        choice_list.append(request_note_list[i][1])   
    if len(choice_list) == 0:
        easygui.msgbox("Нет ни одной заметки в файле")
        return
    elif len(choice_list) == 1:
        check = question_yes_no(f"В файле только одна заметка {choice_list[0]}\nВывести её?")
        if check:
            print_all_notes()
            return
        else:
            return
    choice = easygui.multchoicebox(
        "Выберите заметки для вывода", "Вывод указанных заметок", choice_list)
    if choice == None:
        return
    id_contacts_list = get_id_list(request_notes_tuple, choice)
    selected_notes_list = request_selected_notes(id_contacts_list)
    print_table(get_list_of_choice(selected_notes_list))


#Вывод заметок за определённый период дат, т.к. sql не может на прямую сравнивать даты в запросах, т.к. они в текстовом формате, пришлось немного топорно 
#реализовать функцию вывода заметок за определённый период дат   
def print_date_notes ():
    request_notes_tuple = request_notes()
    if request_notes_tuple == []:
        easygui.msgbox("Нет ни одной заметки в файле")
        return
    while True:
        msg = "Дата начала периода"
        title = "Введите дату начала временного интервала"
        date = ["Год в формате YYYY", "Месяц в формате MM", "День в формате DD"]
        date_list = easygui.multenterbox(msg, title, date)
        if date_list == None:
            return
        if date_list[0] == "":
            date_list[0] = str(datetime.datetime.now().strftime("%Y"))            
        if date_list[1] == "":
           date_list[1] = "01"
        if date_list[2] == "":
           date_list[2] = "01"
        date_string = str
        date_string = f"{date_list[0]}-{date_list[1]}-{date_list[2]} 00:00:00"        
        try:
            start_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
            break
        except:
            check = question_yes_no ("Вы ввели дату в не корректном формате, желаете повторить ввод?")
            if not check:
                return
    while True:
        msg = "Дата окончания периода"
        title = "Введите дату окончания временного интервала"
        date = ["Год в формате YYYY", "Месяц в формате MM", "День в формате DD"]
        date_list = easygui.multenterbox(msg, title, date)
        if date_list == None:
            return
        if date_list[0] == "":
            date_list[0] = str(datetime.datetime.now().strftime("%Y"))            
        if date_list[1] == "":
           date_list[1] = "12"
        if date_list[2] == "":
           date_list[2] = "31"
        date_string = str
        date_string = f"{date_list[0]}-{date_list[1]}-{date_list[2]} 23:59:59"        
        try:
            end_date = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
            break
        except:
            check = question_yes_no ("Вы ввели дату в не корректном формате, желаете повторить ввод?")
            if not check:
                return
    if (start_date > end_date): 
        easygui.msgbox("ОШИБКА, дата начала не может быть больше даты окончания периода")
        return    
    request_notes_list = get_list_of_choice(request_notes_tuple)
    notes_date_period = list()
    for i in range (len(request_notes_list)):
        if (datetime.datetime.strptime(request_notes_list[i][3], "%Y-%m-%d %H:%M:%S") >= start_date and datetime.datetime.strptime(request_notes_list[i][3], "%Y-%m-%d %H:%M:%S") <= end_date):
            notes_date_period.append(request_notes_list[i])
    if (notes_date_period == []):
        easygui.msgbox("За указанный период дат, заметок не найдено")
        return
    print_table(notes_date_period)


#Получение списка для .multchoicebox и .choicebox, внутри функций так же используется сортировка по дате создания/редактирования заметки
def get_list_of_choice(request_tuple: tuple) -> list:
    choice_list = request_tuple.copy()
    for i in range(len(choice_list)):
        choice_list[i] = list(choice_list[i])
    for i in range(len(choice_list)):
        for j in range (len(choice_list[i])):
            if choice_list[i][j] == "NULL" or choice_list[i][j] == "" or choice_list[i][j] == None:
                choice_list[i][j] = " "
    #Сортировка по дате
    choice_list = sorted(choice_list, key=lambda x: datetime.datetime.strptime(x[::][3], "%Y-%m-%d %H:%M:%S"), reverse=True)
    return choice_list


#Получение списка id заметок на основе списка из .multchoicebox, который возвращает список заголовков выбранных заметок
def get_id_list(request_list: tuple, choice: list) -> list:
    id_list = list()
    for item in choice:
        for i in range (len(request_list)):
            if item == request_list[i][1]:
                id_list.append(request_list[i][0])
    return id_list

#Получение одного id, при тех же входных данных, как и в предыдущей функции
def get_id(request_list: tuple, choice: str) -> int:
    for i in range (len(request_list)):
        if request_list[i][1] == choice:           
          return request_list[i][0]

#Закрыть и сохранить базу данных заметок
def close_notes():
    connection.commit()
    cursor.close()
    connection.close()
    easygui.msgbox("Файл заметок успешно сохранён и закрыт")

#Запрос да/нет
def question_yes_no(msg: str) -> bool:
    yes_no = ["Да", "Нет"]
    selection = easygui.ynbox(msg, "", yes_no)
    return selection


while True:
    choice = start_screen()
    if choice == 1:
        add_note()
    elif choice == 2:
        change_note()
    elif choice == 3:
        delete_notes()
    elif choice == 4:
        print_all_notes()
    elif choice == 5:
        print_specified_notes()
    elif choice == 6:
        print_date_notes()
    elif choice == None or choice == 0:
        check = question_yes_no(
            "Закрыть и сохранить файл заметок?")
        if check:
            close_notes()
            break