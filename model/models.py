from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column

from main_app import app


db = SQLAlchemy(app)
print("Модель стартовала...")

class HistoryRetSO031:
    id_hist = db.Column(db.Integer, primary_key=True, unique=True)
    id_user = db.Column(db.Integer, nullable=False)
    date_op = db.Column(db.DateTime, nullable=False)
    sior_id = db.Column(db.Integer, nullable=False)
    deleted = db.Column(db.Integer, nullable=False)
    gfss_in_nom = db.Column(db.String(1), nullable=False)
    doc_date = db.Column(db.DateTime, primary_key=True, unique=True)
    period = db.Column(db.String(6), nullable=False)
    sum_gfss = db.Column(db.Integer, nullable=False)
    p_bin = db.Column(db.String(14), nullable=False)
    p_name = db.Column(db.String(300), nullable=False)
    sicid = db.Column(db.Integer, nullable=False)
    iin = db.Column(db.String(12), nullable=False)
    fio = db.Column(db.String(64), nullable=False)
    doc_ret = db.Column(db.String(30), nullable=False)
    date_ret = db.Column(db.DateTime,  nullable=False)
    sum_ret = db.Column(db.Integer,  nullable=False)
    date_ret_gk = db.Column(db.DateTime,  nullable=False)
    sum_ret_gk = db.Column(db.Integer,  nullable=False)
    doc_num_df = db.Column(db.String(30), nullable=True)
    doc_date_df = db.Column(db.DateTime,  nullable=False)
    reason_return = db.Column(db.String(128), nullable=True)


class HistoryRetSO031F:
    def __init__(self, id_hist, id_user, date_op, sior_id, deleted, gfss_in_nom, doc_date, period, sum_gfss, p_bin,
                 p_name, sicid, iin, fio,
                 doc_ret, date_ret, sum_ret, date_ret_gk, sum_ret_gk, doc_num_df, doc_date_df, reason_return):
        self.id_hist = id_hist
        self.id_user = id_user
        self.date_op = date_op
        self.sior_id = sior_id
        self.deleted = deleted
        self.gfss_in_nom = gfss_in_nom
        self.doc_date = doc_date
        self.period = period
        self.sum_gfss = sum_gfss
        self.p_bin = p_bin
        self.p_name = p_name
        self.sicid = sicid
        self.iin = iin
        self.fio = fio
        self.doc_ret = doc_ret
        self.date_ret = date_ret
        self.sum_ret = sum_ret
        self.date_ret_gk = date_ret_gk
        self.sum_ret_gk = sum_ret_gk
        self.doc_num_df = doc_num_df
        self.doc_date_df = doc_date_df
        self.reason_return = reason_return

