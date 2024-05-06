USE UniversityLibrary;

-- Insert into Admin Table
INSERT INTO [Admin] (Admin_ID, FName, LName, Username, [Password], Email, [Address])
VALUES 
(1, 'John', 'Doe', 'johndoe', 'password123', 'john.doe@example.com', '123 Main St'),
(2, 'Jane', 'Smith', 'janesmith', 'password456', 'jane.smith@example.com', '456 Elm St');

-- Insert into Author Table
INSERT INTO Author (Author_ID, [Name], Biography)
VALUES 
(1, 'J.K. Rowling', 'Author of the Harry Potter series'),
(2, 'George R.R. Martin', 'Author of A Song of Ice and Fire');

-- Insert into Book Table
INSERT INTO Book (Book_ID, Book_Title, Book_Price, Publication_Year, [Availability], No_copies, ISBN, Category, Publisher, Edition, Author_ID, Admin_ID)
VALUES 
(1, 'Harry Potter and the Sorcerers Stone', 19.99, 1997, 1, 10, '9780439708180', 'Fantasy', 'Scholastic', '1st', 1, 1),
(2, 'A Game of Thrones', 24.99, 1996, 1, 15, '9780553103540', 'Fantasy', 'Bantam Books', '1st', 2, 2);

-- Insert into Student Table
INSERT INTO Student (Student_ID, FName, LName, UserName, [Password], Email, [Address])
VALUES 
(1, 'Alice', 'Johnson', 'alicej', 'password789', 'alice.johnson@example.com', '789 Oak St'),
(2, 'Bob', 'Williams', 'bobw', 'password012', 'bob.williams@example.com', '321 Pine St');

-- Insert into PhoneNumber Table
INSERT INTO PhoneNumber (Phone_ID, Student_ID, PhoneNumber)
VALUES 
(1, 1, '123-456-7890'),
(2, 2, '098-765-4321');

-- Insert into [Order] Table
INSERT INTO [Order] (Order_ID, Borrow_Date, Return_Date, Due_Date, Student_ID)
VALUES 
(1, '2024-04-01', '2024-04-15', '2024-04-20', 1),
(2, '2024-04-05', '2024-04-19', '2024-04-25', 2);

-- Insert into BookOrder Table
INSERT INTO BookOrder (Book_ID, Order_ID)
VALUES 
(1, 1),
(2, 2);
