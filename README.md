# University Library Management System

Welcome to the University Library Management System repository. This project is designed to manage a university library, allowing users (students and admins) to sign up, borrow books, and update their details , search for book . Admins can add books, update book information, and manage book orders.

## Table of Contents
- [Project Description](#project-description)
- [Conceptual ERD](#conceptual-erd)
- [Physical ERD](#physical-erd)
- [Database Schema](#database-schema)
- [Application program ](#application-program)
- [meaningful reports](#meaningful-reports)
- [simple GUI](#GUI)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#Installation)
- [Usage](#Usage)


## Project Description
The University Library Management System supports the following functionalities:
- Signing up new users (students, admins)
- Updating user details
- Adding new books to the library (by admin)
- Updating book details (by admin)
- Browsing books (by admin and students)
- Borrowing and returning books
-Showing a list of books that satisfy certain criteria (e.g., ISBN, Publication year, author…)
## Conceptual ERD
the conceptual Entity-Relationship Diagram (ERD), illustrating the relationships between different entities in the system

## Physical ERD
The physical ERD translates the conceptual ERD into a format suitable for implementation in a database. It includes primary keys, foreign keys, and detailed relationships. 

## Database Schema
The database schema in Microsoft SQL Server is defined as follows:
- **Admin Table**
  - Admin_ID, FName, LName, Username, Password, Email, Address
- **Student Table**
  - Student_ID, FName, LName, Username, Password, Email, Address, PhoneNumber
- **Author Table**
  - Author_ID, Name, Biography
- **Book Table**
  - Book_ID, Book_Title, Book_Price, ISBN, Author_ID (FK), Publication_Year
- **Order Table**
  - Order_ID, Borrow_Date, Return_Date, Student_ID (FK)
## application program 
- Insert new records into multiple tables
- Delete records with specific conditions
- Update existing data in various tables
- Retrieve data from individual tables
- Join data across multiple tables for complex queries
## meaningful-reports  

## GUI

## Features
- Sign up and manage user accounts
- Add and update book information
- Borrow and return books
- Browse books with various criteria (e.g., ISBN, Publication year)
- Simple GUI application for user interaction

## Requirements
- Microsoft SQL Server for database
- C# (or other permitted languages) for application development

## Installation
1. Clone this repository to your local machine.
2. Set up the Microsoft SQL Server database using the provided SQL scripts.
3. Populate the database with sample data (optional).
4. Build the C# application to interact with the database.

## Usage
- Run the application to sign up users, add books, borrow and return books.
- Use the SQL scripts to insert, update, and delete data in the database.

