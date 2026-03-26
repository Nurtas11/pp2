import csv
from connect import connect

#create table
def create_table():
    
    sql = """
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY, -- a column called id that automatically counts up  for each new row.
            first_name VARCHAR(100) NOT NULL, -- text column that holds up to 100 characters
            phone VARCHAR(20) NOT NULL -- text column that holds up to 20 characters
        )
    """
    # opening a connection to the database
    conn = connect()
    cur = conn.cursor()         # cursor lets us send SQL commands
    cur.execute(sql)            # send the CREATE TABLE command
    conn.commit()               # save the changes
    cur.close()                 # close cursor
    conn.close()                # close connection


#INSERT FROM CSVFILe

def insert_from_csv(filename='contacts.csv'):
    sql = "INSERT INTO phonebook (first_name, phone) VALUES (%s, %s)"

    conn = connect()
    cur = conn.cursor()

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)      # reads CSV as a dictionary using headers
        for row in reader:
            # row['first_name'] and row['phone'] come from the CSV columns
            cur.execute(sql, (row['first_name'], row['phone']))

    conn.commit()
    cur.close()
    conn.close()

# 3. inserting from console

def insert_from_console():
    first_name = input("Enter first name: ")
    phone = input("Enter phone number: ")

    sql = "INSERT INTO phonebook (first_name, phone) VALUES (%s, %s)"

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (first_name, phone))   
    conn.commit()
    cur.close()
    conn.close()
    print(f"Contact '{first_name}' added successfully.")
# updating 
#update a contact's first name or phone number by their ID
def update_contact():
    
    
    search_all() #shows all ids

    contact_id = input("\nenter the id")
    print("what to update?")
    print("1 - First name")
    print("2 - Phone number")
    choice = input()

    conn = connect()
    cur = conn.cursor()

    if choice == '1':
        new_name = input("fisrt name ")
        sql = "UPDATE phonebook SET first_name = %s WHERE id = %s"
        cur.execute(sql, (new_name, contact_id))
        print("First name updated.")
    elif choice == '2':
        new_phone = input("new phone ")
        sql = "UPDATE phonebook SET phone = %s WHERE id = %s"
        cur.execute(sql, (new_phone, contact_id))
        print("phone number updated")
    else:
        print("input is wrong")

    conn.commit()
    cur.close()
    conn.close()



# search query

def search_all():
    
    sql = "SELECT * FROM phonebook ORDER BY id"

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()  #fetchall() gets ALL the results as a list

    print("\n── All Contacts ──────────────────")
    print(f"{'ID':<5} {'Name':<20} {'Phone':<20}")
    print("-" * 45)
    for row in rows:
        # row[0] = id, row[1] = first_name, row[2] = phone
        print(f"{row[0]:<5} {row[1]:<20} {row[2]:<20}")
    print()

    cur.close()
    conn.close()


def search_by_name(): #search by mame
    
    name = input("enter name")

    sql = "SELECT * FROM phonebook WHERE first_name = %s"

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (name,))     
    rows = cur.fetchall()

    print(f"\n── Results for '{name}' ──────────")
    print(f"{'ID':<5} {'Name':<20} {'Phone':<20}")
    print("-" * 45)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<20} {row[2]:<20}")
    print()

    cur.close()
    conn.close()


def search_by_phone_prefix():
    prefix = input()

    #LEFT takes the first 4 characters of phone
    sql = "SELECT * FROM phonebook WHERE LEFT(phone, %s) = %s"

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (len(prefix), prefix))  
    rows = cur.fetchall()

    print(f"\n── Results for prefix '{prefix}' ──")
    print(f"{'ID':<5} {'Name':<20} {'Phone':<20}")
    print("-" * 45)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<20} {row[2]:<20}")
    print()

    cur.close()
    conn.close()
# deleting
def delete_by_name():
   
    name = input()

    sql = "DELETE FROM phonebook WHERE first_name = %s"

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (name,))
    deleted = cur.rowcount      # tells how many were deleted
    conn.commit()
    cur.close()
    conn.close()

    print(f"deleted {deleted} contacts with name '{name}'.")

#design(menu)
def main():
    create_table()     

    while True:
        print("══════════════════════════════")
        print("       PHONEBOOK MENU         ")
        print("══════════════════════════════")
        print("1. Import contacts from CSV")
        print("2. Add contact manually")
        print("3. Update a contact")
        print("4. Show all contacts")
        print("5. Search by name")
        print("6. Search by phone prefix")
        print("7. Delete by name")
        print("8. Delete by phone")
        print("0. Exit")
        print("──────────────────────────────")

        choice = input("Choose an option: ")

        if choice == '1':
            insert_from_csv()
        elif choice == '2':
            insert_from_console()
        elif choice == '3':
            update_contact()
        elif choice == '4':
            search_all()
        elif choice == '5':
            search_by_name()
        elif choice == '6':
            search_by_phone_prefix()
        elif choice == '7':
            delete_by_name()
        elif choice == '8':
            delete_by_phone()
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.\n")


if __name__ == '__main__': #runs main() only when this file is executed directly
    main()
