import unittest

from flask import json
from flask_sqlalchemy import SQLAlchemy

from banking_system import app


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        db = SQLAlchemy(app)
        db.create_all()

    def register_user(self, id, name, password, balance):
        user_data = {'id': id, 'name': name, 'password': password, 'balance': balance}
        return self.app.post('/create_account', data=json.dumps(user_data), content_type='application/json')

    def login_user(self, id, password):
        user_data = {'id': id, 'password': password}
        return self.app.post('/login', data=json.dumps(user_data), content_type='application/json')

    def deposit_user(self, description, amount, account_id):
        user_data = {'description': description, 'amount': amount, 'account_id': account_id}
        return self.app.post('/my_deposit', data=json.dumps(user_data), content_type='application/json')

    def withdraw_user(self, description, amount, account_id):
        user_data = {'description': description, 'amount': amount, 'account_id': account_id}
        return self.app.post('/my_withdraw', data=json.dumps(user_data), content_type='application/json')

    def test_user_registration(self):
        res = self.register_user(13, 'sri13', 'test1234', 500)
        self.assertIn(b'successfully registered', res.data)
        self.assertEqual(res.status_code, 200)

    def test_user_registration_existing_user(self):
        user_data = {'id': 116, 'name': 'sri116', 'password': 'test1234', 'balance': 500}
        res = self.app.post('/create_account', data=json.dumps(user_data), content_type='application/json')
        self.assertIn(b'already existed', res.data)
        self.assertEqual(res.status_code, 200)

    def test_not_matched_login(self):
        not_a_user = {'id': 116, 'password': 'none'}
        res = self.app.post('/login', data=json.dumps(not_a_user), content_type='application/json')
        self.assertIn(b'Invalid Account ID & Password combination', res.data)
        self.assertEqual(res.status_code, 200)

    def test_user_login(self):
        login_res = self.login_user(116, 'test1234')
        self.assertIn(b'welcome', login_res.data)
        self.assertEqual(login_res.status_code, 200)

    def test_deposit(self):
        self.login_user(116, 'test1234')
        deposit_res = self.deposit_user('self deposit', 200, 116)
        self.assertIn(b'deposit added', deposit_res.data)
        self.assertEqual(deposit_res.status_code, 200)

    def test_withdraw(self):
        self.login_user(116, 'test1234')
        res = self.withdraw_user('self withdraw', 100, 116)
        self.assertIn(b'withdraw successful', res.data)
        self.assertEqual(res.status_code, 200)

    def test_withdraw_bal_check(self):
        self.login_user(116, 'test1234')
        res = self.withdraw_user('self withdraw', 8000, 116)
        self.assertIn(b'withdraw not possible, low balance', res.data)
        self.assertEqual(res.status_code, 200)

    def test_logout(self):
        res = self.app.get('/logout')
        self.assertIn(b'successfully logged out', res.data)
        self.assertEqual(res.status_code, 200)


if __name__ == '__main__':
    unittest.main()
