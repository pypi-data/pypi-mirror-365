import os, shutil, json
from pathlib import Path
import numpy as np
import shutil


#########
# miscelaneous functions
#########


    
def copyTemplate(templateType, prefix = ''):
    utilsPath = os.path.realpath(__file__)
    examplePath = os.path.join(os.path.dirname(utilsPath),'examples','notebooks')
    jsonPath = os.path.join(os.path.dirname(utilsPath),'examples','json','templates.json')
    workingPath = os.getcwd()
    
    with open(jsonPath, 'r') as file:
        templateDict = json.load(file)

    try:
        tempDict = templateDict[templateType]
        srcPath = str(Path(os.path.join(examplePath, tempDict["template"])))
        if prefix != '':
            dstPath = str(Path(os.path.join(workingPath, prefix+'_'+tempDict["template"])))
        else:
            dstPath = str(Path(os.path.join(workingPath, tempDict["template"])))
        shutil.copy2(srcPath,dstPath)
    except KeyError:
        print("The template: %s doesn't exists capullo"%templateType)

def listTemplates():
    utilsPath = os.path.realpath(__file__)
    jsonPath = os.path.join(os.path.dirname(utilsPath),'examples','json','templates.json')
    with open(jsonPath, 'r') as file:
        templateDict = json.load(file)

    print("/-------- List of available hatariTools templates --------/\n")

    for key in templateDict.keys():
        print("Nr %d: %s"%(templateDict[key]["index"],key))
        print("    File: %s"%(templateDict[key]["template"]))
        print("    Description: %s\n"%(templateDict[key]["desc"]))

def isRunningInJupyter():
    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        return shell == 'ZMQInteractiveShell'
    except (NameError, ImportError):
        return False
    
def printBannerHtml():
    from IPython.display import display, HTML

    html_content = """
    <link href="https://fonts.googleapis.com/css2?family=Anton&display=swap" rel="stylesheet">

    <style>
        .styled-text {
        font-family: 'Anton', Impact, sans-serif;
        font-size: 32px;
        font-weight: bold;
        font-style: italic;
        }
    </style>

    <div>
    <a href="https://hatarilabs.com" target="_blank">
            <img src="https://olivosbellaterra.com/static/img/png/hatarilabs.png" alt="Hatarilabs" width="200" height="200"></a> 
            <p class="styled-text">build faster, analyze more</p>
    </div>

    <table border="0px">
    <tbody>
    <tr>
        <td><h3>Follow us:</h3></td>
        <td><a href="https://www.linkedin.com/company/hatarilabs" target="_blank">
            <img src="https://olivosbellaterra.com/static/img/svg/icons8-linkedin.svg" alt="Hatarilabs"></a></td>
        <td><a href="https://www.facebook.com/hatarilabs" target="_blank">
            <img src="https://olivosbellaterra.com/static/img/svg/icons8-facebook.svg" alt="Hatarilabs"></a></td>
        <td><a href="https://www.instagram.com/hatarilabs" target="_blank">
            <img src="https://olivosbellaterra.com/static/img/svg/icons8-instagram.svg" alt="Hatarilabs"></a></td>
        <td><a href="https://www.youtube.com/hatarilabs" target="_blank">
            <img src="https://olivosbellaterra.com/static/img/svg/icons8-youtube.svg" alt="Hatarilabs"></a></td>
        <td><a href="https://www.tiktok.com/@_hatarilabs" target="_blank">
            <img src="https://olivosbellaterra.com/static/img/svg/icons8-tiktok.svg" alt="Hatarilabs"></a></td>
        <td><a href="https://x.com/hatarilabs" target="_blank">
            <img src="https://olivosbellaterra.com/static/img/svg/icons8-twitterx.svg" alt="Hatarilabs"></a></td>
    </tr>
    </tbody>
    </table>

    """

    display(HTML(html_content))

def printBannerText():
    print('''
                                                                                                    
*mSi                                                                                       
gQQ>                                                                                       
dQU;                                 +|:                                     :v)_          
;PQm'                                %B$s                                    .gQMe          
PYQ7.                               -3QE_                                     <e}'          
c8Qx                                '$RT                                                    
?HM"   )7yw1=       .)r]jJfzi.   `=>!QDuvxxi_   `<s[LCwe<    ,>seua:  ^!C3o' `eur           
oRk= vdZ6qDQE"     ]PF)/+vJBNe`  :l{6Q8!I![s' .ebJ<//%3MD]   )fffQDv.ebPhZY/ QQQ#           
JQS'7b]_  ?Q$r     EWy     3Qg^     pQX       :GWj    _mQ5'     lQ&TT4v   .  rQDl           
5QnCV/    ]QZ<      :"/iiss4Q5:    -GQS        .:|/<v%IPQJ`     !Qk[h;       ?QK"           
.SQXd^    _JQh:    -*53e*ppaDQL.    _&QF       '!6fa{vzzMQa      7Q@q|        1Q@,           
;4QWi     :pQp    _dQY-   xm@Qa     _OQd      ^XQV.   rhHQ!     .wQBo         [QK^           
KkQ6'     '2QO}vc/:&QDa}75L<2Qgx="= .nQMCv)%I"UUQ81}j57>SQhi=|; .dQA'         %QQCi%)_       
/jJ>       82mw[i: /zmVFa|  ;t53j}+  `1mVpn!>_ UuSh21/  =oFy7{; .z#I          .nm57r/.       
                                                                                                                                                                                                                                      
''')