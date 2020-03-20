from flask import Flask, render_template, request
from ltlf2dfa.Translator import Translator
import subprocess
import os
import datetime
import uuid
import base64
import json

app = Flask(__name__)


def encode_svg(file):
    with open(file, "r") as image_file:
        encoded_string = base64.b64encode(image_file.read().encode("utf-8"))
    return encoded_string


@app.route('/')
def index():
    return render_template("index.html")


# @app.route('/dfa/<string:formula>/<string:flag>', methods=['GET', 'POST'])
# def dfa(formula, flag):
#     if request.method == 'POST':
#         # formula = request.args.get('formula')
#         # flag = request.args.get('flag')
#         declare_assumption = False
#         if flag == "true":
#             declare_assumption = True
#         if formula:
#             try:
#                 ## TRANSLATOR ##
#                 translator = Translator(formula)
#                 translator.formula_parser()
#                 translator.translate()
#                 translator.createMonafile(declare_assumption)
#                 result = translator.invoke_mona()
#
#                 #dot_handler = DotHandler()
#                 #dot_handler.modify_dot()
#
#                 automa_name = str(datetime.datetime.now()).replace(" ", "_") + "_" + str(uuid.uuid4())
#
#                 #dot_handler.output_dot('/var/www/ltlf2dfa_web/static/dot/'+automa_name+'.dot')
#                 with open("/var/www/ltlf2dfa_web/static/dot/" + automa_name + ".dot", 'w') as fout:
#                     fout.write(translator.output2dot(result))
#
#                 subprocess.call('dot -Tsvg /var/www/ltlf2dfa_web/static/dot/'+ automa_name +'.dot -o /var/www/ltlf2dfa_web/static/tmp/'+automa_name+'.svg', shell=True)
#
#                 # automa_name = "declare-img1"
#
#                 encoding = encode_svg('/var/www/ltlf2dfa_web/static/tmp/{}.svg'.format(automa_name)).decode("utf-8")
#                 data = {'code': "SUCCESS", 'formula': formula, 'flag': declare_assumption, 'svg': encoding}
#                 json_data = json.dumps(data)
#
#                 os.unlink('/var/www/ltlf2dfa_web/static/dot/'+automa_name+'.dot')
#                 os.unlink('/var/www/ltlf2dfa_web/static/tmp/{}.svg'.format(automa_name))
#
#                 return json_data
#
#                 # return render_template('result.html', automa_name=automa_name, formula=params['formula'], encoding=encoding, flag=declare_assumption)
#
#             except Exception as e:
#                 data = {'code': "FAIL", 'formula': formula, 'flag': declare_assumption, 'error': str(e)}
#                 return json.dumps(data)
#                 # return str(e)
#         else:
#             return render_template("index.html")
#     else:
#         return render_template("index.html")


if __name__== "__main__":
    app.run()
