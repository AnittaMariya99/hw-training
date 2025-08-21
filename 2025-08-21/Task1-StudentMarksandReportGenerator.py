# Task-1:Student Record System (with user input)

# taking student details
name = input("Enter student name: ")
age = int(input("Enter student age: "))

# marks input (3 subjects)
marks = []
for i in range(3):
    m = float(input("Enter mark for subject " + str(i+1) + ": "))
    marks.append(m)

# store in dictionary
student = {
    "name": name,
    "age": age,
    "marks": marks
}

# check data types
print("Type of name:", type(student["name"]))
print("Type of age:", type(student["age"]))
print("Type of marks:", type(student["marks"]))

# total and average
total = sum(marks)
average = total / len(marks)
print("Total Marks:", total)
print("Average Marks:", average)

# pass/fail check
if average >= 40:
    is_passed = True
    print("Student Passed")
else:
    is_passed = False
    print("Student Failed")

# print marks one by one
print("Individual Marks:")
for m in marks:
    print(m)

# convert list to set
marks_set = set(marks)
print("Marks as Set:", marks_set)

# subjects in tuple
subjects = ("Maths", "Science", "English")
print("Subjects:", subjects)

# remarks = None
remarks = None
print("Remarks type:", type(remarks))

# boolean type
print("is_passed type:", type(is_passed))

# final report
print("---- Student Report ----")
print("Name:", student["name"])
print("Age:", student["age"])
print("Subjects:", subjects)
print("Marks:", student["marks"])
print("Total:", total)
print("Average:", average)
print("Result:", "Passed" if is_passed else "Failed")
print("Remarks:", remarks)