from flask import render_template, redirect, request, url_for, flash, make_response, current_app
from ..models import FunPic
from flask_login import login_required, current_user
from . import funpic
from .. import db
from .forms import Funpic
from ..decorators import admin_required
from .spider import funny_pic_scheduler, girls_pic_scheduler


@funpic.route('/disable/<id>')
@login_required
@admin_required
def pic_disable(id):
    file = FunPic.query.get_or_404(id)
    file.disabled = True
    db.session.add(file)
    db.session.commit()
    return redirect(url_for('funpic.girls',
                            page=request.args.get('page', 1, type=int)))


@funpic.route('/enable/<id>')
@login_required
@admin_required
def pic_enable(id):
    file = FunPic.query.get_or_404(id)
    file.disabled = False
    db.session.add(file)
    db.session.commit()
    return redirect(url_for('funpic.girls',
                            page=request.args.get('page', 1, type=int)))


@funpic.route('/', methods=['GET', 'POST'])
def index():
    form = Funpic()
    if form.validate_on_submit():
        girls_pic_scheduler()
        funny_pic_scheduler()
        redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_girl = bool(request.cookies.get('show_girls', ''))
    if show_girl:
        query = FunPic.query.filter_by(info='good').filter_by(type='girls')
    else:
        query = FunPic.query.filter_by(info='good').filter_by(type='funny')
    pagination = query.order_by(FunPic.timestamp.desc()).paginate(
        page, per_page=current_app.config['PIC_PER_PAGE'],
        error_out=False)
    links = pagination.items
    return render_template('funpic/funpic.html',
                           form=form,
                           links=links,
                           show_girls=show_girl,
                           pagination=pagination)


@funpic.route('/funny')
def show_funny():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_girls', '', max_age=30*24*60*60)
    return resp


@funpic.route('/girls')
def show_girls():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_girls', '1', max_age=30*24*60*60)
    return resp
