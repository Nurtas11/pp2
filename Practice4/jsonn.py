import json   #imports json library

f = open("sample-data.json") #opens the file
data = json.load(f) #converts a file to a python dictionary
f.close()  #closes the file

print("Interface Status")  #prints interface
print("=" * 72)
print("DN                                            Description          Speed    MTU")
print("-" * 45, "-" * 20, "-" * 7, "-" * 7)

for item in data["imdata"]:  #loops through list
    attrs = item["l1PhysIf"]["attributes"] #enters dictionary and stores "attributes into "attrs"
    print(f"{attrs['dn']:<45} {attrs['descr']:<20} {attrs['speed']:<8} {attrs['mtu']}") # prints the 3 fields from attrs with required space