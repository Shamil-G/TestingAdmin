from main_app import app
from flask import render_template, request, redirect, g, flash
from flask_login import login_required
# from view import app
from model.dml_models import *
from reports.rep_refund_031knp import rep_refund_031knp
import cx_Oracle
import config as cfg
from model.utils import *
#  Не удалять - неправильно красит среда!!!


if cfg.debug_level > 0:
    print("Routes стартовал...")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@app.route('/main', methods=['GET', 'POST'])
@app.route('/history', methods=['GET', 'POST'])
@login_required
def view_history():
    if 'Operator DASORP' in g.user.roles or \
            'Admin' in g.user.roles:

        print("HISTORY. Method: "+request.method+" "+request.path)
        sior_id = request.form.get('sior_id')
        iin = request.form.get('iin')
        if request.method == "POST":
            if cfg.debug_level > 1:
                print("2. HISTORY view_history_search: " + app.static_folder)
            if sior_id != '' and iin != '':
                print("2.HISTORY  view_history_search.  sior_id: " + sior_id + ", IIN: "+iin)
                return render_template("history.html", cursor=history_search_by_isior_id_in(sior_id, iin))
            if sior_id != '':
                print("2.HISTORY  view_history_search.  sior_id: " + sior_id)
                return render_template("history.html", cursor=history_search_by_sior_id(sior_id))
            if iin != '':
                print("3.HISTORY  view_history_search.  iin: " + iin)
                return render_template("history.html", cursor=history_search_by_iin(iin))
            print("4. HISTORY view_history_search.  simple render...")
            return render_template("history.html", cursor=history())
        return render_template("history.html", cursor=history())


@app.route('/history/<int:id_hist>')
@login_required
def view_history_detail(id_hist):
    print("Had got DATE_OP: " + str(id_hist))
    is_admin = 'N'
    if 'Admin' in g.user.roles:
        is_admin = 'Y'
    return render_template("refund_detail.html", is_admin=is_admin, cursor=history_detail(id_hist))


@app.route('/refund-add', methods=['POST', 'GET'])
@login_required
def view_history_create():
    if cfg.debug_level > 1:
        print("Добавляем модель !")
    if request.method == "POST":
        if cfg.debug_level > 0:
            print("1. View добавляем!")
        sior_id = request.form['sior_id']
        doc_ret = request.form['doc_ret']
        date_ret = request.form['date_ret']
        sum_ret = request.form['sum_ret']
        date_ret_gk = request.form['date_ret_gk']
        sum_ret_gk = request.form['sum_ret_gk']
        doc_num_df = request.form['doc_num_df']
        doc_date_df = request.form['doc_date_df']
        reason_return = request.form['reason_return']
        try:
            if cfg.debug_level > 3:
                print("2. +++++++ View добавляем!")
                print(str(sior_id) + " : " + doc_ret + " : " + str(sum_ret))
            history_create(sior_id, doc_ret, date_ret, sum_ret, date_ret_gk, sum_ret_gk, doc_num_df, doc_date_df, reason_return)
            return redirect('/history')
        except cx_Oracle.IntegrityError as e:
            errorObj, = e.args
            if cfg.debug_level > 1:
                print("Error Code:", errorObj.code)
                print("Error Message:", errorObj.message)
                print("При добавлении возврата произошла ошибка")
            return redirect("/history")
    else:
        if cfg.debug_level > 0:
            print("Вход по GET: goto history-create.html")
        return render_template("history-create.html")


@app.route('/history_detail/<int:id_hist>/del')
@login_required
def view_history_delete(id_hist):
    try:
        history_delete(id_hist)
        return redirect('/history')
    except cx_Oracle.IntegrityError as e:
        errorObj, = e.args
        if cfg.debug_level >= 0:
            print("Error Code:", errorObj.code)
            print("Error Message:", errorObj.message)
            print("Произошла ошибка при удалении модели: " + str(id_hist))
        return redirect('/history')


@app.route('/user/<string:name>/<int:id_user>')
def user_page(name, id_user):
    return "User: " + name + " : " + str(id_user)


@app.route('/history/report_031')
def view_report_0701():
    if cfg.debug_level > 2:
        print("Выдаем отчет отчет по 031 КНП ")
    new_path = rep_refund_031knp()
    if cfg.debug_level > 1:
        print("2. Успешное передача отчета: "+new_path)
    return redirect(url_for('uploaded_file', filename=new_path))
