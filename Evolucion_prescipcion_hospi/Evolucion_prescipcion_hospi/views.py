from datetime import datetime
from flask import render_template
from flask import make_response
from flask import request
import pdfkit
import jinja2
import cx_Oracle
from Evolucion_prescipcion_hospi import app

cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_21_6")

config= pdfkit.configuration(wkhtmltopdf= r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')


def connection():
    con = cx_Oracle.connect('vpilco_ro/Exp3rt0#5@172.16.241.31:1521/TRN')
    return con

@app.route('/')
@app.route('/home', methods=['GET'])
def home():
    empresa = []
    nombrep = []
    apellidop = []
    sexo = []
    edad = []
    fecha = []
    hc = []
    pres = []
    nota = []
    aux = "FECHA_HORA"
    paciente = request.args.get('paciente')
    atencion = request.args.get('atencion')
    query1 = "Frecuencia: '|| (SELECT DS_TIP_FRE FROM TIP_FRE WHERE CD_TIP_FRE = ITPMED.CD_TIP_FRE)||' ('||(SELECT NM_OBJETO FROM PAGU_OBJETO WHERE CD_OBJETO = PMED.CD_OBJETO)||') '||CHR(13)||CHR(10) AS RESULTADOS FROM ITPRE_MED ITPMED, PRE_MED PMED, ATENDIME ATE WHERE ITPMED.CD_PRE_MED (+) = PMED.CD_PRE_MED AND PMED.CD_ATENDIMENTO = ATE.CD_ATENDIMENTO AND ATE.CD_PACIENTE = "+ str(paciente)+" AND ATE.CD_ATENDIMENTO = "+ str(atencion)+" AND  ITPMED.CD_TIP_ESQ NOT IN (SELECT CD_TIP_ESQ FROM TIP_ESQ WHERE  SN_EXA_RX = 'S' OR  SN_EXA_LAB = 'S') AND  CD_TIP_ESQ NOT IN ('CON','MDN','MDC','CAR','GUR','MUS','ORL','MRE','VAR','MMD','ME','MDA','PFO','PPS','POD','PEN','PME','PFI','PTO','CIH') UNION (SELECT 1200 SEC,DECODE(TP_PRE_MED,'E','ENFERMERA: ','MEDICO: ')||P.CD_PRESTADOR||' - '||NM_PRESTADOR||' MSP:'||CD_IDENTIFICACAO||CHR(13)||CHR(10)   FROM PRESTADOR P,PRE_MED PMED WHERE P.CD_PRESTADOR = PMED.CD_PRESTADOR AND PMED.CD_ATENDIMENTO = "+ str(atencion)+" ) ) ORDER BY SEC"

    conn1 = connection()
    cursor1 = conn1.cursor()
    cursor1.execute("select a.ds_razao_social from multi_empresas a where rownum=1")
    for row in cursor1.fetchall():
       empresa.append({"empresa":row[0]})
    cursor2 = conn1.cursor()
    cursor2.execute("select DS_PRIMEIRO_NOME || ' ' || DS_SEGUNDO_NOME from dbamv.paciente where paciente.cd_paciente="+str(paciente))
    for row in cursor2.fetchall():
       nombrep.append({"nombre":row[0]})
    cursor3 = conn1.cursor()
    cursor3.execute("select DS_PRIMEIRO_SOBRENOME || ' ' || DS_SEGUNDO_SOBRENOME from dbamv.paciente where paciente.cd_paciente="+str(paciente))
    for row in cursor3.fetchall():
       apellidop.append({"apellido":row[0]})
    cursor4 = conn1.cursor()
    cursor4.execute("select tp_sexo from PACIENTE where cd_paciente ="+str(paciente))
    for row in cursor4.fetchall():
       sexo.append({"sexo":row[0]})
    cursor5 = conn1.cursor()
    cursor5.execute("select trunc(months_between(sysdate, dt_nascimento) / 12) || 'a ' from paciente where cd_paciente ="+str(paciente))
    for row in cursor5.fetchall():
       edad.append({"edad":row[0]})
    cursor6 = conn1.cursor()
    cursor6.execute("select "+str(paciente)+" from dual")
    for row in cursor6.fetchall():
       hc.append({"hc":row[0]})
    cursor7 = conn1.cursor()
    cursor7.execute("SELECT RESULTADO FROM ( SELECT 100 SEC, '(D- DIAGNOTICO PRINCIPAL + DIAGNOSTICO SECUNDARIO)'||CHR(13)||CHR(10) AS RESULTADO FROM DUAL UNION SELECT  /*+ RULE  */  101 SEC, ' * '||dia.cd_cid||' - '||ds_cid||' - Tiempo de Enfermedad: '||QT_TEMPO_DOENCA||DECODE(TP_UNIDADE_TEMPO_DOENCA,'D', ' Dia(s) ','H', ' Hora(s) ','M','Mes(s) ', null)||' - '|| decode(LTRIM(RTRIM(Dia.TP_SITUACAO)), 'HIPOTESE','(PRESUNTIVO)', 'CONFIRMADO',  '(DEFINITIVO)', null)||' - Observaciones: '||DS_OBSERVACAO||CHR(10)||CHR(13) AS RESULTADO from dbamv.diagnostico_atendime  dia, cid,atendime ate where dia.cd_atendimento = ate.cd_atendimento AND ate.CD_PACIENTE = "+ str(paciente)+" AND dia.CD_ATENDIMENTO = "+ str(atencion)+" and dia.cd_cid = cid.cd_cid UNION  select  101 SEC, ' * '||dia.cd_cid||' - '||ds_cid||' - Tiempo de Enfermedad: '||QT_TEMPO_DOENCA||DECODE(TP_UNIDADE_TEMPO_DOENCA,'D', ' Dia(s) ','H', ' Hora(s) ','M','Mes(s) ', null)||' - '|| decode(LTRIM(RTRIM(TP_SITUACAO)), 'HIPOTESE','(PRESUNTIVO)', 'CONFIRMADO', '(DEFINITIVO)', null)||' Observaciones: '||DS_OBSERVACAO||CHR(13)||CHR(10) AS RESULTADO from dbamv.Atendime Ate, dbamv.PW_DIAGNOSTICO_ATENDIME_CID Dia, dbamv.Diagnostico_Atendime diag, cid where Ate.Cd_Atendimento = Dia.Cd_Atendimento and Dia.cd_atendimento =  "+ str(atencion)+" AND CD_PACIENTE = "+ str(paciente)+" and dia.cd_cid = cid.cd_cid and diag.cd_diagnostico_atendime = dia.cd_diagnostico_atendime UNION (SELECT 102 SEC, CHR(13)||CHR(10)||'MEDICO: '||P.CD_PRESTADOR||' - '||NM_PRESTADOR||' MSP:'||CD_IDENTIFICACAO FROM PRESTADOR P,ATENDIME A WHERE P.CD_PRESTADOR = A.CD_PRESTADOR AND A.CD_ATENDIMENTO ="+ str(atencion)+" AND A.CD_PACIENTE = "+ str(paciente)+" ) UNION SELECT 300 SEC, CHR(10)||CHR(13)||'(C- CIRURGIA) '||CHR(10)||CHR(13) FROM DUAL UNION SELECT 301 SEC, /*+ RULE */ DS_SITUACAO||' - '|| CHR(13)||CHR(10)||DS_CIRURGIA||' - '||CHR(13)||CHR(10)|| DS_ATI_MED||': '||(SELECT NM_PRESTADOR FROM PRESTADOR WHERE CD_PRESTADOR = C.CD_PRESTADOR)||CHR(13)||CHR(10) AS RESULTADO FROM V_CADASTRAR_PRESTADOR_CIRURGIA C WHERE cd_atendimento  ="+ str(atencion)+" UNION SELECT 400 SEC, CHR(13)||CHR(10)||'(A- ALERGIAS)'||CHR(13)||CHR(10) FROM DUAL UNION (SELECT /*+ RULE */401 SEC, ' * '||'Tipo: '||DECODE(TP_ALERGIA,'O','Otros','A','Alimentos','S','Medicamentos')||'  -  '|| 'Severidad: '||DECODE(TP_SEVERIDADE,'G','Grave','M','Moderada','L','Leve','D','Desconocida')||' - '|| 'Observaciones: '||DS_ALERGIA||CHR(10)||CHR(13) RESULTADOS FROM HIST_SUBS_PAC WHERE CD_PACIENTE = "+ str(paciente)+" UNION SELECT  401 SEC, ' * ' || 'Tipo: '||DECODE(TP_ALERGIA,'O','Otros','A','Alimentos','S','Medicamentos')||' - '|| 'Severidad: '||DECODE(TP_SEVERIDADE,'G','Grave','M','Moderada','L','Leve','D','Desconocida') || ' - ' || 'Observaciones: '||DECODE(TP_SEVERIDADE,'O',DS_OUTROS,NULL)||' '|| (SELECT DS_SUBSTANCIA FROM SUBSTANCIA WHERE CD_SUBSTANCIA = A.CD_SUBSTANCIA)||' '|| (SELECT DS_ALIMENTO FROM PW_ALIMENTO WHERE CD_ALIMENTO = A.CD_ALIMENTO) ||CHR(10)||CHR(13)  RESULTADOS from PW_ALERGIA_PAC A, PW_PROBLEMA P WHERE A.CD_PROBLEMA = P.CD_PROBLEMA AND P.CD_PACIENTE = "+ str(paciente)+" UNION SELECT 500 SEC, CHR(10)||CHR(13)||'('||'CONCILIACION MEDICAMENTOSA)'||CHR(13)||CHR(10) FROM DUAL UNION SELECT /*+ RULE */ 501 SEC, ' * '||MEDU.DS_MEDICAMENTO_USO|| CHR(13)||CHR(10) MEDICAMENTOS FROM PW_MEDICAMENTO_USO MEDU WHERE MEDU.CD_ATENDIMENTO = "+ str(atencion)+" UNION SELECT 601 SEC,  CHR(13)||CHR(10)||'('||'EXAMENES )'||CHR(13)||CHR(10) FROM DUAL UNION SELECT  602 SEC, ' * '||(SELECT DS_TIP_PRESC FROM TIP_PRESC WHERE CD_TIP_PRESC = ITPMED.CD_TIP_PRESC)||' Fecha Inicio: '|| TO_CHAR(DH_INICIAL,'DD/MM/RRRR')||' '|| (SELECT NM_SET_EXA FROM SET_EXA WHERE CD_SET_EXA = ITPMED.CD_SET_EXA)||' Cantidad: '|| QT_ITPRE_MED ||' Unidad: '|| (SELECT DS_UNIDADE FROM UNI_PRO WHERE CD_UNI_PRO = ITPMED.CD_UNI_PRO AND CD_PRODUTO = ITPMED.CD_PRODUTO) ||' '|| (SELECT DS_FOR_APL FROM FOR_APL WHERE CD_FOR_APL = ITPMED.CD_FOR_APL)||' Frecuencia: '|| (SELECT DS_TIP_FRE FROM TIP_FRE WHERE CD_TIP_FRE = ITPMED.CD_TIP_FRE)||' ('||(SELECT NM_OBJETO FROM PAGU_OBJETO WHERE CD_OBJETO = PMED.CD_OBJETO)||') '||CHR(13)||CHR(10) AS RESULTADOS FROM ITPRE_MED ITPMED, PRE_MED PMED, ATENDIME ATE WHERE ITPMED.CD_PRE_MED (+)  = PMED.CD_PRE_MED AND PMED.CD_ATENDIMENTO = ATE.CD_ATENDIMENTO AND ATE.CD_PACIENTE ="+ str(paciente)+" AND ATE.CD_ATENDIMENTO = "+ str(atencion)+" AND  ITPMED.CD_TIP_ESQ IN (SELECT CD_TIP_ESQ FROM TIP_ESQ WHERE  SN_EXA_RX = 'S' OR  SN_EXA_LAB = 'S') AND ITPMED.CD_TIP_ESQ != 'PME' UNION SELECT 603 SEC,  CHR(13)||CHR(10)||'('||'PROCEDIMIENTOS )'||CHR(13)||CHR(10) FROM DUAL UNION SELECT  603 SEC, '('||INITCAP((SELECT DS_TIP_ESQ FROM TIP_ESQ WHERE CD_TIP_ESQ = ITPMED.CD_TIP_ESQ))||')'|| CHR(13)||CHR(10)|| ' * '||(SELECT DS_TIP_PRESC FROM TIP_PRESC WHERE CD_TIP_PRESC = ITPMED.CD_TIP_PRESC)||' Fecha Inicio: '|| TO_CHAR(DH_INICIAL,'DD/MM/RRRR')||' '|| (SELECT NM_SET_EXA FROM SET_EXA WHERE CD_SET_EXA = ITPMED.CD_SET_EXA)||' Cantidad: '|| QT_ITPRE_MED ||' Unidad: '|| (SELECT DS_UNIDADE FROM UNI_PRO WHERE CD_UNI_PRO = ITPMED.CD_UNI_PRO  AND CD_PRODUTO = ITPMED.CD_PRODUTO) ||' '||  (SELECT DS_FOR_APL FROM FOR_APL  WHERE CD_FOR_APL = ITPMED.CD_FOR_APL)||' Frecuencia: '|| (SELECT DS_TIP_FRE FROM TIP_FRE WHERE CD_TIP_FRE = ITPMED.CD_TIP_FRE)||' ('||(SELECT NM_OBJETO FROM PAGU_OBJETO WHERE CD_OBJETO = PMED.CD_OBJETO)||') '||CHR(13)||CHR(10) AS RESULTADOS FROM ITPRE_MED ITPMED, PRE_MED PMED, ATENDIME ATE WHERE ITPMED.CD_PRE_MED (+)  = PMED.CD_PRE_MED AND PMED.CD_ATENDIMENTO = ATE.CD_ATENDIMENTO AND ATE.CD_PACIENTE ="+ str(paciente)+" AND ATE.CD_ATENDIMENTO = "+ str(atencion)+" AND ITPMED.CD_TIP_ESQ IN ('PFO','PPS','POD','PEN','PME','PFI','PTO','CIH') UNION SELECT 604 SEC,  CHR(13)||CHR(10)||'('||'M-MEDICAMENTOS)'||CHR(13)||CHR(10) FROM DUAL UNION SELECT  605 SEC, ' * '||(SELECT DS_TIP_PRESC FROM TIP_PRESC WHERE CD_TIP_PRESC = ITPMED.CD_TIP_PRESC)||' Fecha Inicio: '|| TO_CHAR(DH_INICIAL,'DD/MM/RRRR')||' '|| (SELECT NM_SET_EXA FROM SET_EXA WHERE CD_SET_EXA = ITPMED.CD_SET_EXA)||' Cantidad: '|| QT_ITPRE_MED ||' Unidad: '|| (SELECT DS_UNIDADE FROM UNI_PRO WHERE CD_UNI_PRO = ITPMED.CD_UNI_PRO AND CD_PRODUTO = ITPMED.CD_PRODUTO) ||' '|| (SELECT DS_FOR_APL FROM FOR_APL WHERE CD_FOR_APL = ITPMED.CD_FOR_APL)||' Frecuencia: '|| (SELECT DS_TIP_FRE FROM TIP_FRE WHERE CD_TIP_FRE = ITPMED.CD_TIP_FRE)||' ('||(SELECT NM_OBJETO FROM PAGU_OBJETO WHERE CD_OBJETO = PMED.CD_OBJETO)||') '||CHR(10)||CHR(13) AS RESULTADOS FROM ITPRE_MED ITPMED, PRE_MED PMED, ATENDIME ATE WHERE ITPMED.CD_PRE_MED (+)  = PMED.CD_PRE_MED AND PMED.CD_ATENDIMENTO = ATE.CD_ATENDIMENTO AND ATE.CD_PACIENTE ="+ str(paciente)+" AND ATE.CD_ATENDIMENTO = "+ str(atencion)+" AND  ITPMED.CD_TIP_ESQ  IN ( 'CON','MDN','MDC','CAR','GUR','MUS','ORL','MRE','VAR','MMD','MDA')) UNION SELECT 700 SEC,  CHR(13)||CHR(10)||'('||'ESCALAS DE VALORACION)'||CHR(13)||CHR(10) FROM DUAL UNION SELECT /*+ RULE */ 701 SEC, ' * '||(SELECT DS_PERGUNTA FROM PAGU_PERGUNTA WHERE CD_PERGUNTA = ITAV.CD_PERGUNTA)||' - Respuesta: '||NVL(DS_RESPOSTA,VL_RESPOSTA)||' Resultado: '||VL_RESULTADO ||CHR(13)||CHR(10) RESULTADOS FROM PAGU_ITAVALIACAO ITAV, PAGU_AVALIACAO PAAV WHERE PAAV.CD_AVALIACAO IN (SELECT CD_AVALIACAO FROM PAGU_AVALIACAO WHERE CD_ATENDIMENTO = "+ str(atencion)+" ) AND ITAV.CD_AVALIACAO = PAAV.CD_AVALIACAO UNION SELECT 800 SEC, CHR(13)||CHR(10)||'(SOLICITUD DE INTERCONSULTA)'||CHR(10)||CHR(13) FROM DUAL UNION SELECT /*+ RULE */ 801 SEC, ' Solicitado por: '||(SELECT  NM_PRESTADOR  FROM PRESTADOR WHERE CD_PRESTADOR = PAR_MED.CD_PRESTADOR) ||CHR(10)||CHR(13)||' Especialidad Solicitada: '||(SELECT DS_ESPECIALID FROM ESPECIALID WHERE CD_ESPECIALID = PAR_MED.CD_ESPECIALID )||CHR(10)||CHR(13)||' Para: '|| (SELECT NM_PRESTADOR FROM PRESTADOR WHERE CD_PRESTADOR = CD_PRESTADOR_REQUISITADO)||CHR(10)||CHR(13)||' Motivo: '||DS_SOLICITACAO||CHR(13)||CHR(10) RESULTADOS FROM PAR_MED,  atendime ate where ate.cd_atendimento = "+ str(atencion)+" and ate.cd_atendimento = par_med.cd_atendimento UNION SELECT 900 SEC,CHR(13)||CHR(10)||'('||'V- MONITOREO SIGNOS VITALES)'|| CHR(13)||CHR(10) FROM DUAL UNION select /*+ RULE */ 901 SEC, ' * '||(SELECT DS_SINAL_VITAL FROM SINAL_VITAL WHERE CD_SINAL_VITAL =  ITSV.CD_SINAL_VITAL)||' - '||ITSV.VALOR||' '|| (SELECT DS_UNIDADE_AFERICAO FROM PW_UNIDADE_AFERICAO WHERE CD_UNIDADE_AFERICAO =  ITSV.CD_UNIDADE_AFERICAO AND SN_ATIVO = 'S')||' '||(SELECT DS_INSTRUMENTO_AFERICAO FROM PW_INSTRUMENTO_AFERICAO WHERE CD_INSTRUMENTO_AFERICAO =  ITSV.CD_INSTRUMENTO_AFERICAO) ||CHR(13)||CHR(10) RESULTADOS from ITCOLETA_SINAL_VITAL ITSV, COLETA_SINAL_VITAL COSV where  COSV.CD_ATENDIMENTO = "+ str(atencion)+" AND COSV.CD_COLETA_SINAL_VITAL = ITSV.CD_COLETA_SINAL_VITAL AND NVL(VALOR,0) > 0 UNION (SELECT 902 SEC, CHR(13)||CHR(10)||'MEDICO: '||P.CD_PRESTADOR||' - '||NM_PRESTADOR||' MSP:'||CD_IDENTIFICACAO RESULTADOS FROM PRESTADOR P, COLETA_SINAL_VITAL COSV WHERE P.CD_PRESTADOR = COSV.CD_PRESTADOR AND CD_ATENDIMENTO = "+ str(atencion)+" ) UNION SELECT 1000 SEC,  CHR(13)||CHR(10)||'(ALTA)'||CHR(10)||CHR(13) FROM DUAL UNION SELECT /*+ RULE */ 1001 SEC, 'Motivo del Alta: '||(SELECT DS_TIPO_DOCUMENTO  FROM PW_DOCUMENTO_CLINICO DCLI, PW_TIPO_DOCUMENTO TDOC WHERE CD_DOCUMENTO_CLINICO = REA.CD_DOCUMENTO_CLINICO AND DCLI.CD_TIPO_DOCUMENTO = TDOC.CD_TIPO_DOCUMENTO)||'Diagn�stico de Alta: '||REA.CD_CID||' '||(SELECT DS_CID FROM CID WHERE CD_CID = REA.CD_CID)||'Observaciones: '||DS_OBS_ALTA||CHR(10)||CHR(13)||CHR(10)||CHR(13)|| 'MEDICO: '||(SELECT NM_PRESTADOR FROM PRESTADOR WHERE CD_PRESTADOR = REA.CD_PRESTADOR)  RESULTADOS FROM PW_REGISTRO_ALTA REA WHERE CD_ATENDIMENTO = "+ str(atencion)+" UNION SELECT 1100 SEC,  CHR(13)||CHR(10)||'(OTROS)'||CHR(10)||CHR(13) FROM DUAL UNION SELECT  1101 SEC, '('||INITCAP((SELECT DS_TIP_ESQ FROM TIP_ESQ WHERE CD_TIP_ESQ = ITPMED.CD_TIP_ESQ))||')'|| CHR(13)||CHR(10)||' * '||(SELECT DS_TIP_PRESC FROM TIP_PRESC WHERE CD_TIP_PRESC = ITPMED.CD_TIP_PRESC)||' Fecha Inicio: '|| TO_CHAR(DH_INICIAL,'DD/MM/RRRR')||' '||' "+query1)
    for row in cursor7.fetchall():
       pres.append({"pres":row[0]})
    cursor8 = conn1.cursor()
    cursor8.execute("SELECT FECHA_HORA FROM ( SELECT TO_CHAR(DT_PRE_MED,'DD/MM/RRRR')||'  '||TO_CHAR(HR_PRE_MED,'HH24:MI')  AS FECHA_HORA, editor_custom.hvq_fnc_consulta_evoluciones(ATE.CD_PACIENTE, PMED.CD_ATENDIMENTO, PMED.CD_PRE_MED) NOTA_EVOLUCION, NULL AS PRESCRIPCION FROM PRE_MED PMED, ATENDIME ATE WHERE PMED.CD_ATENDIMENTO = ATE.CD_ATENDIMENTO AND ATE.CD_PACIENTE = "+str(paciente)+" AND ATE.CD_ATENDIMENTO = "+str(atencion)+" )GROUP BY FECHA_HORA ORDER BY FECHA_HORA")
    for row in cursor8.fetchall():
       fecha.append({"fecha":row[0]})
    cursor9 = conn1.cursor()
    cursor9.execute("SELECT NOTA_EVOLUCION || LISTAGG(PRESCRIPCION, CHR(13)||CHR(10) ) WITHIN GROUP (ORDER BY FECHA_HORA) PRESCRIPCIÓN FROM ( SELECT /*+ RULE */ TO_CHAR(DT_PRE_MED,'DD/MM/RRRR')||'  '||TO_CHAR(HR_PRE_MED,'HH24:MI')  AS FECHA_HORA, editor_custom.hvq_fnc_consulta_evoluciones(ATE.CD_PACIENTE, PMED.CD_ATENDIMENTO, PMED.CD_PRE_MED)||CHR(10)||CHR(13)||CHR(10)||CHR(13)||DECODE(TP_PRE_MED,'E','ENFERMERA: ','MEDICO: ')||(SELECT CD_PRESTADOR||' - '||NM_PRESTADOR||' MSP:'||CD_IDENTIFICACAO FROM PRESTADOR WHERE CD_PRESTADOR = PMED.CD_PRESTADOR)  NOTA_EVOLUCION,NULL AS PRESCRIPCION FROM PRE_MED PMED, ATENDIME ATE  WHERE PMED.CD_ATENDIMENTO = ATE.CD_ATENDIMENTO AND ATE.CD_PACIENTE = "+str(paciente)+" AND ATE.CD_ATENDIMENTO = "+str(atencion)+" and  editor_custom.hvq_fnc_consulta_evoluciones(ATE.CD_PACIENTE, PMED.CD_ATENDIMENTO,PMED.CD_PRE_MED) is not null) GROUP BY NOTA_EVOLUCION")
    for row in cursor9.fetchall():
       nota.append({"nota":row[0]})
    conn1.close()

    res = render_template(
        'index.html',
         empresa=empresa, nombrep=nombrep, apellidop=apellidop,sexo=sexo, edad=edad, hc=hc, pres=pres, fecha=fecha, nota=nota
    )
    options = {
        "enable-local-file-access": True,
        "page-size": "A4",
        "footer-html": "./templates/encabezado.html"
        
        }
    responsestring = pdfkit.from_string(res, options=options)
    response = make_response(responsestring)
    response.headers['Content-Type']='application/pdf'
    response.headers['Content-Disposition'] = 'attachment;filename=output.pdf'
    return response