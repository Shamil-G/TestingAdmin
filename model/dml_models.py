from db_oracle.connect import get_connection
from model.models import HistoryRetSO031F
from flask import redirect, url_for, request, g
import config as cfg
import cx_Oracle


def history():
    if cfg.debug_level > 3:
        print('History List ...')
    con = get_connection()
    cursor = con.cursor()
    if 'Admin' in g.user.roles:
        cmd = 'select id_hist, id_user, date_op, sior_id, deleted, gfss_in_nom, doc_date, period, sum_gfss, p_bin, p_name,' \
              ' sicid, iin, fio, doc_ret, date_ret, sum_ret, date_ret_gk, sum_ret_gk, doc_num_df, doc_date_df, reason_return ' \
              'from HIST_RET_SO_031KNP order by 1 desc'
        print("We are admin")
    else:
        cmd = 'select id_hist, id_user, date_op, sior_id, deleted, gfss_in_nom, doc_date, period, sum_gfss, p_bin, p_name,' \
              ' sicid, iin, fio, doc_ret, date_ret, sum_ret, date_ret_gk, sum_ret_gk, doc_num_df, doc_date_df, reason_return ' \
              'from HIST_RET_SO_031KNP where deleted=\'N\' order by 1 desc'
    cursor.execute(cmd)
    cursor.rowfactory = HistoryRetSO031F
    if cfg.debug_level > 3:
        print('History list have got...')
    return cursor


def history_detail(id_hist):
    if cfg.debug_level > 2:
        print('History Detail id_hist: '+str(id_hist))
    con = get_connection()
    cursor = con.cursor()
    cmd = 'select id_hist, id_user, date_op, sior_id, deleted, gfss_in_nom, doc_date, period, sum_gfss, p_bin, p_name,' \
          ' sicid, iin, fio, doc_ret, date_ret, sum_ret, date_ret_gk, sum_ret_gk, doc_num_df, doc_date_df, reason_return ' \
          ' from HIST_RET_SO_031KNP h where h.id_hist=:id'
    # print('CMD: '+cmd)
    cursor.execute(cmd, [id_hist])
    cursor.rowfactory = HistoryRetSO031F
    if cfg.debug_level > 3:
        print('History list have got...')
    return cursor


def history_create(sior_id, doc_ret, date_ret, sum_ret, date_ret_gk, sum_ret_gk, doc_num_df, doc_date_df, reason_return):
    if cfg.debug_level > 0:
        print("1.+++ History Create " + str(sior_id) + " : " + str(date_ret) + " : " + str(sum_ret)+", user: "+str(g.user.id_user))
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.callproc('refund_031knp.add_sior', [sior_id, g.user.id_user, doc_ret, date_ret, sum_ret,
                                                   date_ret_gk, sum_ret_gk, doc_num_df, doc_date_df, reason_return])
        cursor.close()
        con.close()
        if cfg.debug_level > 0:
            print("2. Успешное завершение добавления возврата!")
    except cx_Oracle.IntegrityError as e:
        errorObj, = e.args
        print("Error Code:", errorObj.code)
        print("Error Message:", errorObj.message)
        print("При добавлении возврата произошла ошибка")
        return


def history_delete(id_hist):
    if cfg.debug_level > 0:
        print("history_delete. id_model " + str(id_hist)+str(g.user.roles))
    try:
        con = get_connection()
        cursor = con.cursor()
        cursor.callproc('refund_031knp.hist_delete', [id_hist,g.user.id_user])
        cursor.close()
        con.close()
        return
    except cx_Oracle.IntegrityError as e:
        errorObj, = e.args
        print("Error Code:", errorObj.code)
        print("Error Message:", errorObj.message)
        print("Произошла ошибка при удалении Возврата: " + str(id_hist))
        return


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
