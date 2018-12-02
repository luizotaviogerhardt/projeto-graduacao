import difflib
import sys
import re
import helper
import os
import subprocess

#from flask import Flask

#app = Flask(__name__)

input_filename  = 'in'
output_filename = 'out'
input_ext   = '.in'
output_ext  = '.out'
input_folder_name = 'in/'
output_folder_name = 'out/'


def diff(file):

    lines = []
    oficial_output_filename = helper.formatOficialExt(file)
    oficial_output_folder   = helper.formatOficialFolder(output_folder_name)

    with open(oficial_output_folder + oficial_output_filename, 'r') as oout:
        with open(output_folder_name + file, 'r') as out:
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


def evaluate(quant):

    wrong = 0

    for i in range(quant):
        file = output_filename+str(i+1)+output_ext
        if diff(file):
            wrong+=1

    return round((1 - wrong/quant)*100,2)

def execPython3(cmd):
    # usar python3 -c se for passar o codigo via string
    p = subprocess.Popen('python3 '+cmd, stdout=subprocess.PIPE, shell=True)
    return (str(p.communicate()[0]).replace('b','').replace('\'' , '').replace('\\n' , '\n'))

def generateOutputs(quant,code,lang='Python3'):
    if lang == 'Python3':
        for i in range(quant):
            file = output_filename+str(i+1)+output_ext
            results = execPython3(code +'< '+ input_folder_name+input_filename+str(i+1)+input_ext)

            with open('out/'+file, 'w') as out:
                out.write(results)

#@app.route('/', methods=['GET'])
def hello():
    return "Hello World!"

if __name__ == "__main__":
    program_filename = 'hi.py' # se usar arquivo melhor subir no s3 ou algo do tipo
    #code = "print\(2\)" # codigo que sera enviado pelo khoeus a ser decriptografado e formatado (escape de caracteres)
    #print(evaluate(3))
    generateOutputs(3,program_filename,'Python3')

