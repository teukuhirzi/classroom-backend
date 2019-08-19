from flask import Flask, request, json, jsonify
import os

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route('/')
def testConnection():
    return "connected"

@app.route('/register', methods=["POST"])
def register():
    userData = []

    # kalau file users-file.json udah ada, di read dulu. kalau file ga ada, ga usah di read, langsung write
    if os.path.exists('./users-file.json'):
        userFile = open('./users-file.json', 'r')
        userData = json.load(userFile)


    body = request.json
    body["classes_as_student"] = []
    body["classes_as_teacher"] = []

    for user in userData:
        if body["username"] == user["username"]:
            return "Username sudah digunakan"
    for user in userData:
        if body["password"] == "":
            return "Password tidak boleh kosong"
                        
    userData.append(body)

    # siapin file buat di write
    userFile = open('./users-file.json', 'w')
    userFile.write(json.dumps(userData))

    return jsonify(body)

@app.route('/login', methods=["POST"])
def login():
    body = request.json

    # siapin file buat di read
    userFile = open('./users-file.json', 'r')
    userData = json.load(userFile)

    for user in userData:
        if body["username"] == user["username"]:
            if body["password"] == user["password"]:
                return "Login succes, welcome {}".format(user["fullname"])
            else:
                return "Login failed. Wrong password"
    
    return "Login failed. Username is not found"

@app.route('/users/<int:id>', methods=["GET"])
def getUser(id):
    # siapin file buat di read
    userFile = open('./users-file.json', 'r')
    userData = json.load(userFile)

    for user in userData:
        if id == user["userid"]:
            return jsonify(user)

    return "User ID {} is not found".format(id)

@app.route('/users', methods=["GET"])
def getAllUsers():
    # siapin file buat di read
    userFile = open('./users-file.json', 'r')
    userData = json.load(userFile)

    return jsonify(userData)

@app.route('/class', methods=["POST"])
def createClass():
    classesData = []
    
    if os.path.exists('./classes-file.json'):
        classesFile = open('./classes-file.json', 'r')
        classesData = json.load(classesFile)

    body = request.json
    body["students"] = []
    body["classworks"] = []

    for class1 in classesData:
        if body["classid"] == class1["classid"]:
            return "Kelas ini sudah ada gurunya"


    classesData.append(body)

    # siapin file buat di write
    classesFile = open('./classes-file.json', 'w')
    classesFile.write(json.dumps(classesData))

    usersFile = open('./users-file.json', 'r')
    usersData = json.load(usersFile)

    for user in usersData:
        if body["teachers"] == user["userid"]:
            if body["classid"] not in user["classes_as_teacher"]:
                user["classes_as_teacher"].append(body["classid"])
    
    usersFile = open('./users-file.json', 'w')
    usersFile.write(json.dumps(usersData))

    return jsonify(body)

@app.route('/class/<int:id>', methods=["GET"])
def getClass(id):
    # read data di user
    userData = getAllUsers().json
    # siapin file buat di read
    classesFile = open('./classes-file.json', 'r')
    classesData = json.load(classesFile)

    for class_ in classesData:
        if id == class_["classid"]:
            class_["students"] = []
            break
    for user in userData:
        if id in user["classes_as_student"]:
            class_["students"].append(user["fullname"])        

    return jsonify(class_)

    # return "User ID {} is not found".format(id)

@app.route('/classes', methods=["GET"])
def getAllClasses():
    # siapin file buat di read
    classesFile = open('./classes-file.json', 'r')
    classesData = json.load(classesFile)

    return jsonify(classesData)

@app.route('/joinClass', methods=["POST"])
def joinClass():
    body = request.json
 
    # nambahin userid ke classes-file
    classesFile = open('./classes-file.json', 'r')
    classesData = json.load(classesFile)

    for class_ in classesData:
        if body["classid"] == class_["classid"]:
            if body["userid"] not in class_["students"]:
                class_["students"].append(body["userid"])
    
    classesFile = open('./classes-file.json', 'w')
    classesFile.write(json.dumps(classesData))

    # nambahin classes as student ke users-file
    usersFile = open('./users-file.json', 'r')
    usersData = json.load(usersFile)

    for user in usersData:
        if body["userid"] == user["userid"]:
            if body["classid"] not in user["classes_as_student"]:
                user["classes_as_student"].append(body["classid"])
    
    usersFile = open('./users-file.json', 'w')
    usersFile.write(json.dumps(usersData))

    return "success"

@app.route('/updateUser/<int:id>', methods = ["PUT"])
def updateUser(id):
    usersData = getAllUsers().json
    body = request.json

    for user in usersData:
        if id == user["userid"]:
            user["username"] = body["username"]
            user["password"] = body["password"]
            user["email"] = body["email"]
            user["fullname"] = body["fullname"]

    usersFile = open('./users-file.json', 'w')
    usersFile.write(json.dumps(usersData))        

    return jsonify(body)    

@app.route('/classWorks', methods = ["POST"])
def createClassWork():

    classWorksData = []

    if os.path.exists('./classworks-file.json'):
        classWorks = open('./classworks-file.json', 'r')
        classWorksData = json.load(classWorks)

    body = request.json
    body["answers"] = []
    classWorksData.append(body) 
 
    classWorks = open('./classworks-file.json', 'w')
    classWorks.write(json.dumps(classWorksData)) 

    classesFile = open('./classes-file.json', 'r')
    classesData = json.load(classesFile)

    for CW in classesData:
        if body["classid"] == CW["classid"]:
            if body["classworkid"] not in CW["classworks"]:
                CW["classworks"].append(body["classworkid"])


       # siapin file buat di write
    classesFile = open('./classes-file.json', 'w')
    classesFile.write(json.dumps(classesData))


    return "succes"

@app.route('/getClassWorks/<int:cwid>', methods = ["GET"])
def getClassWorks(cwid):
    # siapin file buat di read
    classWorks = open('./classworks-file.json', 'r')
    classWorksData = json.load(classWorks)

    for cw in classWorksData:
        if cwid == cw["classworkid"]:
            return jsonify(cw)

    return "Classwork {} is not found".format(id)

@app.route('/getAllCw')
def getAllCw():
    classWorks = open('./classworks-file.json', 'r')
    classWorksData = json.load(classWorks)

    return jsonify(classWorksData)    

@app.route('/assignCw/<int:cwid>', methods = ["POST"])
def assignCw(cwid):
    body = request.json

    # siapin file buat di read
    classWorks = open('./classworks-file.json', 'r')
    classWorksData = json.load(classWorks)

    for CW in classWorksData:        
        if cwid ==  CW["classworkid"]:
            if body["userid"] not in CW["answers"]:
                CW["answers"].append(body)

    classWorks = open('./classworks-file.json', 'w')
    classWorks.write(json.dumps(classWorksData))

    return "Classwork has been sent"     

@app.route('/updateCw/<int:cwid>', methods = ["PUT"])
def updateCw(cwid):
    classWorks = getAllCw().json
   
    body = request.json

    for CW in classWorks:
        if cwid == CW["classworkid"]:
            CW["Question"] = body["Question"]
            

    classWorksData = open('./classworks-file.json', 'w')
    classWorksData.write(json.dumps(classWorks))        

    return jsonify(body)

@app.route('/outclass/<int:cId>', methods = ["POST"])
def outclass(cId):
    body = request.json

    usersData = getAllUsers().json
    classesData = getAllClasses().json

    for class1 in classesData:
        if cId == class1["classid"]:
            for user in usersData:
                if user["userid"] == body["userid"]:
                    user["classes_as_student"].remove(cId)
                    class1["students"].remove(user["userid"])

    usersFile = open('./users-file.json','w')
    usersFile.write(json.dumps(usersData))

    classesFile = open('./classes-file.json','w')
    classesFile.write(json.dumps(classesData))

    return "Anda telah keluar kelas ini"

@app.route('/hapusKelas/<int:idclass>', methods = ["DELETE"])
def hapusKelas(idclass):
    

    usersData = getAllUsers().json
    classesData = getAllClasses().json
    classWorksData = getAllCw().json

    for class1 in classesData:
        if idclass == class1["classid"]:
            classesData.remove(class1)
    for user in usersData:
        if idclass in user["classes_as_student"]:
            user["classes_as_student"].remove(idclass)
        if idclass in user["classes_as_teacher"]:    
            user["classes_as_teacher"].remove(idclass)
    for cw in classWorksData:
        if idclass == cw["classid"]:
            classWorksData.remove(cw)                       
       

    usersFile = open('./users-file.json','w')
    usersFile.write(json.dumps(usersData))

    classesFile = open('./classes-file.json','w')
    classesFile.write(json.dumps(classesData))
    
    classWorks = open('./classworks-file.json', 'w')
    classWorks.write(json.dumps(classWorksData))

    return "Kelas telah dihapus"  

@app.route('/hapusPr/<int:idpr>', methods = ["DELETE"])
def hapusPr(idpr):


    classesData = getAllClasses().json
    classWorksData = getAllCw().json

    for cw in classWorksData:
        if idpr == cw["classworkid"]:
            classWorksData.remove(cw)
    for class1 in classesData:
        if idpr in class1["classworks"]:
            class1["classworks"].remove(idpr)
            
    
    classesFile = open('./classes-file.json','w')
    classesFile.write(json.dumps(classesData))
    
    classWorks = open('./classworks-file.json', 'w')
    classWorks.write(json.dumps(classWorksData))

    return "Tugas telah dihapus"         





