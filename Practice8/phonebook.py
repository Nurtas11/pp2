import csv
from connect import connect

# create table if it doesn't exist yet
def create_table():
    sql = """
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL
        )
    """
    # get connection and setup cursor
    conn = connect()
    cur = conn.cursor()
    # run the sql and save changes
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

# read csv and push to db
def insert_from_csv(filename='contacts.csv'):
    sql = "INSERT INTO phonebook (first_name, phone) VALUES (%s, %s)"
    conn = connect()
    cur = conn.cursor()
    # open file and read row by row
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # execute for every contact in csv
            cur.execute(sql, (row['first_name'], row['phone']))
    conn.commit()
    cur.close()
    conn.close()

# get input from user and save
def insert_from_console():
    first_name = input("Enter first name: ")
    phone = input("Enter phone: ")
    sql = "INSERT INTO phonebook (first_name, phone) VALUES (%s, %s)"
    # standard connect and execute
    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (first_name, phone))
    conn.commit()
    cur.close()
    conn.close()
    print(f"added {first_name} to contacts.")

# change phone number for a name
def update_contact():
    name = input("enter the name: ")
    new_phone = input("enter the new phone: ")
    sql = "UPDATE phonebook SET phone = %s WHERE first_name = %s"
    conn = connect()
    cur = conn.cursor()
    # update row and check how many were changed
    cur.execute(sql, (new_phone, name))
    updated = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    # tell user if name was found or not
    if updated > 0:
        print("updated successfully.")
    else:
        print("not found.")

# print all rows sorted by name
def search_all():
    sql = "SELECT * FROM phonebook ORDER BY first_name"
    conn = connect()
    cur = conn.cursor()
    # fetch all results into a list
    cur.execute(sql)
    rows = cur.fetchall()
    print(f"{'ID':<5} {'Name':<20} {'Phone':<20}")
    # loop through list and print formatted
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<20} {row[2]:<20}")
    cur.close()
    conn.close()

# find specific name
def search_by_name():
    name = input("enter name: ")
    sql = "SELECT * FROM phonebook WHERE first_name = %s"
    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (name,))
    rows = cur.fetchall()
    # if list is not empty print details
    if rows:
        for row in rows:
            print(f"found: {row[1]} - {row[2]}")
    else:
        print("not found.")
    cur.close()
    conn.close()

# search using start of phone number
def search_by_phone_prefix():
    prefix = input("enter prefix: ")
    # use % for wildcards in phone search
    sql = "SELECT * FROM phonebook WHERE phone LIKE %s"
    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (prefix + '%',))
    rows = cur.fetchall()
    # print all matches
    for row in rows:
        print(f"{row[1]} - {row[2]}")
    cur.close()
    conn.close()

# remove by name
def delete_by_name():
    name = input("enter name: ")
    sql = "DELETE FROM phonebook WHERE first_name = %s"
    conn = connect()
    cur = conn.cursor()
    # execute delete and commit to save
    cur.execute(sql, (name,))
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    print(f"deleted {deleted} rows.")

# use sql function to find part of name or phone
def search_pattern():
    pattern = input("pattern: ")
    conn = connect()
    cur = conn.cursor()
    # calling the stored function from database
    cur.execute("SELECT * FROM get_ptn(%s)", (pattern,))
    rows = cur.fetchall()
    # display matched pattern results
    for row in rows:
        print(f"ID: {row[0]} | Name: {row[1]} | Phone: {row[2]}")
    cur.close()
    conn.close()

# use procedure to add or update if exists
def upsert_contact():
    name = input("name: ")
    phone = input("phone: ")
    conn = connect()
    cur = conn.cursor()
    # CALL is used for procedures in postgres
    cur.execute("CALL upsert_usr(%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()
    print("upsert done.")

# add list of users and check phones
def insert_many_with_validation():
    names = input("names (split by comma): ").split(',')
    phones = input("phones (split by comma): ").split(',')
    conn = connect()
    cur = conn.cursor()
    # pass data to procedure and get errors back
    cur.execute("CALL ins_many(%s, %s, %s)", (names, phones, []))
    errors = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    # if procedure returned bad rows print them
    if errors:
        print(f"bad data ignored: {errors}")
    else:
        print("all data ok.")

# show data in pages
def search_pagination():
    limit = input("how many: ")
    offset = input("skip how many: ")
    conn = connect()
    cur = conn.cursor()
    # calling pagination function with limit/offset
    cur.execute("SELECT * FROM get_pg(%s, %s)", (int(limit), int(offset)))
    rows = cur.fetchall()
    # print the requested page
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]}")
    cur.close()
    conn.close()

# remove user by name or phone using procedure
def delete_by_proc():
    val = input("name or phone: ")
    conn = connect()
    cur = conn.cursor()
    # delete via procedure logic
    cur.execute("CALL del_usr(%s)", (val,))
    conn.commit()
    cur.close()
    conn.close()
    print("delete complete.")

# main menu loop
def main():
    create_table()     
    while True:
        # short menu options for fast testing
        print("\n1.csv 2.add 3.update 4.all 5.name 6.prefix 7.del 9.pattern 10.upsert 11.many 12.page 13.delproc 0.exit")
        choice = input("opt: ")
        # check choice and run matching function
        if choice == '1': insert_from_csv()
        elif choice == '2': insert_from_console()
        elif choice == '3': update_contact()
        elif choice == '4': search_all()
        elif choice == '5': search_by_name()
        elif choice == '6': search_by_phone_prefix()
        elif choice == '7': delete_by_name()
        elif choice == '9': search_pattern()
        elif choice == '10': upsert_contact()
        elif choice == '11': insert_many_with_validation()
        elif choice == '12': search_pagination()
        elif choice == '13': delete_by_proc()
        elif choice == '0': break

if __name__ == '__main__':
    main()