

import sqlite3



"""
    
    Table1 : student_information
    Table2 : course
    Table3 : student_course


"""


con = sqlite3.connect("my_testTwo.db")
c = con.cursor()




def createStudentInfos():
    #student_information
    c.execute("""CREATE TABLE student_information
                    (name text,
                    pass int,
                    current_budget int)""")
# createStudentInfos()

def createCourseTable():
    #course
    c.execute("""CREATE TABLE course
                    (course_name text,
                    course_credit int,
                    registered_user name)""")
# createCourseTable()

def createStudentTakenCourses():
    #student_course
    c.execute("""CREATE TABLE student_course
                    (name text,
                    registered_course text)""")
# createStudentTakenCourses()



def studentCanTakeCourses(student_object):
    """
        Gui'de student'in alabileceği course'leri gösterirken bu fonksiyonu kullanacağız.
    """
    c.execute("""SELECT course.course_name FROM course WHERE registered_user IS NOT=?""",(student_object.name,))
    available_courses = [courses for courses in c.fetchall()]
    return available_courses






class User:
    def __init__(self,
                    name,
                    password,
                    budget,
                    connection=None,
                    cursor=None,
                    fromDatabase=True):
        """
            connection = sqlite3.connect("database.db")
            cursor = connection.cursor()
        """
        self.name = name
        self.password = password
        self.budget = budget
        self.registered_lessons = []
        self.con = connection
        self.c = cursor
        self.fromDatabase = fromDatabase
        """
            if its not from database Most probably Object will be created like that:
                User(username,password,budget,connection,cursor,fromDatabase=False)
            
            In that case user will added to automatically Database.
        """
        if self.con is not None and self.c is not None and not self.fromDatabase:
            self.addUsertoDatabase()
    
    def dropSpecificLesson(self,course_object,eventfromUser=True):
        if course_obj in self.registered_lessons:
            self.c.execute("""DELETE FROM student_course WHERE name=? AND 
                                            registered_course=?""",(self.name,course_object.name,))
            self.con.commit()
            self.updateBudget(course_object.paymentBill(),negatively=False)
            if eventfromUser:
                course_object.removeStudent(self,eventfromCourse=False)
            self.registered_lessons.remove(course_object)
        else:
            print("There is not lesson like that.")


    def addUsertoDatabase(self):
        """
            When user created automatically add it to database. if Connection available.
        """
        self.c.execute("""INSERT INTO student_information VALUES (?,?,?)""",(self.name,self.password,self.budget,))
        self.con.commit()
        print("Added to Database Student..")
    
    
    def checkStudentcanTake(self,course_object):
        """
            In this function SQL check is the student allready takes course
            and budget is enough to take.
        """

        if self.budget >= course_object.paymentBill() and self not in course_object.registered_users:
            return True
        return False

    def updateBudget(self,minus,negatively=True):
        if negatively:
            self.budget = self.budget-minus #this is new budget it means student taked the course.
        else:
            self.budget = self.budget+minus
        self.c.execute("""UPDATE student_information SET current_budget =? WHERE name=?""",(self.budget,self.name,))
        self.con.commit()
    
    def takeCourse(self,course_object,eventfromUser=True):
        if self.checkStudentcanTake(course_object):
            self.c.execute("INSERT INTO student_course VALUES (?,?)",(self.name,course_object.name,))
            self.con.commit()
            if eventfromUser:
                course_object.addStudent(self,eventfromCourse=False)
            self.updateBudget(course_object.paymentBill())
            # self.registered_lessons.append(course_object.name)
            self.registered_lessons.append(course_object)
            print("Course Taked Succesfully.")
        else:
            print("Budget is not enough or Allready Taken!")
    def dropAllCourse(self):
        if len(self.registered_lessons) > 0:
            lessons_lists = self.registered_lessons.copy()
            for taking_lessons in lessons_lists:
                self.dropSpecificLesson(taking_lessons)
            del lessons_lists
        else:
            print("Ntohing to drop.")


    def addAdditionalMoney(self,amount):
        pass

    def deleteUser(self):
        pass

    def __repr__(self):
        return self.name

class Course:
    def __init__(self,
                    name,
                    credit,
                    connection,
                    cursor,
                    fromDatabase=True):
        self.name = name 
        self.credit = credit
        self.con = connection
        self.c = cursor
        self.fromDatabase = fromDatabase
        self.registered_users = []
        self.reg_user_text = []

        if self.con is not None and self.c is not None and not self.fromDatabase:
            self.addCoursetoDatabase()
    
    def addCoursetoDatabase(self):
        
        self.c.execute("""INSERT INTO course VALUES (?,?,?) """,(self.name,self.credit,None,))
        self.con.commit()
        print("Added. To Database Course")
    

    def addStudent(self,student_object,eventfromCourse=True):
        if student_object not in self.registered_users:
            self.c.execute("INSERT INTO course VALUES (?,?,?)",(self.name,self.credit,student_object.name,))
            self.con.commit()
            if eventfromCourse:
                student_object.takeCourse(self,eventfromUser=False)
            self.registered_users.append(student_object)
            return True
        return False
    def removeStudent(self,student_object,eventfromCourse=True):
        if student_object in self.registered_users:

            self.c.execute("""DELETE FROM course WHERE course_name=? AND course_credit=? AND 
                                        registered_user=?""",(self.name,self.credit,student_object.name,))
            self.con.commit()
            if eventfromCourse:
                student_object.dropSpecificLesson(self,eventfromUser=False)
            self.registered_users.remove(student_object)
            return True
        return False
    def paymentBill(self):
        return self.credit*100
    
    def deleteCourse(self):
        pass

    def __repr__(self):
        return f'{self.name} Credit : {self.credit}'



def otherLogicalTesting(con,c):
    c.execute("SELECT * FROM course")
    course_objects = {}
    for c_name,credit,reg_user in c.fetchall():
        # print(c_name,credit,reg_user)
        if course_objects.get(c_name) is None:
            obj = Course(c_name,credit,con,c)
            course_objects[c_name] = obj
            if reg_user is not None:
                obj.reg_user_text.append(reg_user)
        else:
            if reg_user is not None:
                course_objects[c_name].reg_user_text.append(reg_user)
    
    c.execute("SELECT * FROM student_information")

    student_object = {}
    for name,password,budget in c.fetchall():
        student_object[name] = User(name,password,budget,con,c)
    
    c.execute("SELECT * FROM student_course")
    
    for std_name , course_name in c.fetchall():
        std_object = student_object.get(std_name)
        course_object = course_objects.get(course_name)
        if std_object.name in course_object.reg_user_text:
            course_object.registered_users.append(std_object)
            std_object.registered_lessons.append(course_object)
    
    return course_objects,student_object





# User("mecit",123,1000,con,c,False) # Defaultly add in to database.
# Course("PHYS103",3,con,c,False) # Defaultly add in to database.


dicts = otherLogicalTesting(con,c) #in the tuple 0.index is all Courses
                                    #            1.index is all Students

print("Returned dicts",dicts)  #({'PHYS103': PHYS103 Credit : 3}, {'mecit': mecit})
print("**************************")
course_obj = dicts[0].get("PHYS103")
std_obj = dicts[1].get("mecit")


# std_obj.takeCourse(course_obj)
# std_obj.dropSpecificLesson(course_obj)
# std_obj.dropAllCourse()

# course_obj.addStudent(std_obj)
# course_obj.removeStudent(std_obj)



# print(std_obj.name ,std_obj.budget , std_obj.registered_lessons , course_obj.registered_users)



def showSTUDENTS(c,key):
    my_dict = {
            0:"student_information",
            1:"course",
            2:"student_course"}
    
    c.execute(f"SELECT * FROM {my_dict[key]}")
    return c.fetchall()
print("------Database info -------")
print("Student Taken Courses : ",showSTUDENTS(c,2))
print("Student Infos : " ,showSTUDENTS(c,0))
print("Courses : " ,showSTUDENTS(c,1))
print("----------------------------")