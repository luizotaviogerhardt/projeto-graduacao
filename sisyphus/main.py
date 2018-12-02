import difflib
import sys
import re
import helper
import os
import subprocess
import json

from flask import Flask
from flask import request

app = Flask(__name__)

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

    print bool(lines)
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
    # usar python3 -c se for passar o codigo via string
    p = subprocess.Popen('python3 '+cmd, stdout=subprocess.PIPE, shell=True)
    return (str(p.communicate()[0]).replace('b','').replace('\'' , '').replace('\\n' , '\n'))

def generateOutputs(quant, directory, program, lang='Python3'):
    if lang == 'Python3':
        for i in range(quant):
            file = output_filename+str(i+1)+output_ext
            results = execPython3(program +' < '+ directory+'/'+input_folder_name+input_filename+str(i+1)+input_ext)


            with open(directory+'/'+'out/'+file, 'w') as out:
                out.write(results.rstrip())

@app.route('/test', methods=['GET'])
def hello():
    return "Hello World!"

@app.route('/evaluate', methods=['POST'])
def grade():

    data = json.loads(request.data)

    filename = data['filename']
    code = data['code']
    lang = data['language']
    inputs = data['inputs']
    o_outs = data['o_outs']

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

if __name__ == "__main__":
    app.run()

