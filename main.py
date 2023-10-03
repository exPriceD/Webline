from flask import render_template, request, jsonify, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from flask_login import login_user, login_required, current_user, logout_user
from config import application, login_manager, mail
from models import db, Orders, Users, Requests, PaymentRequests, Promocodes, ModeratorRequests
import datetime
from threading import Thread


@login_manager.user_loader
def load_user(user_id):
    return Users.query.filter_by(id=user_id).first()


"""@application.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r"""


@application.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        form = request.form.to_dict()
        if form and form["name"] and form["company"] and form["phone"] and form["email"] and form["message"]:
            dt_now = str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
            client_request = Requests(
                status='Рассмотрение', date=dt_now, name=form["name"], email=form["email"],
                phone=form["phone"],company=form["company"], message=form["message"]
            )
            db.session.add(client_request)
            db.session.flush()
            db.session.commit()
            subject = f"Заявка от пользователя"
            body = f'Дата: {dt_now}\nИмя: {form["name"]}\nEmail: {form["email"]}\nТелефон: {form["phone"]}\n'
            body += f'Компания: {form["company"]}\nСообщение: {form["message"]}'
            send_mail(subject=subject, recipient="weblinecompany@mail.ru", body=body)
            return jsonify({'message': "Success"})
    return render_template('index.html')


@application.route('/en', methods=["POST", "GET"])
def index_en():
    if request.method == "POST":
        form = request.form.to_dict()
        if form and form["name"] and form["company"] and form["phone"] and form["email"] and form["message"]:
            dt_now = str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
            client_request = Requests(
                status='Рассмотрение',
                date=dt_now,
                name=form["name"],
                email=form["email"],
                phone=form["phone"],
                company=form["company"],
                message=form["message"]
            )
            db.session.add(client_request)
            db.session.flush()
            db.session.commit()
            return jsonify({'message': "Success"})
    return render_template('index_en.html')


@application.route('/orders')
@login_required
def orders():
    user_role = current_user.role
    user_id = current_user.id
    user_orders = []
    active_requests = []
    ended_requests = []
    if current_user.role == 'Администратор':
        consideration_moderator_requests = ModeratorRequests.query.filter_by(status="Рассмотрение").all()
        ended_moderator_requests = list(reversed(ModeratorRequests.query.filter_by(status="Завершена").all()))
        return render_template(
            'orders.html',
            user=current_user,
            consideration_moderator_requests=consideration_moderator_requests,
            ended_moderator_requests=ended_moderator_requests
        )
    if user_role == 'Заказчик':
        user_orders = list(reversed(Orders.query.filter_by(client_id=current_user.login).all()))
    if user_role == 'Модератор' or user_role == 'Администратор':
        user_orders = list(reversed(Orders.query.filter_by(moderator_id=user_id).all()))
    if user_role == 'Frontend-developer':
        user_orders = list(reversed(Orders.query.filter_by(frontend_id=user_id).all()))
    if user_role == 'Backend-developer':
        user_orders = list(reversed(Orders.query.filter_by(backend_id=user_id).all()))
    ended = []
    active = []
    if user_orders:
        for order in user_orders:
            if order.status == 'Завершен':
                ended.append(order)
            else:
                active.append(order)
    return render_template(
        'orders.html',
        user=current_user,
        active_orders=active,
        active_requests=active_requests,
        ended_orders=ended,
        ended_requests=ended_requests
    )


@application.route('/orders/add', methods=["POST", "GET"])
@login_required
def add_order():
    if current_user.role != 'Модератор' and current_user.role != 'Администратор':
        return ''
    if request.method == "POST":
        form = request.form.to_dict()
        if form and form["title"] and form["description"] and form["client_login"]:
            client = Users.query.filter_by(login=form["client_login"]).first()
            if not(client):
                return jsonify({'Status': "Client not found"})
            admin_payment = ''
            moderator_payment = ''
            designer_payment = ''
            frontend_payment = ''
            backend_payment = ''
            if form["price"]:
                admin_payment = str(int(form["price"]) * 0.05),
                moderator_payment = str(int(form["price"]) * 0.05),
                designer_payment = str(int(form["price"]) * 0.25),
                frontend_payment = str(int(form["price"]) * 0.25),
                backend_payment = str(int(form["price"]) * 0.25)
            dt_now = str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
            client_order = Orders(
                client_id=form["client_login"],
                title=form["title"],
                description=form["description"],
                price=form["price"],
                status="Рассмотрение",
                payment_status="Ожидает оплаты",
                date=dt_now,
                deadline=form['deadline'],
                url=form['url'],
                git=form['github'],
                figma=form['figma'],
                other=form['other'],
                moderator_id=current_user.id,
                admin_payment=admin_payment,
                moderator_payment=moderator_payment,
                designer_payment=designer_payment,
                frontend_payment=frontend_payment,
                backend_payment=backend_payment
            )
            db.session.add(client_order)
            db.session.flush()
            db.session.commit()
            return jsonify({'Status': "Success"})
    return render_template('add_order.html', user=current_user)


@application.route('/orders/<id>')
@login_required
def detailed(id):
    moderator = False
    design = False
    frontend_developer = False
    backend_developer = False
    order = Orders.query.filter_by(id=id).first()
    client = Users.query.filter_by(login=order.client_id).first()
    designers_list = []
    frontend_developers_list = []
    backend_developers_list = []
    moderator_requests = list(reversed(ModeratorRequests.query.filter_by(order_id=id).all()))
    if order:
        if order.moderator_id:
            moderator = Users.query.filter_by(id=int(order.moderator_id)).first()
        if order.design_id:
            design = Users.query.filter_by(id=int(order.design_id)).first()
        if order.frontend_id:
            frontend_developer = Users.query.filter_by(id=int(order.frontend_id)).first()
        if order.backend_id:
            backend_developer = Users.query.filter_by(id=int(order.backend_id)).first()
        designers_list = Users.query.filter_by(role='Дизайнер').all()
        designers_list.extend(Users.query.filter_by(role='Моушн-дизайнер').all())
        frontend_developers_list = Users.query.filter_by(role='Frontend-developer').all()
        backend_developers_list = Users.query.filter_by(role='Backend-developer').all()
        fullstack_developers_list = Users.query.filter_by(role='Fullstack-developer').all()
        frontend_developers_list.extend(fullstack_developers_list)
        backend_developers_list.extend(fullstack_developers_list)
        print(frontend_developers_list)
    return render_template(
        'order_details.html',
        order=order,
        user=current_user,
        moderator=moderator,
        design=design,
        frontend_developer=frontend_developer,
        backend_developer=backend_developer,
        client=client,
        frontend_developers_list=frontend_developers_list,
        backend_developers_list=backend_developers_list,
        designers_list=designers_list,
        moderator_requests=moderator_requests
    )


@application.route('/orders/update/executor', methods=["POST", "GET"])
def update_executor():
    if current_user.role != 'Модератор' and current_user.role != 'Администратор':
        return ''
    if request.method == "POST":
        form = request.form.to_dict()
        if form:
            print(form)
            order = Orders.query.filter_by(id=int(form["order_id"])).first()
            if form['executor_role'] == 'Frontend-developer':
                order.frontend_id = form['executor_id']
            if form['executor_role'] == 'Backend-developer':
                order.backend_id = form['executor_id']
            if form['executor_role'] == 'Designer' or form['executor_role'] == 'Моушн-дизайнер':
                order.design_id = form['executor_id']
            db.session.commit()
            return jsonify({'status': 'Success'})
    return ''


@application.route('/orders/<id>/update/payments', methods=["POST", "GET"])
def update_payments(id):
    if current_user.role != 'Модератор' and current_user.role != 'Администратор':
        return ''
    if request.method == "POST":
        form = request.form.to_dict()
        if not(form):
            return jsonify({'status': 'Not form'})
        order = Orders.query.filter_by(id=id).first()
        order.moderator_payment = form['moderator_payment']
        order.designer_payment = form['designer_payment']
        order.frontend_payment = form['frontend_payment']
        order.backend_payment = form['backend_payment']
        db.session.commit()
        return jsonify({'status': 'Success'})


@application.route('/orders/<id>/update/end', methods=["POST", "GET"])
def end_order(id):
    if current_user.role != 'Администратор':
        return ''
    if request.method == 'POST':
        order = Orders.query.filter_by(id=id).first()
        order.status = 'Завершен'
        moderator = Users.query.filter_by(id=int(order.moderator_id)).first()
        moderator.balance = str(int(moderator.balance) + int(order.moderator_payment))
        if order.frontend_id:
            frontend_developer = Users.query.filter_by(id=int(order.frontend_id)).first()
            frontend_developer.balance = str(int(frontend_developer.balance) + int(order.frontend_payment))
        if order.backend_id:
            backend_developer = Users.query.filter_by(id=int(order.backend_id)).first()
            backend_developer.balance = str(int(backend_developer.balance) + int(order.backend_payment))
        if order.design_id:
            designer = Users.query.filter_by(id=int(order.design_id)).first()
            designer.balance = str(int(designer.balance) + int(order.designer_payment))
        db.session.commit()
        return jsonify({'status': 'Success'})
    return ''

@application.route('/orders/delete/executor', methods=["POST", "GET"])
def delete_executor():
    if current_user.role != 'Модератор' and current_user.role != 'Администратор':
        return ''
    if request.method == "POST":
        form = request.form.to_dict()
        if form:
            print(form)
            order = Orders.query.filter_by(id=int(form["order_id"])).first()
            if form['executor_role'] == 'Frontend-developer':
                order.frontend_id = ''
            if form['executor_role'] == 'Backend-developer':
                order.backend_id = ''
            if form['executor_role'] == 'Designer' or form['executor_role'] == 'Моушн-дизайнер':
                order.design_id = ''
            db.session.commit()
            return jsonify({'status': 'Success'})
    return ''


@application.route('/requests/<id>')
@login_required
def request_detailed(id):
    if current_user.role != 'Модератор' and current_user.role != 'Администратор':
        return ''
    req = Requests.query.filter_by(id=id).first()
    return render_template('user_requests_details.html', request=req, user=current_user)


@application.route('/requests/<id>/accept', methods=["POST", "GET"])
@login_required
def accept_user_request(id):
    if current_user.role != "Модератор" and current_user.role != "Администратор":
        return ''
    if request.method == "POST":
        r = Requests.query.filter_by(id=int(id)).first()
        r.status = "Принята"
        r.moderator_id = current_user.id
        db.session.commit()
        return jsonify({"Status": "Success"})
    return ''


@application.route('/requests/<id>/end', methods=["POST", "GET"])
@login_required
def end_user_request(id):
    if current_user.role != "Модератор" and current_user.role != "Администратор":
        return ''
    if request.method == "POST":
        r = Requests.query.filter_by(id=int(id)).first()
        r.status = "Завершена"
        db.session.commit()
        return jsonify({"Status": "Success"})
    return ''


@application.route('/create_user', methods=["POST", "GET"])
@login_required
def create_user():
    if current_user.role != 'Модератор' and current_user.role != 'Администратор':
        return ''
    if request.method == "POST":
        form = request.form.to_dict()
        if form and form["role"] and form["login"] and form["username"] and form["password"]:
            if not(check_users(form["login"])):
                return jsonify({'Status': 'Login already exist'})
            hash = generate_password_hash(password=form["password"])
            user = Users(
                username=request.form["username"],
                login=request.form["login"],
                password=hash,
                role=form["role"],
                email=form["email"],
                phone=form["phone"],
                telegram=form["telegram"],
                other=form["other"],
                balance='0'
            )
            print(f"{form['username']} зарегистрирован!")
            db.session.add(user)
            db.session.flush()
            db.session.commit()
            return jsonify({'Status': 'Success!'})
    return render_template('add_user.html', user=current_user)


@application.route('/withdrawal', methods=["POST", "GET"])
@login_required
def withdrawal():
    if current_user.role == 'Заказчик':
        return ''
    if request.method == "POST":
        form = request.form.to_dict()
        withdrawal_r = PaymentRequests.query.filter_by(user_id=current_user.id).all()
        if withdrawal_r:
            for r in withdrawal_r:
                if r.status == "Рассмотрение":
                    return jsonify({"Status": "Previously submitted application"})
        if int(form["amount"]) > int(current_user.balance):
            return jsonify({"Status": "Not enough money"})
        if form and form["amount"] and form["details"]:
            dt_now = str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
            payment = PaymentRequests(
                user_id=current_user.id,
                status='Рассмотрение',
                date=dt_now,
                name=current_user.username,
                phone=current_user.phone,
                email=current_user.email,
                telegram=current_user.telegram,
                role=current_user.role,
                amount=form["amount"],
                details=form["details"]
            )
            db.session.add(payment)
            db.session.flush()
            db.session.commit()
            return jsonify({"Status": "Success"})
    return render_template('withdrawal.html', user=current_user)


@application.route('/login', methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect("/orders")
    if request.method == "POST":
        form = request.form.to_dict()
        if form and form["login"] and form["password"]:
            user = Users.query.filter_by(login=request.form["login"]).first()
            if not user:
                return jsonify({'status': 'User not found!'})
            else:
                if check_password_hash(pwhash=user.password, password=request.form["password"]):
                    login_user(user, remember=True, duration=datetime.timedelta(days=365))
                    return jsonify({'status': 'Success!'})
                else:
                    return jsonify({'status': 'Incorrect password!'})
    return render_template('vxod.html')


@application.route('/orders/payments')
@login_required
def payments():
    if current_user.role != 'Администратор':
        return ''
    consideration = PaymentRequests.query.filter_by(status="Рассмотрение").all()
    accepted = PaymentRequests.query.filter_by(status="Принята").all()
    rejected = PaymentRequests.query.filter_by(status="Отклонена").all()
    ended = accepted + rejected
    return render_template('payments.html', consideration=consideration, ended=ended, user=current_user)


@application.route('/orders/payments/<id>')
@login_required
def payments_details(id):
    if current_user.role != 'Администратор':
        return ''
    payment = PaymentRequests.query.filter_by(id=id).first()
    withdrawal_user = Users.query.filter_by(id=int(payment.user_id)).first()
    if not(withdrawal_user):
        return '<h3>Заявка не найдена</h3>'
    page = "Consideration"
    if payment.status == "Принята" or payment.status == "Отклонена":
        page = "Ended"
    return render_template(
        'payments_details.html', withdrawal_user=withdrawal_user,
        payment=payment, user=current_user,page=page
    )


@application.route('/orders/payments/ended/<id>')
def ended_payment(id):
    if current_user.role != 'Администратор':
        return ''
    payment = PaymentRequests.query.filter_by(id=id).first()
    withdrawal_user = Users.query.filter_by(id=int(payment.user_id)).first()
    return render_template(
        'payments_details.html', payment=payment,
        user=current_user, page="Ended", withdrawal_user=withdrawal_user)


@application.route('/orders/update/payment', methods=["POST", "GET"])
@login_required
def update_payment():
    if current_user.role != 'Модератор' and current_user.role != 'Администратор':
        return ''
    if request.method == "POST":
        form = request.form.to_dict()
        if form and form['payment_status'] and form['order_id']:
            order = Orders.query.filter_by(id=form['order_id']).first()
            order.payment_status = form['payment_status']
            db.session.commit()
            return jsonify({'Status': 'success'})
    return ''


@application.route('/orders/update/work', methods=["POST", "GET"])
@login_required
def update_work():
    if current_user.role != 'Модератор' and current_user.role != 'Администратор':
        return ''
    if request.method == "POST":
        form = request.form.to_dict()
        if form and form['work_status'] and form['order_id']:
            order = Orders.query.filter_by(id=form['order_id']).first()
            order.status = form['work_status']
            db.session.commit()
            return jsonify({'Status': 'success'})
    return ''


@application.route('/requests')
@login_required
def req():
    if current_user.role != 'Модератор' and current_user.role != 'Администратор':
        return ''
    user_role = current_user.role
    active_requests = []
    ended_requests = []
    if user_role == 'Модератор' or user_role == 'Администратор':
        my_requests = []
        moderator_request = list(reversed(Requests.query.filter_by(moderator_id=current_user.id).all()))
        for r in moderator_request:
            if r.status == "Принята":
                my_requests.append(r)
        active_requests = list(reversed(Requests.query.filter_by(status="Рассмотрение").all()))
        ended_requests = Requests.query.filter_by(status="Завершена").all()
    return render_template(
        'user_requests.html', my_requests=my_requests,
        active_requests=active_requests, ended_requests=ended_requests,
        user=current_user
    )


@application.route('/orders/edit/<id>', methods=["POST", "GET"])
@login_required
def edit_order(id):
    if current_user.role == 'Заказчик':
        return ''
    order = Orders.query.filter_by(id=id).first()
    if request.method == "POST":
        form = request.form.to_dict()
        if form:
            order.title = form['title']
            order.description = form['description']
            order.price = form['price']
            order.deadline = form['deadline']
            order.client_id = form['client_login']
            order.url = form['url']
            order.git = form['github']
            order.figma = form['figma']
            order.other = form['other']
            db.session.commit()
            return jsonify({'Status': 'Success'})
    return render_template('edit_order.html', order=order, user=current_user)


@application.route("/withdrawal/update", methods=["POST", "GET"])
@login_required
def change_payment_status():
    if current_user.role != 'Администратор':
        return ''
    if request.method == "POST":
        form = request.form.to_dict()
        if form:
            payment = PaymentRequests.query.filter_by(id=int(form["id"])).first()
            payment.status = form["status"]
            if form["status"] == "Отклонена":
                if not(form["comment"]):
                    return jsonify({"Status": "No comment"})
                payment.comment = form["comment"]
                db.session.commit()
                return jsonify({"Status": "Success"})
            user = Users.query.filter_by(id=int(form["user_id"])).first()
            if (int(user.balance) - int(form["amount"])) < 0:
                return jsonify({"Status": "Balance under zero"})
            user.balance = str(int(user.balance) - int(form["amount"]))
            db.session.commit()
            return jsonify({"Status": "Success"})
    return ''


@application.route('/promocodes', methods=["POST", "GET"])
def create_promo():
    if current_user.role != 'Администратор':
        return ''
    if request.method == "POST":
        form = request.form.to_dict()
        if form and form['promocode'] and form['amount'] and form['expire_date'] and form['count_used']:
            finded = Promocodes.query.filter_by(promocode=form['promocode']).first()
            if finded:
                return jsonify({"Status": "Already exist"})
            promocode = Promocodes(promocode=form['promocode'], amount=form['amount'],
                                   expire_date=form['expire_date'], uses=form['count_used'])
            db.session.add(promocode)
            db.session.flush()
            db.session.commit()
            return jsonify({"Status": "Success"})
    return render_template('promocodes.html', user=current_user)


@application.route('/write/promo', methods=["POST", "GET"])
def check_promo():
    if request.method == "POST":
        form = request.form.to_dict()
        if form and form["promocode"]:
            promocode = Promocodes.query.filter_by(promocode=form["promocode"]).first()
            user = Users.query.filter_by(id=int(current_user.id)).first()
            if not promocode:
                return jsonify({"Status": "Promo not found", "Balance": f"{user.balance}"})
            dt_now = str(datetime.datetime.now().strftime("%Y-%m-%d"))
            expire_date = promocode.expire_date
            if expire_date:
                if dt_now > expire_date:
                    return jsonify({"Status": "Expired", "Balance": f"{user.balance}"})
            if int(promocode.uses) > 0:
                used_promo = user.used_promocodes
                if not(used_promo):
                    used_promo = ''
                used_promo = used_promo.split(',')
                if promocode.promocode in used_promo:
                    return jsonify({"Status": "Already used", "Balance": f"{user.balance}"})
                used_promo.append(promocode.promocode)
                user.used_promocodes = ','.join(used_promo)
                user.balance = str(int(user.balance) + int(promocode.amount))
                promocode.uses = str(int(promocode.uses) - 1)
                db.session.commit()
                return jsonify({"Status": "Success", "Balance": f"{user.balance}", "Amount":f"{promocode.amount}"})
            else:
                return jsonify({"Status": "Used", "Balance": f"{user.balance}"})
    return ''


@application.route('/admin/help', methods=["POST", "GET"])
def help():
    if current_user.role != 'Модератор':
        return ''
    if request.method == "POST":
        form = request.form.to_dict()
        if form and form["comment"]:
            moderator = Users.query.filter_by(id=int(form["moderator_id"])).first()
            moder_request = ModeratorRequests(
                date=str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M")),
                status="Рассмотрение",
                moderator_id=moderator.id,
                moderator_name=moderator.username,
                order_id=int(form["order_id"]),
                comment=form["comment"],
                admin_name='',
                admin_comment='',
                answer_date=''

            )
            db.session.add(moder_request)
            db.session.flush()
            db.session.commit()
            return jsonify({"Status": "Success"})
    return ''


@application.route('/admin/help/accept/<id>', methods=["POST", "GET"])
def end_request(id):
    if current_user.role != 'Администратор':
        return ''
    if request.method == "POST":
        form = request.form.to_dict()
        if not(form):
            return jsonify({"Status": "Not form"})
        moder_request = ModeratorRequests.query.filter_by(id=int(id)).first()
        moder_request.status = "Завершена"
        moder_request.admin_id = int(current_user.id)
        moder_request.admin_name = current_user.username
        moder_request.admin_comment = form["admin_comment"] if form["admin_comment"] else '-'
        moder_request.answer_date = str(datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
        db.session.commit()
        return jsonify({"Status": "Success"})
    return ''


@application.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


def check_users(login):
    if Users.query.filter_by(login=login).all():
        return False
    return True


def async_send_mail(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(subject: str, recipient: str, body: str, **kwargs):
    msg = Message(subject, body=body, sender=application.config['MAIL_DEFAULT_SENDER'], recipients=[recipient])
    thr = Thread(target=async_send_mail,  args=[application,  msg])
    thr.start()
    return thr


if __name__ == "__main__":
    application.debug = True
    application.run()
    with application.app_context():
        db.create_all()

