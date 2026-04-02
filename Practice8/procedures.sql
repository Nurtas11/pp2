-- start of the procedure to add or update
-- fn is name, ph is phone number
create or replace procedure upsert_usr(fn varchar, ph varchar)
language plpgsql as $$
begin
    -- check if name already exists in the table
    if exists (select 1 from phonebook where first_name = fn) then
        -- if name is found, we just update the phone
        update phonebook set phone = ph where first_name = fn;
    else
        -- if name is not found, we insert a brand new row
        insert into phonebook (first_name, phone) values (fn, ph);
    end if;
-- end of the logic block
end;
$$;

-- procedure to handle many inserts at once
-- uses arrays for names and phones
create or replace procedure ins_many(
    fn_arr varchar[],
    ph_arr varchar[],
    -- inout lets us send the error list back to python
    inout err_arr varchar[] default '{}'
)
language plpgsql as $$
declare
    -- variables to keep track of loop size and index
    sz integer;
    i integer;
begin
    -- find out how many items are in the name array
    sz := array_length(fn_arr, 1);
    
    -- loop from 1 up to the total number of items
    for i in 1..sz loop
        -- validation check: phone must be 10+ digits and only numbers/symbols
        if length(ph_arr[i]) >= 10 and ph_arr[i] ~ '^[0-9\+\-\(\)]+$' then
            -- if phone is valid, insert into the table
            insert into phonebook (first_name, phone) values (fn_arr[i], ph_arr[i]);
        else
            -- if phone is bad, add the name and phone to the error array
            err_arr := array_append(err_arr, fn_arr[i] || ':' || ph_arr[i]);
        end if;
    end loop;
-- end of the loop and procedure
end;
$$;

-- procedure to delete a record
-- takes one value that could be a name or a phone
create or replace procedure del_usr(val varchar)
language plpgsql as $$
begin
    -- delete if the input matches either column
    delete from phonebook
    where first_name = val or phone = val;
-- finish deletion
end;
$$;