from db_oracle.connect import get_connection
from model.models import TaskF, ThemesF, ResultF
from flask import redirect, url_for, request, g
import config as cfg
import cx_Oracle


def programs():
    if cfg.debug_level > 3:
        print('Programs List ...')
    con = get_connection()
    cursor = con.cursor()
    cmd = 'select id_task, coalesce(period_for_testing,0) period_for_testing, name_task from tasks order by 1 desc'
    cursor.execute(cmd)
    cursor.rowfactory = TaskF
    if cfg.debug_level > 3:
        print('List programs have got...')
    return cursor


def program(id_task):
    if cfg.debug_level > 3:
        print('Programs List ...')
    con = get_connection()
    cursor = con.cursor()
    cmd = 'select id_task, coalesce(period_for_testing,0) period_for_testing, name_task ' \
          'from tasks t ' \
          'where t.id_task=:id ' \
          'order by 1 desc'
    cursor.execute(cmd, [id_task])
    cursor.rowfactory = TaskF
    if cfg.debug_level > 3:
        print('List programs have got...')
    return cursor


def program_upd(id_task, period_for_testing, name_task):
    if cfg.debug_level > 0:
        print("1.+++ History Create " + name_task + " : ")
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.callproc('admin.program_upd', [id_task, period_for_testing, name_task])
        cursor.close()
        con.close()
        if cfg.debug_level > 0:
            print("2. Успешное завершение добавления программы!")
    except cx_Oracle.IntegrityError as e:
        errorObj, = e.args
        print("Error Code:", errorObj.code)
        print("Error Message:", errorObj.message)
        print("При добавлении программы произошла ошибка")
        return


def program_add(period_for_testing, name_task):
    if cfg.debug_level > 0:
        print("1.+++ History Create " + name_task + " : " + period_for_testing)
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.callproc('admin.program_add', [period_for_testing, name_task])
        cursor.close()
        con.close()
        if cfg.debug_level > 0:
            print("2. Успешное завершение добавления программы!")
    except cx_Oracle.IntegrityError as e:
        errorObj, = e.args
        print("Error Code:", errorObj.code)
        print("Error Message:", errorObj.message)
        print("При добавлении программы произошла ошибка")
        return


def get_name_program(id_task):
    if cfg.debug_level > 3:
        print("Get Name Program " + str(id_task))
    try:
        con = get_connection()
        cursor = con.cursor()
        mess = cursor.callfunc('admin.get_name_program', str, [id_task])
        cursor.close()
        con.close()
        if cfg.debug_level > 3:
            print("2. Успешное завершение добавления программы!")
        return mess
    except cx_Oracle.IntegrityError as e:
        errorObj, = e.args
        print("Error Code:", errorObj.code)
        print("Error Message:", errorObj.message)
        print("При добавлении программы произошла ошибка")
        return


def program_delete(id_task):
    if cfg.debug_level > 2:
        print("program_delete. id_task " + str(id_task))
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.callproc('admin.program_delete', [id_task])
        cursor.close()
        con.close()
        return
    except cx_Oracle.IntegrityError as e:
        errorObj, = e.args
        print("Error Code:", errorObj.code)
        print("Error Message:", errorObj.message)
        print("Произошла ошибка при удалении Программы: " + str(id_task))
        return


def themes(id_task):
    if cfg.debug_level > 2:
        print('History Detail id_hist: '+str(id_task))
    con = get_connection()
    cursor = con.cursor()
    cmd = 'select bt.id_task, bt.id_theme, bt.theme_number, bt.count_question, bt.count_success, ' \
          't.descr as theme_name ' \
          'from bundle_themes bt, themes t ' \
          'where bt.id_task=:id ' \
          'and   bt.id_theme=t.id_theme'
    # print('CMD: '+cmd)
    cursor.execute(cmd, [id_task])
    cursor.rowfactory = ThemesF
    if cfg.debug_level > 3:
        print('History list have got...')
    return cursor


def theme(id_task, id_theme):
    if cfg.debug_level > 2:
        print('Theme id_theme: '+str(id_theme))
    con = get_connection()
    cursor = con.cursor()
    cmd = 'select bt.id_task, bt.id_theme, bt.theme_number, bt.count_question, bt.count_success,  t.descr as theme_name ' \
          'from bundle_themes bt, themes t ' \
          'where bt.id_task=:id1 ' \
          'and   bt.id_theme=:id2 ' \
          'and   bt.id_theme=t.id_theme'
    # print('CMD: '+cmd)
    cursor.execute(cmd, [id_task, id_theme])
    cursor.rowfactory = ThemesF
    if cfg.debug_level > 3:
        print('History list have got...')
    return cursor


def theme_update(id_task, id_theme, theme_name, theme_number, count_question, count_success):
    if cfg.debug_level > 2:
        print('Theme update. id_task: ' + str(id_task) + ', id_theme' + str(id_theme))
    con = get_connection()
    cursor = con.cursor()
    cursor.callproc("admin.theme_update", [id_task, id_theme, theme_name, theme_number, count_question, count_success])
    cursor.close()
    con.close()


def theme_delete(id_theme):
    if cfg.debug_level > 2:
        print('Theme delete. id_theme' + str(id_theme))
    con = get_connection()
    cursor = con.cursor()
    cursor.callproc("admin.theme_delete", [id_theme])
    cursor.close()
    con.close()


def get_result_info():
    if cfg.debug_level > 1:
        print('Get Result Info: ' + str(g.user.id_user) + ' : ' + str(g.user.username))
    con = get_connection()
    cursor = con.cursor()
    id_reg = cursor.var(cx_Oracle.DB_TYPE_NUMBER)
    iin = cursor.var(cx_Oracle.DB_TYPE_NVARCHAR)
    time_beg = cursor.var(cx_Oracle.DB_TYPE_DATE)
    time_end = cursor.var(cx_Oracle.DB_TYPE_DATE)
    fio = cursor.var(cx_Oracle.DB_TYPE_NVARCHAR)
    cursor.callproc('test.get_personal_info', (g.user.id_user, id_reg, iin, time_beg, time_end, fio))
    print('Got result info ' + fio.getvalue())
    return id_reg.getvalue(), iin.getvalue(), time_beg.getvalue(), time_end.getvalue(), fio.getvalue()


def get_result_info(id_reg):
    if cfg.debug_level > 1:
        print('Get Result Info: ' + str(g.user.id_user) + ' : ' + str(g.user.username))
    con = get_connection()
    cursor = con.cursor()
    iin = cursor.var(cx_Oracle.DB_TYPE_NVARCHAR)
    time_beg = cursor.var(cx_Oracle.DB_TYPE_DATE)
    time_end = cursor.var(cx_Oracle.DB_TYPE_DATE)
    fio = cursor.var(cx_Oracle.DB_TYPE_NVARCHAR)
    cursor.callproc('test.get_personal_info', (id_reg, iin, time_beg, time_end, fio))
    if cfg.debug_level > 1 and iin.getvalue() != '':
        print('Got result info ' + str(iin.getvalue()))
    if iin != '':
        return id_reg, iin.getvalue(), time_beg.getvalue(), time_end.getvalue(), fio.getvalue()
    else:
        return id_reg, '', '', '', ''


def get_result(id_registration):
    if cfg.debug_level > 1:
        print('Get answer for: ' + str(g.user.id_user) + ' : ' + str(g.user.username))
    con = get_connection()
    cursor = con.cursor()
    cmd = 'select theme_number, descr as theme_name, count_question, count_success, ' \
          'sum(true_result) true_score, sum(false_result) false_score ' \
          'from ( ' \
          'select th.id_theme, theme_number, th.descr, tft.count_question, tft.count_success, ' \
          'case when correctly=\'Y\' then 1 else 0 end true_result, ' \
          'case when correctly != \'Y\' then 1 else 0 end false_result ' \
          'from questions_for_testing qft, answers a, ' \
          'themes_for_testing tft, themes th ' \
          'where qft.id_registration=tft.id_registration ' \
          'and qft.id_theme=th.id_theme ' \
          'and a.id_answer(+) = qft.id_answer ' \
          'and tft.id_registration = :id ' \
          'and tft.id_theme = th.id_theme ' \
          ') ' \
          'group by theme_number, count_question, count_success, descr'
    cursor.execute(cmd, [id_registration])
    cursor.rowfactory = ResultF
    return cursor


def get_id_reg_by_iin(iin):
    if cfg.debug_level > 1:
        print('Got request for ИИН: ' + iin)
    con = get_connection()
    cursor = con.cursor()
    cmd = 'select id_registration ' \
          'from testing t, persons p ' \
          'where p.iin = :iin ' \
          'and t.id_person=p.id_person ' \
          'and t.status=\'Active\' '
    cursor.execute(cmd, [iin])
    id_reg = 0
    for rec in cursor:
        id_reg = rec[0]
    if cfg.debug_level > 1:
        print('ID_REG: ' + str(id_reg))
    return id_reg


# def history_search_by_sior_id(sior_id):
#     if cfg.debug_level > 3:
#         print('history_search_by_sior_id ...')
#     con = get_connection()
#     cursor = con.cursor()
#     cmd = 'select id_hist, id_user, date_op, sior_id, deleted, gfss_in_nom, doc_date, period, sum_gfss, p_bin, p_name,' \
#           ' sicid, iin, fio, doc_ret, date_ret, sum_ret, date_ret_gk, sum_ret_gk, doc_num_df, doc_date_df, reason_return ' \
#           'from HIST_RET_SO_031KNP where sior_id like :id||\'%\' '
#     if 'Admin' not in g.user.roles:
#         cmd = cmd + 'and deleted=\'N\' '
#     cmd = cmd + 'order by 1 desc'
#     if sior_id == '':
#         cursor.execute(cmd, [sior_id])
#     else:
#         cursor.execute(cmd, [sior_id])
#     cursor.rowfactory = HistoryRetSO031F
#     if cfg.debug_level > 3:
#         print('History list have got by sior_id ...')
#     return cursor
#
#
# def history_search_by_iin(iin):
#     if cfg.debug_level > 3:
#         print('History List ...')
#     con = get_connection()
#     cursor = con.cursor()
#     cmd = 'select id_hist, id_user, date_op, sior_id, deleted, gfss_in_nom, doc_date, period, sum_gfss, p_bin, p_name,' \
#           ' sicid, iin, fio, doc_ret, date_ret, sum_ret, date_ret_gk, sum_ret_gk, doc_num_df, doc_date_df, reason_return ' \
#           'from HIST_RET_SO_031KNP where iin like :id||\'%\' '
#     if 'Admin' not in g.user.roles:
#         cmd = cmd + 'and deleted=\'N\' '
#     cmd = cmd + 'order by 1 desc'
#     if cfg.debug_level > 3:
#         print('CMD: '+cmd)
#     cursor.execute(cmd, [iin])
#     cursor.rowfactory = HistoryRetSO031F
#     if cfg.debug_level > 3:
#         print('History list have got by IIN ...')
#     return cursor
#
#
# def history_search_by_isior_id_in(sior_id, iin):
#     if cfg.debug_level > 3:
#         print('History List ...')
#     con = get_connection()
#     cursor = con.cursor()
#     cmd = 'select id_hist, id_user, date_op, sior_id, deleted, gfss_in_nom, doc_date, period, sum_gfss, p_bin, p_name,' \
#           ' sicid, iin, fio, doc_ret, date_ret, sum_ret, date_ret_gk, sum_ret_gk, doc_num_df, doc_date_df, reason_return ' \
#           'from HIST_RET_SO_031KNP where sior_id like :id1||\'%\' and iin like :id2||\'%\' '
#     if 'Admin' not in g.user.roles:
#         cmd = cmd + 'and deleted=\'N\' '
#     cmd = cmd + 'order by 1 desc'
#     if cfg.debug_level > 3:
#         print('CMD: '+cmd)
#     cursor.execute(cmd, [sior_id, iin])
#     cursor.rowfactory = HistoryRetSO031F
#     if cfg.debug_level > 3:
#         print('History list have got by IIN ...')
#     return cursor
