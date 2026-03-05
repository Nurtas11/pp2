import re
import json

with open("raw.txt", "r", encoding="utf-8") as f: #tells Python which character encoding to use when reading/writing.
    text = f.read()
lines = text.splitlines()
#turn1 200,00 into 1200.0
def to_float(s):
    return float(s.strip().replace(" ", "").replace(",", ".")) #needed for reading russian format numbers


items = []
for i in range(1, len(lines) - 1): #l oop through every line by index number.
    if " x " in lines[i] and re.search(r"\d,\d\d\d", lines[i]):    #checl if it also contain a digit-comma-3digits pattern
        parts      = lines[i].split(" x ") # looking for the quantity×price line
        qty        = to_float(parts[0]) #converting to float
        unit_price = to_float(parts[1])
        line_total = to_float(lines[i + 1])
        name       = lines[i - 1].strip()
        items.append({ #save all four values as a dictionary and add it to the items list.
            "name":       name,  
            "quantity":   qty,
            "unit_price": unit_price,
            "line_total": line_total
        })

# date and time 
# looping to find dates from lists
date = None
time = None
for line in lines:
    if re.search(r"\d\d\.\d\d\.\d\d\d\d", line):
        date = re.search(r"\d\d\.\d\d\.\d\d\d\d", line).group()
        time = re.search(r"\d\d:\d\d:\d\d", line).group()

# Payment method and grand total 

payment_method = None
payment_amount = None
grand_total    = None

for i in range(len(lines) - 1):   #loop for finding the payments method line
    if "карта" in lines[i].lower() or "наличные" in lines[i].lower():
        payment_method = lines[i].replace(":", "").strip()
        payment_amount = to_float(lines[i + 1])
    if "ИТОГО" in lines[i]: #if it finds the total, it converts to float
        grand_total = to_float(lines[i + 1])

# finding all unique prices 
all_prices = set()
for line in lines:
    for match in re.findall(r"\d[\d ]*,\d\d", line): #start with a digit, then more digits or spaces (for thousands separator), then comma, then exactly 2 digits
        all_prices.add(to_float(match))
all_prices = sorted(all_prices)

#print results 
calculated_total = round(sum(item["line_total"] for item in items), 2) 
# Add up all line_total values from our parsed items


# everything here is  just interface
print("=" * 70)
print("PARSED RECEIPT")
print("=" * 70)
print(f"Date   : {date}  {time}")
print(f"Payment: {payment_method}  {payment_amount} ₸")
print()
print(f"{'#':<4} {'Product':<42} {'Qty':>4} {'Unit ₸':>9} {'Total ₸':>9}")
print("-" * 70)
for i, item in enumerate(items, 1):
    print(f"{i:<4} {item['name'][:41]:<42} {item['quantity']:>4.0f}"
          f" {item['unit_price']:>9.2f} {item['line_total']:>9.2f}")
print("-" * 70)
print(f"{'Calculated total:':>60} {calculated_total:>9.2f}")
print(f"{'Receipt total   :':>60} {grand_total:>9.2f}")
print()
print("All unique prices (₸):", all_prices)

result = {
    "date": date,
    "time": time,
    "payment_method": payment_method,
    "payment_amount": payment_amount,
    "grand_total": grand_total,
    "calculated_total": calculated_total,
    "items": items
}
print()
print("── JSON ──")
print(json.dumps(result, ensure_ascii=False, indent=2))
