import re

# 1. 'a' followed by zero or more 'b's
tests = ["ac", "ab", "abbb", "a", "bc"]
for s in tests:
    print(s, 'match' if re.match(r'ab*', s) else 'no match')

print()

# 2. 
tests = ["ab", "abb", "abbb", "abbbb", "a"]
for s in tests:
    print(s, 'match' if re.match(r'ab{2,3}', s) else 'no match')

print()

#3
tests = ["hello_world", "Hello_World", "qw_qw_qw", "test", "a_b"]
for s in tests:
    print(s, re.findall(r'[a-z]+_[a-z]+', s))

print()

# 4one uppercase letter followed by lowercase letters
tests = ["Hello", "hEllo", "HELLO", "Hi"]
for s in tests:
    print(s, re.findall(r'[A-Z][a-z]*', s))

print()

#  'a' followed by anything, ending in 'b'
tests = ["aab", "axyzb", "ab", "a123b", "abc"]
for s in tests:
    print(s, 'match' if re.match(r'a.*b', s) else 'no match')

print()

# 6replace space, comma or dot with colon
text = "one two,three.four"
print(re.sub(r"[ ,.]", ":", text))

print()

# 7snake case to camel case
def snake_to_camel(s):
    return re.sub(r"_([a-z])", lambda m: m.group(1).upper(), s)

for s in ["hello_world", "some_variable", "convert_this"]:
    print(s, snake_to_camel(s))

print()

#8spplit string at uppercase letters
for s in ["HelloWorld", "qwqwQQQQ", "YOooo"]:
    parts = [p for p in re.split(r"([A-Z][a-z]*)", s) if p]
    print(s, parts)

print()

#9innsert spaces before capital letters
for s in ["HelloWorld", "IamNurtas", "sOmetHing"]:
    print(s, re.sub(r"([A-Z])", r" \1", s).strip())

print()

#10camel case to snake case
def camel_to_snake(s):
    return re.sub(r"([A-Z])", lambda m: "_" + m.group(1).lower(), s).lstrip("_")

for s in ["helloWorld", "qqQq", "IamNurtas"]:
    print(s, camel_to_snake(s))
