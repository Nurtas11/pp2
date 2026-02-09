def kbtu_grades(*grades):  #creating a function
    attestation = 0
    for scores in grades:
        attestation = attestation + scores
    how_much_i_need_on_final = 70-attestation
    return how_much_i_need_on_final  #returning a value
print(kbtu_grades(30, 15 ))