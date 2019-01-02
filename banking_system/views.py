from flask import request
from flask import session, jsonify
from werkzeug.security import check_password_hash

from banking_system import app
from .models import Account_1, Transaction_1, Deposit_1, Withdraw_1, db


@app.route('/')
def index():
    session.clear()
    return '<h1>welcome to online banking</h1>'


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    id = request.json.get('id')
    name = request.json.get('name')
    password = request.json.get('password')
    if request.json.get('balance') > 0:
        balance = request.json.get('balance')
    else:
        balance = 0
    if Account_1.query.filter_by(id=id).first():
        return jsonify({id: 'already existed'})
    else:
        new_account = Account_1(id, name, password, balance)
        db.session.add(new_account)
        db.session.commit()
        new_transaction = Transaction_1('deposit', 'account opening', new_account.id, balance)
        new_deposit = Deposit_1('account opening', new_account.id, balance)
        db.session.add(new_transaction)
        db.session.add(new_deposit)
        db.session.commit()
        return jsonify({new_account.id: 'successfully registered'})


@app.route('/login', methods=['GET', 'POST'])
def login():
    id = request.json.get('id')
    password = request.json.get('password')
    account = Account_1.query.get(id)
    if check_password_hash(account.password, password):
        session['username'] = account.name
        session['id'] = account.id
        return jsonify({'welcome': account.id})
    else:
        return '<h1>Invalid Account ID & Password combination</h1>'


@app.route('/logout', methods=['GET'])
def logout():
    session['username'] = None
    return '<h1>successfully logged out</h1>'


@app.route('/json/account/name/<name>')
def json_names(name):
    if Account_1.query.filter_by(name=name).first():
        return jsonify({'name': 'taken'})
    else:
        return jsonify({'name': 'available'})


@app.route('/json/account/id/<account_id>')
def json_account_id(account_id):
    if Account_1.query.filter_by(id=account_id).first():
        return jsonify({'account': 'valid account ID'})
    else:
        return jsonify({'account': 'invalid account ID'})


@app.route('/my_deposit', methods=['GET', 'POST'])
def my_deposit():
    if session['username'] is None:
        return '<h1>login required</h1>'
    user = session['username']
    account = Account_1.query.filter_by(name=user).first()
    id = account.id
    amount = request.json.get('amount')
    account = Account_1.query.get(id)
    if amount >= 0:
        new_transaction = Transaction_1('deposit', 'self deposit', account.id, amount)
        new_deposit = Deposit_1('self deposit', account.id, amount)
        account.balance += amount
        db.session.add(new_transaction)
        db.session.add(new_deposit)
        db.session.commit()
        return '<h1>deposit added</h1>'
    else:
        return '<h1>deposit amount should be +ve</h1>'


@app.route('/my_withdraw', methods=['GET', 'POST'])
def my_withdraw():
    if session['username'] is None:
        return jsonify({'account': 'login required'})
    user = session['username']
    account = Account_1.query.filter_by(name=user).first()
    id = account.id
    amount = request.json.get('amount')
    account = Account_1.query.get(id)
    new_transaction = Transaction_1('withdraw', 'self withdraw', account.id, (amount * (-1)))
    new_withdraw = Withdraw_1('self withdraw', account.id, (amount * (-1)))
    if account.balance >= amount:
        account.balance += (amount * (-1))
        db.session.add(new_transaction)
        db.session.add(new_withdraw)
        db.session.commit()
        return '<h1>withdraw successful</h1>'
    else:
        return '<h1>withdraw not possible, low balance</h1>'


@app.route('/my_transfer', methods=['GET', 'POST'])
def my_transfer():
    if session['username'] is None:
        return jsonify({'account': 'login required'})
    user = session['username']
    account = Account_1.query.filter_by(name=user).first()
    id = account.id
    amount = request.json.get('amount')
    account_id = request.json.get('account_id')
    password = request.json.get('password')
    account = Account_1.query.get(id)
    if check_password_hash(account.password, password):
        if session['username'] is None:
            return jsonify({'account': 'login required'})
        new_transaction = Transaction_1('transfer out', f'transfer to account {account_id}', account.id,
                                        (amount * (-1)))
        new_withdraw = Withdraw_1(f'transfer to account {account_id}', account.id,
                                  (amount * (-1)))
        if account.balance >= amount:
            account.balance += (amount * (-1))
            db.session.add(new_transaction)
            db.session.add(new_withdraw)
            recipient = Account_1.query.get(account_id)
            new_transaction2 = Transaction_1('transfer in', f'transfer from account {account.id}', account_id,
                                             amount)
            new_deposit = Deposit_1(f'transfer from account {account.id}', account_id,
                                    amount)
            recipient.balance += (amount)
            db.session.add(new_transaction2)
            db.session.add(new_deposit)
            db.session.commit()
            return '<h1>transfer successful</h1>'
        else:
            return '<h1>withdraw not possible, low balance</h1>'
    else:
        return '<h1>Invalid Account Password</h1>'
