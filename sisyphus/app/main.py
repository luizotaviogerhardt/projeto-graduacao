import difflib
import sys
import re
import helper
import os
import subprocess
import json
import time
import flask
import sqlite3
import shutil

from flask import Flask
from flask import request
from flask import Response

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

input_filename  = 'in'
output_filename = 'out'
input_ext   = '.in'
output_ext  = '.out'
input_folder_name = 'in/'
output_folder_name = 'out/'


def diff(directory, file):

    lines = []
    oficial_output_filename = helper.formatOficialExt(file)
    oficial_output_folder   = directory+'/'+helper.formatOficialFolder(output_folder_name)

    with open(oficial_output_folder + oficial_output_filename, 'r') as oout:
        with open(directory+'/'+output_folder_name + file, 'r') as out:
            diff = difflib.unified_diff(
                oout.readlines(),
                out.readlines(),
                fromfile='oout',
                tofile='out',
            )

    if diff:
        for line in diff:
            if re.match("(\-|\+)\w+", line): # Searchs for any + or - followed by an alphanumeric expression
                lines.append(line)

    return lines


def evaluate(directory, quant):

    wrong = 0

    for i in range(quant):
        file = output_filename+str(i+1)+output_ext
        if diff(directory, file):
            wrong+=1

    frac = float(wrong)/float(quant)
    return round((1 - frac)*100,2)

def execPython3(cmd):
    try:
        print 'python3 '+cmd
        check = subprocess.check_output('python3 '+cmd, stderr=subprocess.STDOUT, shell=True)
        print check
        p = subprocess.Popen('python3 '+cmd, stdout=subprocess.PIPE, shell=True)
        return (str(p.communicate()[0]).replace('\'' , '').replace('\\n' , '\n'))
    except subprocess.CalledProcessError as e:
        err = str(e.output).replace('File "tmp.py",', "Error at ")
        print err
        return err;


def execPython(cmd):
    p = subprocess.Popen('python '+cmd, stdout=subprocess.PIPE, shell=True)
    return (str(p.communicate()[0]).replace('\'' , '').replace('\\n' , '\n'))

def execC(cmd):
    p = subprocess.Popen('gcc '+cmd, stdout=subprocess.PIPE, shell=True)
    while not p:
        time.sleep(1)
    time.sleep(1)
    p = subprocess.Popen('./a.out '+cmd, stdout=subprocess.PIPE, shell=True)
    while not p:
        time.sleep(1)
    return (str(p.communicate()[0]).replace('\'' , '').replace('\\n' , '\n'))

def generateOutputs(quant, directory, program, lang='Python3'):
    if lang == 'Python3':
        for i in range(quant):
            file = output_filename+str(i+1)+output_ext
            results = execPython3(program +' < '+ directory+'/'+input_folder_name+input_filename+str(i+1)+input_ext)
            print 'RESULTADO AE '+results           

            with open(directory+'/'+'out/'+file, 'w') as out:
                out.write(results.rstrip())

    elif lang == 'Python':
        for i in range(quant):
            file = output_filename+str(i+1)+output_ext
            results = execPython(program +' < '+ directory+'/'+input_folder_name+input_filename+str(i+1)+input_ext)

            with open(directory+'/'+'out/'+file, 'w') as out:
                out.write(results.rstrip())

    elif lang == 'C':
        for i in range(quant):
            file = output_filename+str(i+1)+output_ext
            results = execC(program +' < '+ directory+'/'+input_folder_name+input_filename+str(i+1)+input_ext)
            print 'RESULTADO AE '+results  

            with open(directory+'/'+'out/'+file, 'w') as out:
                out.write(results.rstrip())

    
        #os.remove('a.out')

@app.route('/test', methods=['GET'])
def hello():
    return json.dumps({'sucess' : "OK"})

@app.route('/evaluate', methods=['POST'])
def grade():

    data = json.loads(request.data)
    print(data)

    filename = data['filename']
    code = data['code']
    lang = data['language']
    inputs = data['inputs']
    o_outs = data['o_outs']

    code = helper.unicodeToAscii(code)
    # inputs = helper.unicodeListToAscii(inputs)
    # o_outs = helper.unicodeListToAscii(o_outs)

    print code
    print inputs
    print o_outs

    foldername = helper.removeExt(filename)
    qtd_inputs = len(inputs)
    qtd_testes = len(o_outs)

    directory = foldername
    if not os.path.exists(directory):
        os.makedirs(directory)
        os.makedirs(directory+'/'+'in')
        os.makedirs(directory+'/'+'oout')
        os.makedirs(directory+'/'+'out')


    i = 1
    for entrada in inputs:
        with open(foldername+'/'+'in/'+'in'+str(i)+'.in', 'w') as input_file:
             input_file.write(entrada.rstrip())
             i+=1

    i = 1
    for o_out in o_outs:
        with open(foldername+'/'+'oout/'+'out'+str(i)+'.oout', 'w') as oout_file:
             oout_file.write(o_out.rstrip())
             i+=1

    with open(foldername+'/'+filename, 'w') as program_file:
        program_file.write(code)


    generateOutputs(qtd_inputs, directory, directory+'/'+filename, lang)
    grade = evaluate(directory, qtd_testes)

    json_response = json.dumps({'grade' : grade})

    print json_response
    return json_response


@app.route('/compile', methods=['POST'])
def submit():

    data = json.loads(request.data)
    print data


    code = data['code']
    lang = data['language']
    entrada = data['input']

    #os.makedirs("tmp")

    with open("tmp.input", 'w') as input_file:
             input_file.write(entrada.rstrip())

    if lang == 'Python3':
        with open("tmp.py", 'w') as program_file:
            program_file.write(code)

        result = execPython3("tmp.py < tmp.input")
        os.remove("tmp.py")

    if lang == 'Python':
        with open("tmp.py", 'w') as program_file:
            program_file.write(code)

        result = execPython("tmp.py < tmp.input")
        os.remove("tmp.py")


    if lang == 'C':
        with open("tmp.c", 'w') as program_file:
            program_file.write(code)

        result = execC("tmp.c < tmp.input")
        os.remove("tmp.c")

    os.remove("tmp.input")

    print result
    return json.dumps({'output' : result})


@app.route('/inouts', methods=['POST'])
def inouts():

    data = json.loads(request.data)
    print data

    identifier = data['id']
    inputs = data['inputs']
    o_outs = data['o_outs']

    if identifier == "new":
        conn = sqlite3.connect('/DbVolume:/db/development.sqlite3')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id 
            FROM board_items
            ORDER BY id DESC
            """)

        ids = cursor.fetchall()
        print ids
        identifier = str(int(ids[0][0])+1)
        


    foldername = "inouts/"+identifier
    if os.path.exists(foldername):
        shutil.rmtree(foldername)

    os.makedirs(foldername)
    os.makedirs(foldername+'/'+'in')
    os.makedirs(foldername+'/'+'oout')
    os.makedirs(foldername+'/'+'out')

    i = 1
    for entrada in inputs:
        with open(foldername+'/'+'in/'+"in"+str(i)+'.in', 'w') as input_file:
             input_file.write(entrada.rstrip())
             i+=1

    i = 1
    for o_out in o_outs:
        with open(foldername+'/'+'oout/'+'out'+str(i)+'.oout', 'w') as oout_file:
             oout_file.write(o_out.rstrip())
             i+=1


    return json.dumps({'status' : "OK"})


@app.route('/autoeval', methods=['POST'])
def autoeval():

    data = json.loads(request.data)
    print data

    user_id = int(data['user_id'])
    identifier = str(data['id'])
    lang = data['language']
    code = data['code']

    id_counter = int(identifier)

    code = helper.unicodeToAscii(code)


    if lang == 'Python3' or lang == 'Python':
        ext = ".py"
    if lang == 'C':
        ext = ".c"

    foldername = "inouts/"+identifier
    filename = identifier+ext
    path, dirs, files = next(os.walk(foldername+'/'+'in/'))
    qty = len(files)


    print(qty)

    with open(foldername+'/'+filename, 'w') as program_file:
        program_file.write(code)


    generateOutputs(qty, foldername, foldername+'/'+filename, lang)
    grade = evaluate(foldername, qty)

    # conn = sqlite3.connect('./../../khoeus-app/db/development.sqlite3')
    # cursor = conn.cursor()

    # # cursor.execute('update submissions set grade = '+str(grade)+  ' where user_id = '+str(user_id) +' AND id = '+str(id_counter)+';')

    # # cursor.execute("""
    # # UPDATE submissions 
    # # SET grade = ?
    # # WHERE id = ? AND user_id = ?
    # # """, (grade, id_counter, user_id))


    # # cursor.execute("""
    # #     SELECT grade 
    # #     FROM submissions
    # #     WHERE id = ? AND user_id = ?
    # #     """, (id_counter, user_id))
    # # # abc = cursor.fetchall()
    # # # print abc

    # conn.commit()

    # conn.close()


    foldername = "grades/"+identifier
    if os.path.exists(foldername):
        shutil.rmtree(foldername)

    os.makedirs(foldername)

    with open(foldername+"/user_"+str(user_id), 'w') as grade_file:
        grade_file.write(str(grade))


    print("vo retornar")

    print grade
    return json.dumps({'grade' : grade})


@app.route('/grade/<id>/<user_id>', methods=['GET'])
def get_grade(id, user_id):



    path = "grades/"+id+"/"+"user_"+user_id
    print path
    
    if not os.path.exists(path):
        return Response("{'error':'User not found'}", status=500, mimetype='application/json')

    with open(path, 'r') as grade_file:
        grade = grade_file.read()

    print grade
    return json.dumps({'grade' : grade})


@app.route('/')
def index():
    return flask.render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0')

