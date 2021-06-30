from db_oracle.connect import get_connection
from model.models import TaskF, ThemesF
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


def history_search_by_sior_id(sior_id):
    if cfg.debug_level > 3:
        print('history_search_by_sior_id ...')
    con = get_connection()
    cursor = con.cursor()
    cmd = 'select id_hist, id_user, date_op, sior_id, deleted, gfss_in_nom, doc_date, period, sum_gfss, p_bin, p_name,' \
          ' sicid, iin, fio, doc_ret, date_ret, sum_ret, date_ret_gk, sum_ret_gk, doc_num_df, doc_date_df, reason_return ' \
          'from HIST_RET_SO_031KNP where sior_id like :id||\'%\' '
    if 'Admin' not in g.user.roles:
        cmd = cmd + 'and deleted=\'N\' '
    cmd = cmd + 'order by 1 desc'
    if sior_id == '':
        cursor.execute(cmd, [sior_id])
    else:
        cursor.execute(cmd, [sior_id])
    cursor.rowfactory = HistoryRetSO031F
    if cfg.debug_level > 3:
        print('History list have got by sior_id ...')
    return cursor


def history_search_by_iin(iin):
    if cfg.debug_level > 3:
        print('History List ...')
    con = get_connection()
    cursor = con.cursor()
    cmd = 'select id_hist, id_user, date_op, sior_id, deleted, gfss_in_nom, doc_date, period, sum_gfss, p_bin, p_name,' \
          ' sicid, iin, fio, doc_ret, date_ret, sum_ret, date_ret_gk, sum_ret_gk, doc_num_df, doc_date_df, reason_return ' \
          'from HIST_RET_SO_031KNP where iin like :id||\'%\' '
    if 'Admin' not in g.user.roles:
        cmd = cmd + 'and deleted=\'N\' '
    cmd = cmd + 'order by 1 desc'
    if cfg.debug_level > 3:
        print('CMD: '+cmd)
    cursor.execute(cmd, [iin])
    cursor.rowfactory = HistoryRetSO031F
    if cfg.debug_level > 3:
        print('History list have got by IIN ...')
    return cursor


def history_search_by_isior_id_in(sior_id, iin):
    if cfg.debug_level > 3:
        print('History List ...')
    con = get_connection()
    cursor = con.cursor()
    cmd = 'select id_hist, id_user, date_op, sior_id, deleted, gfss_in_nom, doc_date, period, sum_gfss, p_bin, p_name,' \
          ' sicid, iin, fio, doc_ret, date_ret, sum_ret, date_ret_gk, sum_ret_gk, doc_num_df, doc_date_df, reason_return ' \
          'from HIST_RET_SO_031KNP where sior_id like :id1||\'%\' and iin like :id2||\'%\' '
    if 'Admin' not in g.user.roles:
        cmd = cmd + 'and deleted=\'N\' '
    cmd = cmd + 'order by 1 desc'
    if cfg.debug_level > 3:
        print('CMD: '+cmd)
    cursor.execute(cmd, [sior_id, iin])
    cursor.rowfactory = HistoryRetSO031F
    if cfg.debug_level > 3:
        print('History list have got by IIN ...')
    return cursor
