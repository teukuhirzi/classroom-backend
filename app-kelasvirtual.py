from flask import Flask, request, json, jsonify
import os
from src.utils.crypt import encrypt, decrypt

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


def readFile(filePath):
    thisData = []
    # kalau file *.json sudah ada, diread. Kalau file ga ada, return list kosong
    if os.path.exists(filePath) and os.path.getsize(filePath) > 0: # dan kalau isi filenya tidak kosong banget
        thisFile = open(filePath,'r')
        thisData = json.load(thisFile)
        thisFile.close()

    return thisData 

def writeFile(filePath, data):
    thisFile = open(filePath, 'w')
    thisFile.write(json.dumps(data))
    thisFile.close()


   

usersFileLocation = 'src/data/users-file.json'
classesFileLocation = 'src/data/classes-file.json'
classworksLocation = 'src/data/classworks-file.json'

@app.route('/')
def testConnection(): 
    return "connected"

@app.route('/register', methods=["POST"])
def register():
    response = {}

    userData = []

    # kalau file users-file.json udah ada, di read dulu. kalau file ga ada, ga usah di read, langsung write
    if os.path.exists(usersFileLocation):
        userFile = open(usersFileLocation, 'r')
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

    body["password"] = encrypt(body["password"])        
                        
    userData.append(body)

    # siapin file buat di write
    userFile = open(usersFileLocation, 'w')
    userFile.write(json.dumps(userData))

    response["message"] = "Register successful"
    response["data"] = body    
    return jsonify(response)

@app.route('/login', methods=["POST"])
def login():
    response = {}
    response['message'] = "Login failed. Username or password is wrong"
    response['data'] = {}

    body = request.json

    # siapin file buat di read
    userFile = open(usersFileLocation, 'r')
    userData = json.load(userFile)

    for user in userData:
        if body["username"] == user["username"]:
            if body["password"] == decrypt(user["password"]):
                response["message"] = "Login succes, welcome {}".format(user["fullname"])
                response["data"] = user
            break
           
    
    return jsonify(response)

@app.route('/users/<int:id>', methods=["GET"])
def getUser(id):
    response = {}
    response["message"] = "Userid {} is not found".format(id)
    response["data"] = {}
    # siapin file buat di read
    userFile = open(usersFileLocation, 'r')
    userData = json.load(userFile)

    for user in userData:
        if id == user["userid"]:
            response["message"] = "User Found"
            response["data"] = user

    return jsonify(response)

@app.route('/users', methods=["GET"])
def getAllUsers():
    # siapin file buat di read
    userFile = open(usersFileLocation, 'r')
    userData = json.load(userFile)

    return jsonify(userData)

@app.route('/class', methods=["POST"])
def createClass():
    body = request.json
    body["students"] = []
    body["classworks"] = []

    response = {}
    response['message'] = "Create Class Succes"
    response['data'] = {}

    classesData = readFile(classesFileLocation)
    classidAlreadyExist = False
    for class1 in classesData:
        if body["classid"] == class1["classid"]:
            response["message"] = "Class ID {} is already exist".format(body["classid"])
            classidAlreadyExist = True
            break

    if not classidAlreadyExist:
        classesData.append(body)
        writeFile(classesFileLocation, classesData)        
    
    usersData = readFile(usersFileLocation)
    for user in usersData:
        if body["teacher"] == user["userid"]:
            if body["classid"] not in user["classes_as_teacher"]:
                user["classes_as_teacher"].append(body["classid"])
    
    writeFile(usersFileLocation, usersData)

    response["data"] = body

    return jsonify(response)

@app.route('/class/<int:id>', methods=["GET"])
def getClass(id):
    response = {}
    response["message"] = "Class with classid {} is not found".format(id)
    response["data"] = {}
    
    # nyari kealasnya    
    classesData = readFile(classesFileLocation)
    classData = {}
    classFound = False
    for class_ in classesData:
        if id == class_["classid"]:
            classData = class_
            response["message"] = "Get Class Success"
            classFound = True
            break

    if classFound:
        classData["students"] = []
        classData["classworks"] = []

    # nyari muridnya
    userData = readFile(usersFileLocation)            
    for user in userData:
        if id in user["classes_as_student"]:
            classData["students"].append(user["fullname"]) 

    # nyari classworknya
    classWorksData = readFile(classworksLocation)
    for cw in classWorksData:
        if cw["classid"] == id:
            classData["classworks"].append(cw)   

    response["data"] = classData                    

    return jsonify(response)

@app.route('/classes', methods=["GET"])
def getAllClasses():
    # siapin file buat di read
   
    classesData = readFile(classesFileLocation)

    return jsonify(classesData)

@app.route('/joinClass', methods=["POST"])
def joinClass():
    body = request.json
 
    # nambahin userid ke classes-file
    classesFile = open(classesFileLocation, 'r')
    classesData = json.load(classesFile)

    for class_ in classesData:
        if body["classid"] == class_["classid"]:
            if body["userid"] not in class_["students"]:
                class_["students"].append(body["userid"])
    
    classesFile = open(classesFileLocation, 'w')
    classesFile.write(json.dumps(classesData))

    # nambahin classes as student ke users-file
    usersFile = open(usersFileLocation, 'r')
    usersData = json.load(usersFile)

    for user in usersData:
        if body["userid"] == user["userid"]:
            if body["classid"] not in user["classes_as_student"]:
                user["classes_as_student"].append(body["classid"])
    
    usersFile = open(usersFileLocation, 'w')
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

    usersFile = open(usersFileLocation, 'w')
    usersFile.write(json.dumps(usersData))        

    return jsonify(body)    

@app.route('/classWorks', methods = ["POST"])
def createClassWork():

    classWorksData = []

    if os.path.exists(classworksLocation):
        classWorks = open(classworksLocation, 'r')
        classWorksData = json.load(classWorks)

    body = request.json
    body["answers"] = []
    classWorksData.append(body) 
 
    classWorks = open(classworksLocation, 'w')
    classWorks.write(json.dumps(classWorksData)) 

    classesFile = open(classesFileLocation, 'r')
    classesData = json.load(classesFile)

    for CW in classesData:
        if body["classid"] == CW["classid"]:
            if body["classworkid"] not in CW["classworks"]:
                CW["classworks"].append(body["classworkid"])


       # siapin file buat di write
    classesFile = open(classesFileLocation, 'w')
    classesFile.write(json.dumps(classesData))


    return "succes"

@app.route('/getClassWorks/<int:cwid>', methods = ["GET"])
def getClassWorks(cwid):
    # siapin file buat di read
    classWorks = open(classworksLocation, 'r')
    classWorksData = json.load(classWorks)

    for cw in classWorksData:
        if cwid == cw["classworkid"]:
            return jsonify(cw)

    return "Classwork {} is not found".format(id)

@app.route('/getAllCw')
def getAllCw():
    classWorks = open(classworksLocation, 'r')
    classWorksData = json.load(classWorks)

    return jsonify(classWorksData)    

@app.route('/assignCw/<int:cwid>', methods = ["POST"])
def assignCw(cwid):
    body = request.json

    # siapin file buat di read
    classWorks = open(classworksLocation, 'r')
    classWorksData = json.load(classWorks)

    for CW in classWorksData:        
        if cwid ==  CW["classworkid"]:
            if body["userid"] not in CW["answers"]:
                CW["answers"].append(body)

    classWorks = open(classworksLocation, 'w')
    classWorks.write(json.dumps(classWorksData))

    return "Classwork has been sent"     

@app.route('/updateCw/<int:cwid>', methods = ["PUT"])
def updateCw(cwid):
    classWorks = getAllCw().json
   
    body = request.json

    for CW in classWorks:
        if cwid == CW["classworkid"]:
            CW["Question"] = body["Question"]
            

    classWorksData = open(classworksLocation, 'w')
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

    usersFile = open(usersFileLocation,'w')
    usersFile.write(json.dumps(usersData))

    classesFile = open(classesFileLocation,'w')
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
       

    usersFile = open(usersFileLocation,'w')
    usersFile.write(json.dumps(usersData))

    classesFile = open(classesFileLocation,'w')
    classesFile.write(json.dumps(classesData))
    
    classWorks = open(classworksLocation, 'w')
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
            
    
    classesFile = open(classesFileLocation,'w')
    classesFile.write(json.dumps(classesData))
    
    classWorks = open(classworksLocation, 'w')
    classWorks.write(json.dumps(classWorksData))

    return "Tugas telah dihapus"         





