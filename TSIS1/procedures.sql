
-- adds a new phone number to an existing contact
-- raises an error if the contact name is not found
create or replace procedure add_phone(
    p_contact_name varchar,
    p_phone        varchar,
    p_type         varchar
)
language plpgsql as $$
declare
    v_contact_id integer;
begin
    -- find the contact id by name
    select id into v_contact_id
    from contacts
    where first_name = p_contact_name
    limit 1;

    -- if nothing was found, id will be null
    if v_contact_id is null then
        raise exception 'contact "%" not found', p_contact_name;
    end if;

    insert into phones (contact_id, phone, type)
    values (v_contact_id, p_phone, p_type);
end;
$$;


-- moves a contact to a group, creates the group if it does not exist
create or replace procedure move_to_group(
    p_contact_name varchar,
    p_group_name   varchar
)
language plpgsql as $$
declare
    v_group_id integer;
begin
    -- try to find the group
    select id into v_group_id
    from groups
    where name = p_group_name
    limit 1;

    -- group not found: create it and get the new id with RETURNING
    if v_group_id is null then
        insert into groups (name)
        values (p_group_name)
        returning id into v_group_id;
    end if;

    update contacts
    set group_id = v_group_id
    where first_name = p_contact_name;

    -- FOUND is true if the update matched at least one row
    if not found then
        raise notice 'no contact named "%" was found', p_contact_name;
    end if;
end;
$$;


-- searches contacts by name, email, or any phone number
-- left join means contacts with no group or no phone still appear in results
create or replace function search_contacts(p_query varchar)
returns table(
    id         integer,
    first_name varchar,
    email      varchar,
    birthday   date,
    group_name varchar,
    phone      varchar,
    phone_type varchar
)
language plpgsql as $$
begin
    return query
    select
        c.id,
        c.first_name,
        c.email,
        c.birthday,
        g.name   as group_name,
        p.phone,
        p.type   as phone_type
    from contacts c
    left join groups g on g.id = c.group_id
    left join phones p on p.contact_id = c.id
    where
        c.first_name ilike '%' || p_query || '%'
        or c.email   ilike '%' || p_query || '%'
        or p.phone   ilike '%' || p_query || '%'
    order by c.first_name;
end;
$$;
