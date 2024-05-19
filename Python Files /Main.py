import customtkinter as ctk
from customtkinter import E, END, INSERT, LEFT, N, NS, S, SE, SEL, TOP, W, X, Y
import pyodbc
import tkinter as tk
from tkinter import messagebox
import datetime
server = 'DESKTOP-GLJLREN\\MSSQLSERVER01'  ## YOU MUST PUT YOUR SERVER NAME --> You will find it at the begin of SSMS in server name or in the first line in Object Explorer
database = 'UniversityLibrary'             ##Database name DO NOT change it
driver = 'ODBC Driver 17 for SQL Server'   ## ODBC (Open Database Connectivity) driver to be used for connecting to the SQL Server database + driver version + SQL server
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes'

def connect_to_database():
    try:
        connection = pyodbc.connect(connection_string)
        return connection
    except Exception as e:
        print(f'Error connecting to the database: {e}')
        return None

def execute_query(query):
    connection = None
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            print('Query executed successfully.')
    except Exception as e:
        print(f'Error executing query: {e}')
    finally:
        if connection:
            connection.close()

def add_book(book_id, title, price, year, availability, copies, isbn, category, publisher, edition, author_id):
    query = f"\n            INSERT INTO Book (Book_ID, Book_Title, Book_Price, Publication_Year, [Availability], No_copies, ISBN, Category, Publisher, Edition, Author_ID)\n            VALUES ({book_id}, '{title}', {price}, {year}, {availability}, {copies}, '{isbn}', '{category}', '{publisher}', '{edition}', {author_id})\n        "
    execute_query(query)


def edit_book(book_id, title=None, price=None, year=None, availability=None, copies=None, isbn=None, category=None,publisher=None, edition=None, author_id=None):
    if not any([title, price, year, availability, copies, isbn, category, publisher, edition, author_id]):
        print('No updates provided.')
        return

    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()

            update_query = 'UPDATE Book SET '
            update_values = []

            if title:
                update_values.append(f"Book_Title = '{title}'")
            if price:
                update_values.append(f"Book_Price = {price}")
            if year:
                update_values.append(f"Publication_Year = {year}")
            if availability is not None:
                update_values.append(f"[Availability] = {availability}")
            if copies:
                update_values.append(f"No_copies = {copies}")
            if isbn:
                update_values.append(f"ISBN = '{isbn}'")
            if category:
                update_values.append(f"Category = '{category}'")
            if publisher:
                update_values.append(f"Publisher = '{publisher}'")
            if edition:
                update_values.append(f"Edition = '{edition}'")
            if author_id:
                update_values.append(f"Author_ID = {author_id}")

            update_query += ', '.join(update_values)
            update_query += f" WHERE Book_ID = {book_id}"

            cursor.execute(update_query)
            connection.commit()
            print('Book details updated successfully.')
    except Exception as e:
        print(f'Error updating book details: {e}')
    finally:
        if connection:
            connection.close()
def delete_book(book_id):
    query = f'DELETE FROM Book WHERE Book_ID = {book_id}'
    execute_query(query)

def return_book(username, book_id, return_date):
    update_order_query = """
        UPDATE [Order]
        SET Return_Date = ?
        WHERE Order_ID IN (
            SELECT o.Order_ID
            FROM [Order] o
            JOIN BookOrder bo ON o.Order_ID = bo.Order_ID
            JOIN Student s ON o.Student_ID = s.Student_ID
            WHERE s.UserName = ? AND bo.Book_ID = ?
        )
        AND Return_Date IS NULL
    """
    delete_book_order_query = """
        DELETE FROM BookOrder
        WHERE Order_ID IN (
            SELECT o.Order_ID
            FROM [Order] o
            JOIN BookOrder bo ON o.Order_ID = bo.Order_ID
            JOIN Student s ON o.Student_ID = s.Student_ID
            WHERE s.UserName = ? AND bo.Book_ID = ?
        )
        AND Order_ID NOT IN (
            SELECT Order_ID
            FROM [Order]
            WHERE Return_Date IS NULL
        )
    """
    update_book_query = """
        UPDATE Book
        SET No_copies = No_copies + 1,
            Availability = CASE WHEN No_copies + 1 > 0 THEN 1 ELSE Availability END
        WHERE Book_ID = ?
    """
    check_borrow_query = """
        SELECT o.Order_ID
        FROM [Order] o
        JOIN BookOrder bo ON o.Order_ID = bo.Order_ID
        JOIN Student s ON o.Student_ID = s.Student_ID
        WHERE s.UserName = ? AND bo.Book_ID = ? AND o.Return_Date IS NULL
    """
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            # Retrieve Student_ID based on the username
            cursor.execute("SELECT Student_ID FROM Student WHERE UserName = ?", (username,))
            row = cursor.fetchone()
            student_id = row[0] if row else None

            if student_id is None:
                print("Error: Student with the provided username does not exist.")
                return False

            # Check if the student has borrowed this book and hasn't returned it
            cursor.execute(check_borrow_query, (username, book_id))
            order_row = cursor.fetchone()

            if order_row is None:
                print("Error: This student did not borrow this book or the book has already been returned.")
                return False

            # Execute the update order query
            cursor.execute(update_order_query, (return_date, username, book_id))

            # Execute the delete book order query
            cursor.execute(delete_book_order_query, (username, book_id))

            # Execute the update book availability query
            cursor.execute(update_book_query, (book_id,))

            connection.commit()  # Commit changes to the database
            connection.close()
            return True
    except Exception as e:
        print(f'Error returning book: {e}')
        return False


def display_books():
    query = """
    SELECT 
        b.Book_ID,
        b.Book_Title,
        b.Book_Price,
        b.Publication_Year,
        b.ISBN,
        a.[Name] AS Author_Name,
        b.Category
    FROM 
        Book b
    LEFT JOIN 
        Author a ON b.Author_ID = a.Author_ID
    """
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute(query)
            books = cursor.fetchall()
            if books:
                result = 'Books available in the library:\n'
                for book in books:
                    result += f'Book ID: {book[0]}, Title: {book[1]}, Price: {book[2]}, Publication Year: {book[3]}, ISBN: {book[4]}, Author: {book[5]}, Category: {book[6]}\n'
                    result += '------------------------------\n'
                connection.close()
                return result
            else:
                connection.close()
                return 'No books found in the library.'
    except Exception as e:
        print(f'Error displaying books: {e}')
        return 'Error displaying books.'
def sign_in(username, password, user_type):
    table = 'Admin' if user_type == 'admin' else 'Student'
    query = f"SELECT * FROM {table} WHERE Username = '{username}' AND Password = '{password}'"
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute(query)
            user = cursor.fetchone()
            connection.close()
            return bool(user)
    except Exception as e:
        print(f'Error signing in: {e}')
        return False

def sign_up(username, password, user_type, first_name, last_name, email, address, phone_number):
    table = 'Admin' if user_type == 'admin' else 'Student'
    id_column = 'Admin_ID' if user_type == 'admin' else 'Student_ID'
    query_id = f'SELECT MAX({id_column}) FROM {table}'
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute(query_id)
            max_id = cursor.fetchone()[0]
            new_id = (max_id if max_id else 0) + 1
            if table == 'Student':
                query = f"\n                INSERT INTO {table} ({id_column}, FName, LName, Username, Password, Email, Address,PhoneNumber)\n                VALUES ({new_id}, '{first_name}', '{last_name}', '{username}', '{password}', '{email}', '{address}','{phone_number}')\n            "
            else:
                query = f"\n                INSERT INTO {table} ({id_column}, FName, LName, Username, Password, Email, Address)\n                VALUES ({new_id}, '{first_name}', '{last_name}', '{username}', '{password}', '{email}', '{address}')\n                "
            execute_query(query)
            return True
    except Exception as e:
        print(f'Error signing up: {e}')
        return False



def borrow_book(username, book_id):
    borrow_date = datetime.date.today()
    due_date = borrow_date + datetime.timedelta(days=14)  # Assuming a 2-week borrowing period

    # Retrieve Student_ID based on the username
    get_student_id_query = """
        SELECT Student_ID FROM Student WHERE UserName = ?
    """

    # First, update the book's number of copies and availability if needed
    update_book_query = """
        UPDATE Book
        SET No_copies = No_copies - 1,
            Availability = CASE WHEN No_copies - 1 = 0 THEN 0 ELSE Availability END
        WHERE Book_ID = ? AND No_copies > 0
    """

    # Second, insert a new order into the Order table
    insert_order_query = """
        INSERT INTO [Order] (Order_ID, Borrow_Date, Due_Date, Student_ID)
        VALUES (?, ?, ?, ?)
    """

    # Third, insert into the BookOrder table to link the book with the order
    insert_book_order_query = """
        INSERT INTO BookOrder (Book_ID, Order_ID)
        VALUES (?, ?)
    """

    try:
        connection = connect_to_database()  # Replace with your connection details
        cursor = connection.cursor()

        # Retrieve Student_ID based on the username
        cursor.execute(get_student_id_query, (username,))
        row = cursor.fetchone()
        student_id = row[0] if row else None

        if student_id is None:
            print("Error: Student with the provided username does not exist.")
            return False

        # Execute the update book query
        cursor.execute(update_book_query, (book_id,))

        if cursor.rowcount > 0:
            # Only proceed if the book's number of copies was successfully updated

            # Fetch the current maximum Order_ID and increment it by one
            cursor.execute("SELECT MAX(Order_ID) FROM [Order]")
            max_order_id = cursor.fetchone()[0]
            order_id = max_order_id + 1 if max_order_id is not None else 1

            # Execute insert order query
            cursor.execute(insert_order_query, (order_id, borrow_date, due_date, student_id))

            # Insert into BookOrder table to link the book with the order
            cursor.execute(insert_book_order_query, (book_id, order_id))

            connection.commit()
            connection.close()
            return True
        else:
            print("Error: The book is not available for borrowing.")
            connection.close()
            return False
    except Exception as e:
        print(f'Error borrowing book: {e}')
        return False

def update_user_details(username, first_name=None, last_name=None, address=None, password=None):
    if not any([first_name, last_name, address, password]):
        print('No updates provided.')
        return
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM Admin WHERE Username = '{username}'")
            admin_user = cursor.fetchone()
            cursor.execute(f"SELECT * FROM Student WHERE Username = '{username}'")
            student_user = cursor.fetchone()
            if admin_user:
                update_query = 'UPDATE Admin SET'
                update_values = []
                if first_name:
                    update_values.append(f"FName = '{first_name}'")
                if last_name:
                    update_values.append(f"LName = '{last_name}'")
                if address:
                    update_values.append(f"Address = '{address}'")
                if password:
                    update_values.append(f"Password = '{password}'")
                update_query += ' ' + ', '.join(update_values)
                update_query += f" WHERE Username = '{username}'"
                cursor.execute(update_query)
                connection.commit()
                print('Admin details updated successfully.')
            elif student_user:
                update_query = 'UPDATE Student SET'
                update_values = []
                if first_name:
                    update_values.append(f"FName = '{first_name}'")
                if last_name:
                    update_values.append(f"LName = '{last_name}'")
                if address:
                    update_values.append(f"Address = '{address}'")
                if password:
                    update_values.append(f"Password = '{password}'")
                update_query += ' ' + ', '.join(update_values)
                update_query += f" WHERE Username = '{username}'"
                cursor.execute(update_query)
                connection.commit()
                print('Student details updated successfully.')
            else:
                print(f'No user found with username: {username}')
    except Exception as e:
        print(f'Error updating user details: {e}')
    finally:
        if connection:
            connection.close()

def execute_search_query(query):
    connection = None
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute(query)
            books = cursor.fetchall()
            connection.close()
            return books
    except Exception as e:
        print(f"Error executing search query: {e}")
        return None
def delete_student(username):
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM Student WHERE username = '{username}'")
            student = cursor.fetchone()
            if student:
                cursor.execute(f"DELETE FROM Student WHERE username = '{username}'")
                connection.commit()
                return True
            else:
                print("Student does not exist.")
    except Exception as e:
        print(f"Error deleting student: {e}")
    finally:
        if connection:
            connection.close()
    return False

class LibraryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Library Management System')
        self.geometry('800x600')  # Set the initial window size

        container = ctk.CTkFrame(self)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid(row=0, column=0, sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomePage, SignInPage, SignUpPage, AdminPage, StudentPage, EditBookPage, DeleteBookPage, DisplayBooksPage, BorrowBookPage, AddBookPage, UpdateDetailsPage,SearchBooksPage , ReturnBookPage ,DeleteStudentPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame('HomePage')

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.user_type = tk.StringVar(value='admin')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(self, text='Library Management System', font=('Arial', 24))
        label.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')

        button_login = ctk.CTkButton(self, text='Login', command=lambda: controller.show_frame('SignInPage'))
        button_login.grid(row=1, column=0, padx=20, pady=20, sticky='nsew')

        button_signup = ctk.CTkButton(self, text='Sign Up', command=lambda: controller.show_frame('SignUpPage'))
        button_signup.grid(row=2, column=0, padx=20, pady=20, sticky='nsew')

    def go_back(self):
        if self.user_type.get() == 'admin':
            self.controller.show_frame('AdminPage')
        else:
            self.controller.show_frame('StudentPage')

class SignInPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text='Log in', font=('Arial', 18)).pack(pady=10)
        username_frame = ctk.CTkFrame(self)
        username_frame.pack(pady=5)
        ctk.CTkLabel(username_frame, text='Username').pack(side=tk.LEFT)
        self.entry_username = ctk.CTkEntry(username_frame)
        self.entry_username.pack(side=tk.LEFT)
        password_frame = ctk.CTkFrame(self)
        password_frame.pack(pady=5)
        ctk.CTkLabel(password_frame, text='Password').pack(side=tk.LEFT)
        self.entry_password = ctk.CTkEntry(password_frame, show='*')
        self.entry_password.pack(side=tk.LEFT)
        ctk.CTkLabel(self, text='User Type').pack(pady=5)
        self.user_type = tk.StringVar(value='admin')
        user_type_frame = ctk.CTkFrame(self)
        user_type_frame.pack(pady=5)
        ctk.CTkRadioButton(user_type_frame, text='Admin', variable=self.user_type, value='admin').pack(side=tk.LEFT)
        ctk.CTkRadioButton(user_type_frame, text='Student', variable=self.user_type, value='student').pack(side=tk.LEFT)
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text='Login', command=self.submit_sign_in).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(button_frame, text='Back', command=self.go_back).pack(side=tk.LEFT, padx=5)

    def submit_sign_in(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        user_type = self.user_type.get()
        if sign_in(username, password, user_type):
            home_page = self.controller.frames['HomePage']
            home_page.user_type.set(user_type)
            if user_type == 'admin':
                self.controller.show_frame('AdminPage')
            else:
                self.controller.show_frame('StudentPage')
        else:
            messagebox.showerror('Error', 'Invalid username or password')

    def go_back(self):
        self.controller.show_frame('HomePage')

class SignUpPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text='Sign Up', font=('Arial', 18)).pack(pady=10)
        ctk.CTkLabel(self, text='First Name *').pack()
        self.entry_first_name = ctk.CTkEntry(self)
        self.entry_first_name.pack()
        ctk.CTkLabel(self, text='Last Name *').pack()
        self.entry_last_name = ctk.CTkEntry(self)
        self.entry_last_name.pack()
        ctk.CTkLabel(self, text='Username *').pack()
        self.entry_username = ctk.CTkEntry(self)
        self.entry_username.pack()
        ctk.CTkLabel(self, text='Password *').pack()
        self.entry_password = ctk.CTkEntry(self, show='*')
        self.entry_password.pack()
        ctk.CTkLabel(self, text='Email *').pack()
        self.entry_email = ctk.CTkEntry(self)
        self.entry_email.pack()
        ctk.CTkLabel(self, text='Phone Number (for Students)').pack()
        self.entry_phone_number = ctk.CTkEntry(self)
        self.entry_phone_number.pack()
        ctk.CTkLabel(self, text='Address').pack()
        self.entry_address = ctk.CTkEntry(self)
        self.entry_address.pack()
        ctk.CTkLabel(self, text='User Type').pack()
        self.user_type = tk.StringVar(value='admin')
        ctk.CTkRadioButton(self, text='Admin', variable=self.user_type, value='admin').pack()
        ctk.CTkRadioButton(self, text='Student', variable=self.user_type, value='student').pack()
        ctk.CTkButton(self, text='Sign Up', command=self.submit_sign_up).pack(pady=10)
        ctk.CTkButton(self, text='Back', command=lambda: controller.show_frame('HomePage')).pack(pady=10)

    def submit_sign_up(self):
        first_name = self.entry_first_name.get()
        last_name = self.entry_last_name.get()
        username = self.entry_username.get()
        password = self.entry_password.get()
        email = self.entry_email.get()
        phone_number = self.entry_phone_number.get()
        address = self.entry_address.get()
        user_type = self.user_type.get()
        if not all([first_name, last_name, username, password, email]):
            messagebox.showerror('Error', 'Please fill in all required fields .')
            return
        if sign_up(username, password, user_type, first_name, last_name, email, address, phone_number):
            messagebox.showinfo('Success', 'Sign up successful!')
            self.controller.show_frame('SignInPage')
        else:
            messagebox.showerror('Error', 'Sign up failed. Please try again.')

class AdminPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text='Admin Dashboard', font=('Arial', 18)).pack(pady=10)
        ctk.CTkButton(self, text='Search Books', command=lambda: controller.show_frame('SearchBooksPage')).pack(pady=10)
        ctk.CTkButton(self, text='Add Book', command=lambda: controller.show_frame('AddBookPage')).pack(pady=10)
        ctk.CTkButton(self, text='Edit Book', command=lambda: controller.show_frame('EditBookPage')).pack(pady=10)
        ctk.CTkButton(self, text='Delete Book', command=lambda: controller.show_frame('DeleteBookPage')).pack(pady=10)
        ctk.CTkButton(self, text='View Book List', command=lambda: controller.show_frame('DisplayBooksPage')).pack(pady=10)
        ctk.CTkButton(self, text='Update Details', command=lambda: controller.show_frame('UpdateDetailsPage')).pack(pady=10)
        ctk.CTkButton(self, text='Delete Student', command=lambda: controller.show_frame('DeleteStudentPage')).pack(pady=10)

        ctk.CTkButton(self, text='Log Out', command=lambda: controller.show_frame('HomePage')).pack(pady=10)

class StudentPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text='Student Dashboard', font=('Arial', 18)).pack(pady=10)
        ctk.CTkButton(self, text='Search Books', command=lambda: controller.show_frame('SearchBooksPage')).pack(pady=10)
        ctk.CTkButton(self, text='View Book List', command=lambda: controller.show_frame('DisplayBooksPage')).pack(pady=10)
        ctk.CTkButton(self, text='Borrow Book', command=lambda: controller.show_frame('BorrowBookPage')).pack(pady=10)
        ctk.CTkButton(self, text='Return Book', command=lambda: controller.show_frame('ReturnBookPage')).pack(pady=10)
        ctk.CTkButton(self, text='Update Details', command=lambda: controller.show_frame('UpdateDetailsPage')).pack(pady=10)
        ctk.CTkButton(self, text='Log Out', command=lambda: controller.show_frame('HomePage')).pack(pady=10)

class AddBookPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text='Add Book', font=('Arial', 18)).pack(pady=10)
        frame_add_book = ctk.CTkFrame(self)
        frame_add_book.pack(pady=10)
        ctk.CTkLabel(frame_add_book, text='Book ID').grid(row=0, column=0)
        self.entry_book_id = ctk.CTkEntry(frame_add_book)
        self.entry_book_id.grid(row=0, column=1)
        ctk.CTkLabel(frame_add_book, text='Title').grid(row=1, column=0)
        self.entry_title = ctk.CTkEntry(frame_add_book)
        self.entry_title.grid(row=1, column=1)
        ctk.CTkLabel(frame_add_book, text='Price').grid(row=2, column=0)
        self.entry_price = ctk.CTkEntry(frame_add_book)
        self.entry_price.grid(row=2, column=1)
        ctk.CTkLabel(frame_add_book, text='Publication Year').grid(row=3, column=0)
        self.entry_year = ctk.CTkEntry(frame_add_book)
        self.entry_year.grid(row=3, column=1)
        ctk.CTkLabel(frame_add_book, text='Availability').grid(row=4, column=0)
        self.entry_availability = ctk.CTkEntry(frame_add_book)
        self.entry_availability.grid(row=4, column=1)
        ctk.CTkLabel(frame_add_book, text='Number of Copies').grid(row=5, column=0)
        self.entry_copies = ctk.CTkEntry(frame_add_book)
        self.entry_copies.grid(row=5, column=1)
        ctk.CTkLabel(frame_add_book, text='ISBN').grid(row=6, column=0)
        self.entry_isbn = ctk.CTkEntry(frame_add_book)
        self.entry_isbn.grid(row=6, column=1)
        ctk.CTkLabel(frame_add_book, text='Category').grid(row=7, column=0)
        self.entry_category = ctk.CTkEntry(frame_add_book)
        self.entry_category.grid(row=7, column=1)
        ctk.CTkLabel(frame_add_book, text='Publisher').grid(row=8, column=0)
        self.entry_publisher = ctk.CTkEntry(frame_add_book)
        self.entry_publisher.grid(row=8, column=1)
        ctk.CTkLabel(frame_add_book, text='Edition').grid(row=9, column=0)
        self.entry_edition = ctk.CTkEntry(frame_add_book)
        self.entry_edition.grid(row=9, column=1)
        ctk.CTkLabel(frame_add_book, text='Author ID').grid(row=10, column=0)
        self.entry_author_id = ctk.CTkEntry(frame_add_book)
        self.entry_author_id.grid(row=10, column=1)
        ctk.CTkButton(frame_add_book, text='Add Book', command=self.submit_add_book).grid(row=11, columnspan=2, pady=10)
        ctk.CTkButton(frame_add_book, text='Back', command=lambda: controller.show_frame('AdminPage')).grid(row=12, columnspan=2, pady=10)

    def submit_add_book(self):
        try:
            book_id = int(self.entry_book_id.get())
            title = self.entry_title.get()
            price = float(self.entry_price.get())
            year = int(self.entry_year.get())
            availability = int(self.entry_availability.get())
            copies = int(self.entry_copies.get())
            isbn = self.entry_isbn.get()
            category = self.entry_category.get()
            publisher = self.entry_publisher.get()
            edition = self.entry_edition.get()
            author_id = int(self.entry_author_id.get())
            add_book(book_id, title, price, year, availability, copies, isbn, category, publisher, edition, author_id)
            messagebox.showinfo('Add Book', 'Book added successfully!')
        except ValueError:
            messagebox.showerror('Error', 'Please enter valid numeric values for Book ID, Price, Publication Year, Availability, Number of Copies, Author ID, and Admin ID.')
        except Exception as e:
            messagebox.showerror('Error', f'An error occurred: {e}')


class EditBookPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text='Edit Book', font=('Arial', 18)).pack(pady=10)
        frame_edit_book = ctk.CTkFrame(self)
        frame_edit_book.pack(pady=10)
        ctk.CTkLabel(frame_edit_book, text='Book ID').grid(row=0, column=0)
        self.entry_book_id = ctk.CTkEntry(frame_edit_book)
        self.entry_book_id.grid(row=0, column=1)
        ctk.CTkLabel(frame_edit_book, text='Title').grid(row=1, column=0)
        self.entry_title = ctk.CTkEntry(frame_edit_book)
        self.entry_title.grid(row=1, column=1)
        ctk.CTkLabel(frame_edit_book, text='Price').grid(row=2, column=0)
        self.entry_price = ctk.CTkEntry(frame_edit_book)
        self.entry_price.grid(row=2, column=1)
        ctk.CTkLabel(frame_edit_book, text='Publication Year').grid(row=3, column=0)
        self.entry_year = ctk.CTkEntry(frame_edit_book)
        self.entry_year.grid(row=3, column=1)
        ctk.CTkLabel(frame_edit_book, text='Availability').grid(row=4, column=0)
        self.entry_availability = ctk.CTkEntry(frame_edit_book)
        self.entry_availability.grid(row=4, column=1)
        ctk.CTkLabel(frame_edit_book, text='Number of Copies').grid(row=5, column=0)
        self.entry_copies = ctk.CTkEntry(frame_edit_book)
        self.entry_copies.grid(row=5, column=1)
        ctk.CTkLabel(frame_edit_book, text='ISBN').grid(row=6, column=0)
        self.entry_isbn = ctk.CTkEntry(frame_edit_book)
        self.entry_isbn.grid(row=6, column=1)
        ctk.CTkLabel(frame_edit_book, text='Category').grid(row=7, column=0)
        self.entry_category = ctk.CTkEntry(frame_edit_book)
        self.entry_category.grid(row=7, column=1)
        ctk.CTkLabel(frame_edit_book, text='Publisher').grid(row=8, column=0)
        self.entry_publisher = ctk.CTkEntry(frame_edit_book)
        self.entry_publisher.grid(row=8, column=1)
        ctk.CTkLabel(frame_edit_book, text='Edition').grid(row=9, column=0)
        self.entry_edition = ctk.CTkEntry(frame_edit_book)
        self.entry_edition.grid(row=9, column=1)
        ctk.CTkLabel(frame_edit_book, text='Author ID').grid(row=10, column=0)
        self.entry_author_id = ctk.CTkEntry(frame_edit_book)
        self.entry_author_id.grid(row=10, column=1)
        ctk.CTkButton(frame_edit_book, text='Edit Book', command=self.submit_edit_book).grid(row=11, columnspan=2, pady=10)
        ctk.CTkButton(frame_edit_book, text='Back', command=lambda: controller.show_frame('AdminPage')).grid(row=12,  columnspan=2,  pady=10)

    def submit_edit_book(self):
        book_id = self.entry_book_id.get()
        title = self.entry_title.get() or None
        price = self.entry_price.get() or None
        year = self.entry_year.get() or None
        availability = self.entry_availability.get() or None
        copies = self.entry_copies.get() or None
        isbn = self.entry_isbn.get() or None
        category = self.entry_category.get() or None
        publisher = self.entry_publisher.get() or None
        edition = self.entry_edition.get() or None
        author_id = self.entry_author_id.get() or None

        if not any([title, price, year, availability, copies, isbn, category, publisher, edition, author_id]):
            messagebox.showerror('Error', 'Please provide at least one value to update.')
            return

        edit_book(book_id, title=title, price=price, year=year, availability=availability, copies=copies, isbn=isbn,  category=category, publisher=publisher, edition=edition, author_id=author_id)
        messagebox.showinfo('Edit Book', 'Book details updated successfully!')
class DeleteBookPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text='Delete Book', font=('Arial', 18)).pack(pady=10)
        frame_delete_book = ctk.CTkFrame(self)
        frame_delete_book.pack(pady=10)
        ctk.CTkLabel(frame_delete_book, text='Book ID').grid(row=0, column=0)
        self.entry_book_id = ctk.CTkEntry(frame_delete_book)
        self.entry_book_id.grid(row=0, column=1)
        ctk.CTkButton(frame_delete_book, text='Delete Book', command=self.submit_delete_book).grid(row=1, columnspan=2, pady=10)
        ctk.CTkButton(frame_delete_book, text='Back', command=lambda: controller.show_frame('AdminPage')).grid(row=2, columnspan=2, pady=10)

    def submit_delete_book(self):
        book_id = int(self.entry_book_id.get())
        delete_book(book_id)
        messagebox.showinfo('Delete Book', 'Book deleted successfully!')



class BorrowBookPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text='Borrow Book', font=('Arial', 18)).pack(pady=(20, 10))

        frame_borrow_book = ctk.CTkFrame(self)
        frame_borrow_book.pack(pady=10)

        ctk.CTkLabel(frame_borrow_book, text='Student Username:').grid(row=0, column=0, sticky=E, padx=(0, 10))
        self.entry_username = ctk.CTkEntry(frame_borrow_book)
        self.entry_username.grid(row=0, column=1, sticky=W)

        ctk.CTkLabel(frame_borrow_book, text='Book ID:').grid(row=1, column=0, sticky=E, padx=(0, 10))
        self.entry_book_id = ctk.CTkEntry(frame_borrow_book)
        self.entry_book_id.grid(row=1, column=1, sticky=W)

        ctk.CTkButton(frame_borrow_book, text='Borrow Book', command=self.submit_borrow_book).grid(row=2, columnspan=2, pady=10)
        ctk.CTkButton(frame_borrow_book, text='Back', command=lambda: controller.show_frame('StudentPage')).grid(row=3, columnspan=2, pady=10)

    def submit_borrow_book(self):
        username = self.entry_username.get()
        book_id = self.entry_book_id.get()

        # Check if username or book_id are empty
        if not username.strip() or not book_id.strip():
            messagebox.showerror('Error', 'Please enter both the username and book ID.')
            return

        # Convert book_id to integer
        try:
            book_id = int(book_id)
        except ValueError:
            messagebox.showerror('Error', 'Please enter a valid book ID.')
            return

        # Call the borrow_book function
        success = borrow_book(username, book_id)

        if success:
            messagebox.showinfo('Borrow Book', 'Book borrowed successfully!')
        else:
            messagebox.showerror('Error', 'Failed to borrow book.')

class DisplayBooksPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text='Books List', font=('Arial', 18)).pack(pady=10)
        self.text_display_books = ctk.CTkTextbox(self, width=600, height=400)
        self.text_display_books.pack(pady=10)
        ctk.CTkButton(self, text='Refresh', command=self.display_books).pack(pady=10)
        ctk.CTkButton(self, text='Back', command=self.go_back).pack(pady=10)
        self.display_books()

    def display_books(self):
        books = display_books()
        self.text_display_books.delete(1.0, tk.END)
        self.text_display_books.insert(tk.END, books)

    def go_back(self):
        current_page = self.controller.frames['HomePage']
        if current_page.user_type.get() == 'admin':
            self.controller.show_frame('AdminPage')
        else:
            self.controller.show_frame('StudentPage')

class UpdateDetailsPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text='Update Details', font=('Arial', 18)).pack(pady=10)
        frame_update_details = ctk.CTkFrame(self)
        frame_update_details.pack(pady=10)
        ctk.CTkLabel(frame_update_details, text='Username to be Updated').grid(row=0, column=0)
        self.entry_username = ctk.CTkEntry(frame_update_details)
        self.entry_username.grid(row=0, column=1)
        ctk.CTkLabel(frame_update_details, text='First Name').grid(row=1, column=0)
        self.entry_first_name = ctk.CTkEntry(frame_update_details)
        self.entry_first_name.grid(row=1, column=1)
        ctk.CTkLabel(frame_update_details, text='Last Name').grid(row=2, column=0)
        self.entry_last_name = ctk.CTkEntry(frame_update_details)
        self.entry_last_name.grid(row=2, column=1)
        ctk.CTkLabel(frame_update_details, text='Address').grid(row=3, column=0)
        self.entry_address = ctk.CTkEntry(frame_update_details)
        self.entry_address.grid(row=3, column=1)
        ctk.CTkLabel(frame_update_details, text='Password').grid(row=4, column=0)
        self.entry_password = ctk.CTkEntry(frame_update_details, show='*')
        self.entry_password.grid(row=4, column=1)
        ctk.CTkButton(frame_update_details, text='Update Details', command=self.submit_update_details).grid(row=5, columnspan=2, pady=10)
        ctk.CTkButton(self, text='Back', command=self.go_back).pack(pady=10)

    def submit_update_details(self):
        username = self.entry_username.get()
        first_name = self.entry_first_name.get()
        last_name = self.entry_last_name.get()
        address = self.entry_address.get()
        password = self.entry_password.get()
        if not any([first_name, last_name, address, password]):
            messagebox.showerror('Error', 'Please provide at least one value to update.')
            return
        update_user_details(username, first_name=first_name, last_name=last_name, address=address, password=password)
        messagebox.showinfo('Update Details', 'Details updated successfully!')

    def go_back(self):
            current_page = self.controller.frames['HomePage']
            if current_page.user_type.get() == 'admin':
                self.controller.show_frame('AdminPage')
            else:
                self.controller.show_frame('StudentPage')

class SearchBooksPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text='Search Books', font=('Arial', 18)).pack(pady=10)
        frame_search = ctk.CTkFrame(self)
        frame_search.pack(pady=10)
        ctk.CTkLabel(frame_search, text='ISBN:').grid(row=0, column=0)
        self.entry_isbn = ctk.CTkEntry(frame_search)
        self.entry_isbn.grid(row=0, column=1)
        ctk.CTkLabel(frame_search, text='Publication Year:').grid(row=1, column=0)
        self.entry_year = ctk.CTkEntry(frame_search)
        self.entry_year.grid(row=1, column=1)
        ctk.CTkLabel(frame_search, text='Author:').grid(row=2, column=0)
        self.entry_author = ctk.CTkEntry(frame_search)
        self.entry_author.grid(row=2, column=1)
        ctk.CTkButton(frame_search, text='Search', command=self.search_books).grid(row=3, columnspan=2, pady=10)
        self.text_search_results = ctk.CTkTextbox(self, width=400, height=200)
        self.text_search_results.pack(pady=10)
        ctk.CTkButton(self, text='Back', command=self.go_back).pack(pady=10)

    def search_books(self):
        isbn = self.entry_isbn.get()
        year = self.entry_year.get()
        author = self.entry_author.get()

        query = '''
            SELECT 
                b.Book_ID,
                b.Book_Title,
                b.Book_Price,
                b.Publication_Year,
                b.Availability,
                b.No_copies,
                b.ISBN,
                b.Category,
                b.Publisher,
                b.Edition,
                a.Name AS Author_Name
            FROM 
                Book b
            LEFT JOIN 
                Author a ON b.Author_ID = a.Author_ID
            WHERE 1=1
        '''

        if isbn:
            query += f" AND b.ISBN = '{isbn}'"
        if year:
            query += f" AND b.Publication_Year = {year}"
        if author:
            query += f" AND a.Name LIKE '%{author}%'"

        books = execute_search_query(query)

        if books:
            self.text_search_results.delete(1.0, tk.END)
            for book in books:
                book_details = f"Book ID: {book[0]}\nTitle: {book[1]}\nPrice: {book[2]}\nPublication Year: {book[3]}\nAvailability: {book[4]}\nNumber of Copies: {book[5]}\nISBN: {book[6]}\nCategory: {book[7]}\nPublisher: {book[8]}\nEdition: {book[9]}\nAuthor: {book[10]}\n\n"

                self.text_search_results.insert(tk.END, book_details)
        else:
            self.text_search_results.delete(1.0, tk.END)
            self.text_search_results.insert(tk.END, 'No books found matching the criteria.')

    def go_back(self):
        current_page = self.controller.frames['HomePage']
        if current_page.user_type.get() == 'admin':
            self.controller.show_frame('AdminPage')
        else:
            self.controller.show_frame('StudentPage')

class ReturnBookPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text='Return Book', font=('Arial', 18)).pack(pady=10)
        frame_return_book = ctk.CTkFrame(self)
        frame_return_book.pack(pady=10)
        ctk.CTkLabel(frame_return_book, text='Student Username').grid(row=0, column=0)
        self.entry_username = ctk.CTkEntry(frame_return_book)
        self.entry_username.grid(row=0, column=1)
        ctk.CTkLabel(frame_return_book, text='Book ID').grid(row=1, column=0)
        self.entry_book_id = ctk.CTkEntry(frame_return_book)
        self.entry_book_id.grid(row=1, column=1)
        ctk.CTkButton(frame_return_book, text='Return Book', command=self.submit_return_book).grid(row=2, columnspan=2, pady=10)
        ctk.CTkButton(frame_return_book, text='Back', command=lambda: controller.show_frame('StudentPage')).grid(row=3, columnspan=2, pady=10)

    def submit_return_book(self):
        username = self.entry_username.get()
        book_id = int(self.entry_book_id.get())
        return_date = datetime.date.today()

        if return_book(username, book_id, return_date):
            messagebox.showinfo('Return Book', 'Book returned successfully!')
        else:
            messagebox.showerror('Error', 'Failed to return book. Please check the details.')
class DeleteStudentPage(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.CTkLabel(self, text='Delete Student', font=('Arial', 18)).pack(pady=10)
        frame_delete_student = ctk.CTkFrame(self)
        frame_delete_student.pack(pady=10)
        ctk.CTkLabel(frame_delete_student, text='Student username').grid(row=0, column=0)
        self.entry_username = ctk.CTkEntry(frame_delete_student)
        self.entry_username.grid(row=0, column=1)
        ctk.CTkButton(frame_delete_student, text='Delete Student', command=self.submit_delete_student).grid(row=1, columnspan=2, pady=10)
        ctk.CTkButton(frame_delete_student, text='Back', command=lambda: controller.show_frame('AdminPage')).grid(row=2, columnspan=2, pady=10)

    def submit_delete_student(self):
        username = self.entry_username.get()
        # Call the delete_student function passing the student_id
        if delete_student(username):
            messagebox.showinfo('Delete Student', 'Student deleted successfully!')
        else:
            messagebox.showerror('Error', 'Failed to delete student. Please try again.')


if __name__ == '__main__':
    app = LibraryApp()
    app.mainloop()
