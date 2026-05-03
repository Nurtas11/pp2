import csv
import json
from connect import connect


# create all tables needed for this project
def create_tables():
    conn = connect()
    cur = conn.cursor()

    # groups table stores categories like Family, Work, Friend, Other
    cur.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id   SERIAL PRIMARY KEY,
            name VARCHAR(50) UNIQUE NOT NULL
        )
    """)

    # insert default groups, skip if they already exist
    cur.execute("""
        INSERT INTO groups (name) VALUES ('Family'),('Work'),('Friend'),('Other')
        ON CONFLICT DO NOTHING
    """)

    # contacts table with email, birthday, and group foreign key
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id         SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            email      VARCHAR(100),
            birthday   DATE,
            group_id   INTEGER REFERENCES groups(id)
        )
    """)

    # phones table — one contact can have many phones
    # ON DELETE CASCADE removes phones automatically when contact is deleted
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phones (
            id         SERIAL PRIMARY KEY,
            contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
            phone      VARCHAR(20) NOT NULL,
            type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


# helper: finds group id by name, creates the group if it doesn't exist
def get_or_create_group(cur, group_name):
    cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
    return cur.fetchone()[0]


# import contacts from csv file (first_name, email, birthday, group, phone, phone_type)
def insert_from_csv(filename='contacts.csv'):
    conn = connect()
    cur = conn.cursor()

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            group_id = get_or_create_group(cur, row['group'])

            # insert contact and get back the new id with RETURNING
            cur.execute("""
                INSERT INTO contacts (first_name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (row['first_name'], row['email'] or None, row['birthday'] or None, group_id))
            contact_id = cur.fetchone()[0]

            # insert phone linked to this contact
            cur.execute("""
                INSERT INTO phones (contact_id, phone, type)
                VALUES (%s, %s, %s)
            """, (contact_id, row['phone'], row['phone_type'] or 'mobile'))

    conn.commit()
    cur.close()
    conn.close()
    print("csv imported.")


# show contacts that belong to a chosen group
def filter_by_group():
    conn = connect()
    cur = conn.cursor()

    # show available groups first
    cur.execute("SELECT name FROM groups ORDER BY name")
    groups = [row[0] for row in cur.fetchall()]
    print("groups:", ', '.join(groups))

    group_name = input("enter group: ").strip()

    cur.execute("""
        SELECT c.id, c.first_name, c.email, c.birthday, p.phone, p.type
        FROM contacts c
        JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE g.name = %s
        ORDER BY c.first_name
    """, (group_name,))

    rows = cur.fetchall()
    if not rows:
        print("no contacts found.")
    else:
        print(f"\n{'ID':<5} {'Name':<20} {'Email':<25} {'Birthday':<12} {'Phone':<18} {'Type'}")
        for row in rows:
            birthday = str(row[3]) if row[3] else 'N/A'
            print(f"{row[0]:<5} {row[1]:<20} {str(row[2] or ''):<25} {birthday:<12} {str(row[4] or ''):<18} {str(row[5] or '')}")

    cur.close()
    conn.close()


# search contacts by partial email match
def search_by_email():
    query = input("enter email or part of it: ").strip()
    conn = connect()
    cur = conn.cursor()

    # ilike makes it case-insensitive, % on both sides matches anywhere in the string
    cur.execute("""
        SELECT id, first_name, email FROM contacts
        WHERE email ILIKE %s
        ORDER BY first_name
    """, (f'%{query}%',))

    rows = cur.fetchall()
    if not rows:
        print("not found.")
    else:
        for row in rows:
            print(f"{row[0]} | {row[1]} | {row[2]}")

    cur.close()
    conn.close()


# show all contacts sorted by chosen field
def sort_contacts():
    print("sort by: 1.name  2.birthday  3.date added")
    choice = input("choice: ").strip()

    # whitelist to avoid putting raw user input directly into sql
    sort_map = {'1': 'c.first_name', '2': 'c.birthday', '3': 'c.id'}
    order_col = sort_map.get(choice, 'c.first_name')

    conn = connect()
    cur = conn.cursor()

    # f-string is safe here because order_col only comes from our whitelist above
    cur.execute(f"""
        SELECT c.id, c.first_name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        ORDER BY {order_col} NULLS LAST
    """)

    rows = cur.fetchall()
    print(f"\n{'ID':<5} {'Name':<20} {'Email':<25} {'Birthday':<12} {'Group'}")
    for row in rows:
        birthday = str(row[3]) if row[3] else 'N/A'
        print(f"{row[0]:<5} {row[1]:<20} {str(row[2] or ''):<25} {birthday:<12} {str(row[4] or '')}")

    cur.close()
    conn.close()


# browse contacts page by page using the get_pg function from the database
def paginated_browse():
    page_size = 3
    offset = 0

    conn = connect()
    cur = conn.cursor()

    while True:
        cur.execute("SELECT * FROM get_pg(%s, %s)", (page_size, offset))
        rows = cur.fetchall()

        if not rows:
            print("no more contacts.")
            offset = max(0, offset - page_size)
            continue

        print(f"\n--- showing {offset + 1} to {offset + len(rows)} ---")
        for row in rows:
            print(f"{row[0]} | {row[1]} | {row[2]}")

        cmd = input("[n]ext  [p]rev  [q]uit: ").strip().lower()
        if cmd == 'n':
            offset += page_size
        elif cmd == 'p':
            offset = max(0, offset - page_size)
        elif cmd == 'q':
            break

    cur.close()
    conn.close()


# export all contacts with phones and group to a json file
def export_to_json(filename='contacts_export.json'):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.first_name, c.email, c.birthday, g.name
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        ORDER BY c.id
    """)
    contacts = cur.fetchall()

    result = []
    for contact in contacts:
        cid, fname, email, birthday, group = contact

        # get all phones for this contact
        cur.execute("SELECT phone, type FROM phones WHERE contact_id = %s", (cid,))
        phones = cur.fetchall()

        result.append({
            "id":         cid,
            "first_name": fname,
            "email":      email,
            "birthday":   str(birthday) if birthday else None,
            "group":      group,
            "phones":     [{"phone": p[0], "type": p[1]} for p in phones]
        })

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    cur.close()
    conn.close()
    print(f"exported {len(result)} contacts to {filename}.")


# import contacts from a json file, ask user what to do on duplicates
def import_from_json(filename='contacts_export.json'):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = connect()
    cur = conn.cursor()

    for item in data:
        fname = item['first_name']

        # check if contact already exists
        cur.execute("SELECT id FROM contacts WHERE first_name = %s", (fname,))
        existing = cur.fetchone()

        if existing:
            choice = input(f'"{fname}" already exists. [s]kip or [o]verwrite? ').strip().lower()
            if choice != 'o':
                print(f"skipped {fname}.")
                continue

            # overwrite: update fields and replace phones
            group_id = get_or_create_group(cur, item['group']) if item.get('group') else None
            cur.execute("""
                UPDATE contacts SET email = %s, birthday = %s, group_id = %s
                WHERE first_name = %s
            """, (item.get('email'), item.get('birthday'), group_id, fname))
            contact_id = existing[0]
            cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
        else:
            # new contact
            group_id = get_or_create_group(cur, item['group']) if item.get('group') else None
            cur.execute("""
                INSERT INTO contacts (first_name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (fname, item.get('email'), item.get('birthday'), group_id))
            contact_id = cur.fetchone()[0]
            print(f"inserted {fname}.")

        for phone_entry in item.get('phones', []):
            cur.execute("""
                INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)
            """, (contact_id, phone_entry['phone'], phone_entry.get('type', 'mobile')))

    conn.commit()
    cur.close()
    conn.close()
    print("import done.")


# call add_phone procedure to add a phone number to an existing contact
def add_phone():
    name  = input("contact name: ").strip()
    phone = input("phone number: ").strip()
    ptype = input("type (home/work/mobile): ").strip()

    conn = connect()
    cur = conn.cursor()
    try:
        cur.execute("CALL add_phone(%s::varchar, %s::varchar, %s::varchar)", (name, phone, ptype))
        conn.commit()
        print("phone added.")
    except Exception as e:
        conn.rollback()
        print(f"error: {e}")
    finally:
        cur.close()
        conn.close()


# call move_to_group procedure to move a contact into a group
def move_to_group():
    name  = input("contact name: ").strip()
    group = input("group name: ").strip()

    conn = connect()
    cur = conn.cursor()
    try:
        cur.execute("CALL move_to_group(%s::varchar, %s::varchar)", (name, group))
        conn.commit()
        print("contact moved.")
    except Exception as e:
        conn.rollback()
        print(f"error: {e}")
    finally:
        cur.close()
        conn.close()


# call search_contacts function to search across name, email and all phones
def search_contacts():
    query = input("search: ").strip()
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s::varchar)", (query,))
    rows = cur.fetchall()

    if not rows:
        print("no results.")
    else:
        print(f"\n{'ID':<5} {'Name':<20} {'Email':<25} {'Birthday':<12} {'Group':<12} {'Phone':<18} {'Type'}")
        for row in rows:
            birthday = str(row[3]) if row[3] else 'N/A'
            print(f"{row[0]:<5} {row[1]:<20} {str(row[2] or ''):<25} {birthday:<12} {str(row[4] or ''):<12} {str(row[5] or ''):<18} {str(row[6] or '')}")

    cur.close()
    conn.close()


def main():
    create_tables()

    while True:
        print("\n1.import csv  2.filter by group  3.search by email  4.sort  5.browse pages")
        print("6.export json  7.import json  8.add phone  9.move to group  10.search  0.exit")
        choice = input("option: ").strip()

        if   choice == '1':  insert_from_csv()
        elif choice == '2':  filter_by_group()
        elif choice == '3':  search_by_email()
        elif choice == '4':  sort_contacts()
        elif choice == '5':  paginated_browse()
        elif choice == '6':  export_to_json()
        elif choice == '7':  import_from_json()
        elif choice == '8':  add_phone()
        elif choice == '9':  move_to_group()
        elif choice == '10': search_contacts()
        elif choice == '0':  break
        else:                print("invalid option.")


if __name__ == '__main__':
    main()
