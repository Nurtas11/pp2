-- start of the search function
-- it takes one string called ptn
create or replace function get_ptn(ptn varchar)
-- it returns a table with 3 columns matching our phonebook
returns table(id integer, fn varchar, ph varchar) as $$
begin
    -- start the actual query
    return query
    -- get id, name and phone from the table
    select p.id, p.first_name, p.phone
    from phonebook p
    -- ilike makes it ignore big or small letters
    -- % on both sides means search anywhere in the string
    where p.first_name ilike '%' || ptn || '%'
       or p.phone ilike '%' || ptn || '%';
-- end of the query logic
end;
$$ language plpgsql;
-- end of function

-- start of the pagination function
-- takes limit (how many) and offset (how many to skip)
create or replace function get_pg(lmt integer, offst integer)
-- returns the same table structure as the other function
returns table(id integer, fn varchar, ph varchar) as $$
begin
    -- start the query for pages
    return query
    -- select everything from phonebook
    select p.id, p.first_name, p.phone
    from phonebook p
    -- order by id so the pages stay in the same order
    order by p.id
    -- limit restricts the number of rows
    -- offset skips the rows we already saw
    limit lmt offset offst;
-- end of the logic
end;
$$ language plpgsql;
-- end of function