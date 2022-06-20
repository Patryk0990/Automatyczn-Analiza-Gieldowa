from flask import render_template, redirect, url_for, request, flash, session
from User.user_manager import UserManager
from Stock.stock_chart import StockChart
from Stock.stock_manager import StockManager
from datetime import datetime


class Routes:

    @staticmethod
    def render_index_view():
        if session.get('user'):
            return redirect(url_for('dashboard'))

        if request.method == 'POST' and 'register' in request.form:
            email = request.form.get('email', '').strip()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            password_repetition = request.form.get('password_repetition', '').strip()
            failed_validations = 0

            # Email not validated
            if not UserManager.validate_email(email):
                flash("Incorrect e-mail address.", "warning")
                failed_validations += 1

            # Username not validated
            if not UserManager.validate_username(username):
                flash("Incorrect username.\nUsername should contain 6-32 characters. Allowed characters are:\nlowercase and uppercase letters,\nnumbers,\nspecial characters (@#$%^&+=!.-_).", "warning")
                failed_validations += 1

            # Passwords not matching
            if password != password_repetition:
                flash("The passwords given differ.", "warning")
                failed_validations += 1

            # Password not validated
            if not UserManager.validate_password(password):
                flash("Incorrect password.\nPassword should contain 8-100 characters including at least:\n1 lower case letter,\n1 upper case letter,\n1 number,\n1 special character (@#$%^&+=!.-_).", "warning")
                failed_validations += 1

            if failed_validations != 0:
                return render_template('index.html')

            if UserManager.get_user_by_username(username) is not None:
                flash("A user with the specified name already exists.", "warning")
                return render_template('index.html')

            if UserManager.get_user_by_email(email) is not None:
                flash("A user with the specified e-mail already exists.", "warning")
                return render_template('index.html')

            if UserManager.create_user(username, email, password):
                flash("Registration successfully completed.", "success")
            else:
                flash("An unknown error has occurred while trying to register.\nPlease try again later.", "warning")

        elif request.method == 'POST' and 'login' in request.form:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            if UserManager.get_user_by_username(username):
                user = UserManager.authenticate_user(username, password)
                if user is None:
                    flash("Incorrect password.", "warning")
                else:
                    ui_settings = UserManager.get_user_interface_settings(user.get('id'))
                    u_api_settings = UserManager.get_user_api_settings(user.get('id'))

                    if ui_settings is None or u_api_settings is None:
                        flash("An error occurred while retrieving user settings from the database. Please try again later.", "warning")
                    else:
                        session['user'] = user
                        session['user']['interface_settings'] = ui_settings
                        session['user']['api_settings'] = u_api_settings
                        return redirect(url_for('dashboard'))

            else:
                flash("The user with the specified name does not exist.", "warning")

        return render_template('index.html')

    @staticmethod
    def render_dashboard_view():
        if session.get('user'):
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )
            positions = None
            news = StockManager.get_rest_api_connection().get_news()
            if user.is_privileged():
                rest_api = StockManager.get_rest_api_connection(
                    session.get('user').get('api_settings').get('apca_api_key_id'),
                    session.get('user').get('api_settings').get('apca_api_secret_key')
                )
                if rest_api.get_account():
                    positions = rest_api.list_positions()
                for index in range(len(positions)):
                    positions[index] = {
                        'symbol': positions[index]['symbol'],
                        'quantity': positions[index]['qty'],
                        'entry_price': positions[index]['avg_entry_price'],
                        'current_price': positions[index]['current_price']
                    }
            for index in range(len(news)):
                news[index] = news[index]._raw
                news[index] = {"title": news[index]['headline'],
                               "update_time": datetime.strptime(news[index]['updated_at'], '%Y-%m-%dT%H:%M:%SZ').strftime("%d/%m/%Y %H:%M:%S"),
                               "link": news[index]['url']}

            return render_template('User/dashboard.html', user=user, ui_settings=session.get('user').get('interface_settings'), positions=positions, news=news)
        flash("Unauthorised access attempt.", "warning")
        return redirect(url_for('index'))

    @staticmethod
    def render_manage_users_view():
        if session.get('user'):
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )
            users = UserManager.get_users()
            users.remove({
                'id': session.get('user').get('id'),
                'username': session.get('user').get('username'),
                'permission_level': session.get('user').get('permission_level'),
                'active': session.get('user').get('active')
            })
            if user.is_superuser():
                return render_template('Admin/manage_users.html', user=user, ui_settings=session.get('user').get('interface_settings'), users=users)
        flash("Unauthorised access attempt.", "warning")
        return redirect(url_for('index'))

    @staticmethod
    def render_modify_user_view():
        if session.get('user'):
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )
            if user.is_superuser():
                if request.args.get('id'):
                    user_id = request.args.get('id')
                    if request.method == 'POST':

                        update_dictionary = {
                            'active': True
                        }
                        for k, v in request.form.items():
                            update_dictionary[k] = v.strip()

                        password = update_dictionary.get('password', '')
                        password_repetition = update_dictionary.get('password_repetition', '')
                        del update_dictionary['password']
                        del update_dictionary['password_repetition']
                        failed_validations = 0

                        # Username not validated
                        if update_dictionary.get('username') and not UserManager.validate_username(update_dictionary.get('username')):
                            flash(
                                "Incorrect username.\nUsername should contain 6-32 characters. Allowed characters are:\nlowercase and uppercase letters,\nnumbers,\nspecial characters (@#$%^&+=!.-_).",
                                "warning")

                            failed_validations += 1

                        if password or password_repetition:
                            # Passwords not matching
                            if password != password_repetition:
                                flash("The passwords given differ.", "warning")
                                failed_validations += 1

                            # Password not validated
                            if not UserManager.validate_password(password):
                                flash(
                                    "Incorrect password.\nPassword should contain 8-100 characters including at least:\n1 lower case letter,\n1 upper case letter,\n1 number,\n1 special character (@#$%^&+=!.-_).",
                                    "warning")

                                failed_validations += 1

                        if failed_validations == 0:
                            if UserManager.update_user(user_id, **update_dictionary):
                                flash("Successfully updated data.", "success")
                            else:
                                flash("Unknown error while trying to update data.", "warning")
                            return redirect(url_for('manage_users'))
                    result = UserManager.get_user_by_id(user_id)
                    if result:
                        return render_template(
                            'Admin/modify_user.html',
                            user=user,
                            ui_settings=session.get('user').get('interface_settings'),
                            user_to_modify={
                                'id': result[0],
                                'username': result[2],
                                'permission_level': result[4],
                                'active': result[5]
                            }
                        )
                flash("Unauthorised access attempt. Unspecified user to modify.", "warning")
                return redirect(url_for('manage_users'))
        flash("Unauthorised access attempt.", "warning")
        return redirect(url_for('index'))

    @staticmethod
    def render_update_user():
        if session.get('user'):
            user_id = request.args.get('user_id')
            request.args.pop('user_id')
            if UserManager.update_user(user_id, **request.args.to_dict()):
                flash("Successfully updated data.", "success")
            else:
                flash("Unknown error while trying to update data.", "warning")
        return redirect(url_for('index'))

    @staticmethod
    def render_change_user_password_view():
        if session.get('user'):
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )

            if request.method == "POST":  # change password form
                old_password = request.form.get('old_password', '').strip()
                password = request.form.get('password', '').strip()
                password_repetition = request.form.get('password_repetition', '').strip()
                failed_validations = 0

                # Current password not matching
                if UserManager.authenticate_user(user.get_username(), old_password) is None:
                    flash("The wrong old password was given.", "warning")
                    failed_validations += 1

                # Passwords not matching
                if password != password_repetition:
                    flash("The passwords given differ.", "warning")
                    failed_validations += 1

                # Password not validated
                if not UserManager.validate_password(password):
                    flash(
                        "Incorrect password.\nPassword should contain 8-100 characters including at least:\n1 lower case letter,\n1 upper case letter,\n1 number,\n1 special character (@#$%^&+=!.-_).",
                        "warning")

                    failed_validations += 1

                if failed_validations == 0:
                    if UserManager.update_user(user.get_id(), password=password):
                        flash("You have successfully changed your user password.", "success")
                    else:
                        flash("The wrong old password was given.", "warning")
            return render_template('User/change_password.html', user=user, ui_settings=session.get('user').get('interface_settings'))
        flash("Unauthorised access attempt.", "warning")
        return redirect(url_for('index'))

    @staticmethod
    def render_update_user_interface_settings():
        if session.get('user'):
            if UserManager.update_user_interface_settings(session.get('user').get('id'), **request.args.to_dict()):
                for key, value in request.args.items():
                    if value == 'True' or value == 'False':
                        session['user']['interface_settings'][key] = eval(value)
                    else:
                        session['user']['interface_settings'][key] = int(value)
                flash("Successfully updated data.", "success")
            else:
                flash("Unknown error while trying to update data.", "warning")
        return redirect(url_for('dashboard'))

    @staticmethod
    def render_change_user_api_settings():
        if session.get('user'):
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )
            if request.method == "POST":  # change password form
                u_api_new_settings = {
                    "apca_api_key_id": request.form.get('apca_api_key_id', '').strip(),
                    "apca_api_secret_key": request.form.get('apca_api_secret_key', '').strip()
                }
                if UserManager.update_user_api_settings(session.get('user').get('id'), **u_api_new_settings):
                    for key, value in u_api_new_settings.items():
                        session['user']['api_settings'][key] = value
                    flash("Successfully updated data.", "success")
                else:
                    flash("Unknown error while trying to update data.", "warning")
            return render_template(
                'User/change_alpaca_settings.html',
                user=user,
                ui_settings=session.get('user').get('interface_settings'),
                u_api_settings=session.get('user').get('api_settings')
            )
        flash("Unauthorised access attempt.", "warning")
        return redirect(url_for('index'))

    @staticmethod
    def render_delete_user_view():
        if session.get('user'):
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )
            if user.is_superuser():
                if request.args.get('id'):
                    if request.method == "POST":
                        if UserManager.delete_user(request.args.get('id')):
                            flash("User successfully deleted.", "success")
                        else:
                            flash("Unknown error when trying to delete a user.", "warning")
                        return redirect(url_for('manage_users'))
                    user_to_delete = UserManager.get_user_by_id(request.args.get('id'))
                    return render_template(
                        'Admin/delete_user.html',
                        user=user,
                        ui_settings=session.get('user').get('interface_settings'),
                        user_to_delete_username=user_to_delete[2]
                    )
                flash("Unauthorized access attempt. Unspecified user to modify.", "warning")
                return redirect(url_for('manage_users'))
        flash("Unauthorised access attempt.", "warning")
        return redirect(url_for('index'))

    @staticmethod
    def render_stocks_view():
        if session.get('user'):
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )
            if user.is_privileged():
                try:
                    connection = StockManager.get_rest_api_connection(
                        session.get('user').get('api_settings').get('apca_api_key_id'),
                        session.get('user').get('api_settings').get('apca_api_secret_key')
                    )
                    if connection.get_account()['status'] == 'ACTIVE':
                        return render_template(
                            'Trade/view_stocks.html',
                            user=user,
                            ui_settings=session.get('user').get('interface_settings'),
                            u_api_connection_valid=True,
                        )
                except Exception as error:
                    print("Error while connecting user with Alpaca API", error)
                    flash("The access data to the Alpaca API is incorrect or the account is not active.", "warning")
            if user.is_authenticated():
                return render_template('Trade/view_stocks.html', user=user, ui_settings=session.get('user').get('interface_settings'))
            flash("Unauthorised access attempt.", "warning")
        return redirect(url_for('index'))

    @staticmethod
    def render_stocks_search():
        if session.get('user'):
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )
            if user.is_authenticated():
                return StockManager.search_stocks_by_name(request.form.get("name", ""))
        return "Unauthorised access attempt."

    @staticmethod
    def render_stocks_graph():
        if session.get('user'):
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )
            if user.is_authenticated():
                session['stock'] = StockChart(
                    StockManager.get_stock_by_symbol(request.form.get("symbol", ""))
                )

        return "Unauthorised access attempt."

    @staticmethod
    def render_update_stocks():
        if session.get('user'):
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )
            if user.is_superuser():
                if StockManager.update_stocks():
                    flash("Successfully updated data.", "success")
                else:
                    flash("Unknown error while trying to update data.", "warning")
                return redirect(url_for('dashboard'))
        flash("Unauthorised access attempt.", "warning")
        return redirect(url_for('index'))

    @staticmethod
    def render_logout_user():
        session.clear()
        flash("You have successfully logged out.", "success")
        return redirect(url_for('index'))

    @staticmethod
    def render_get_positions():
        if session.get('user'):
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )
            if user.is_privileged():
                rest_api = StockManager.get_rest_api_connection(
                    session.get('user').get('api_settings').get('apca_api_key_id'),
                    session.get('user').get('api_settings').get('apca_api_secret_key')
                )
                result = rest_api.list_positions()
                quantity = 0
                if request.args.get('symbol'):
                    for position in result:
                        if position['symbol'] == request.args.get('symbol'):
                            quantity += int(position['qty'])
                else:
                    for position in result:
                        quantity += int(position['qty'])

                return {
                    'message': 'OK',
                    'quantity': quantity
                }
        return {'message': 'Unauthorised access attempt.'}

    @staticmethod
    def render_get_account_budget():
        if session.get('user'):
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )
            if user.is_privileged():
                rest_api = StockManager.get_rest_api_connection(
                    session.get('user').get('api_settings').get('apca_api_key_id'),
                    session.get('user').get('api_settings').get('apca_api_secret_key')
                )
                buying_power = rest_api.get_account()['buying_power']
                cash = rest_api.get_account()['cash']
                return {
                    'message': 'OK',
                    'cash': cash,
                    'buying_power': buying_power
                }
        return {'message': 'Unauthorised access attempt.'}

    @staticmethod
    def render_buy_stocks():
        if session.get('user'):
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )
            if user.is_privileged():
                StockManager.buy_stocks(
                    request.args.get('symbol'),
                    request.args.get('quantity'),
                    session.get('user').get('api_settings').get('apca_api_key_id'),
                    session.get('user').get('api_settings').get('apca_api_secret_key')
                )
                return {
                    'message': 'Successfully bought stock.'
                }
        return {'message': 'Unauthorised access attempt.'}

    @staticmethod
    def render_sell_stocks():
        if session.get('user'):
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )
            if user.is_privileged():
                StockManager.sell_stocks(
                    request.args.get('symbol'),
                    request.args.get('quantity'),
                    session.get('user').get('api_settings').get('apca_api_key_id'),
                    session.get('user').get('api_settings').get('apca_api_secret_key')
                )
                return {'message': 'Successfully sold stock.'}
        return {'message': 'Unauthorised access attempt.'}
