# First you must Create Database tables you can find Schema in Schema file
import pyodbc
# Connection parameters
server = 'DESKTOP-GLJLREN\\MSSQLSERVER01'   ## YOU MUST PUT YOUR SERVER NAME --> You will find it at the begin of SSMS in server name or in the first line in Object Explorer
database = 'UniversityLibrary'              ##Database name DO NOT change it
driver = 'ODBC Driver 17 for SQL Server'    ## ODBC (Open Database Connectivity) driver to be used for connecting to the SQL Server database + driver version + SQL server

connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes" # Create the connection string for a trusted connection

def connect_to_database():
    try:
        connection = pyodbc.connect(connection_string)
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def execute_query(query):     # put this function at the end of each function to Execute query
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            print("Query executed successfully.")
            connection.close()
    except Exception as e:
        print(f"Error executing query: {e}")

def add_book(book_id, title, price, year, availability, copies, isbn, category, publisher, edition, author_id, admin_id):
    query = f"""
            INSERT INTO Book (Book_ID, Book_Title, Book_Price, Publication_Year, [Availability], No_copies, ISBN, Category, Publisher, Edition, Author_ID, Admin_ID)
            VALUES ({book_id}, '{title}', {price}, {year}, {availability}, {copies}, '{isbn}', '{category}', '{publisher}', '{edition}', {author_id}, {admin_id})
        """
    execute_query(query)

def add_admin():
    pass

def add_student():
    pass

def update_user_details():
    pass

def update_book_details():
    pass

def browse_books():
    pass

def show_books_by_criteria(criteria):
    pass

def display_book():
    query = """
            SELECT Book_ID, Book_Title, Book_Price, Publication_Year, [Availability], No_copies, ISBN, Category, Publisher, Edition, Author_ID, Admin_ID
            FROM Book
            """
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute(query)
            books = cursor.fetchall()
            if books:
                print("Books available in the library:")
                for book in books:
                    print("Book ID:", book[0])
                    print("Title:", book[1])
                    print("Price:", book[2])
                    print("Publication Year:", book[3])
                    print("Availability:", book[4])
                    print("Number of Copies:", book[5])
                    print("ISBN:", book[6])
                    print("Category:", book[7])
                    print("Publisher:", book[8])
                    print("Edition:", book[9])
                    print("Author ID:", book[10])
                    print("Admin ID:", book[11])
                    print("------------------------------")
            else:
                print("No books found in the library.")
            connection.close()
    except Exception as e:
        print(f"Error displaying books: {e}")

def main():
    # Example usage: Adding a book
    add_book(
        book_id=1,
        title="Python Programming",
        price=29.99,
        year=2020,
        availability=1,
        copies=10,
        isbn="978-0-13-444432-1",
        category="Programming",
        publisher="Example Publisher",
        edition="1st Edition",
        author_id=1,
        admin_id=1
    )

    # Example usage: Adding an admin
    # add_admin()

    # Example usage: Adding a student
    # add_student()

    # Example usage: Updating a user's details
    # update_user_details()

    # Example usage: Updating a book's details
    # update_book_details()

    # Example usage: Browsing books
    # browse_books()

    # Example usage: Showing books by certain criteria
    # show_books_by_criteria(criteria)

    # Displaying books
    display_book()

if __name__ == "__main__":
    main()
