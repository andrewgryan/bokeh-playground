import bokeh.plotting
import bokeh.models
import bokeh.layouts
import os
from tinydb import TinyDB, Query
from passlib.hash import sha256_crypt


USER_DB = os.path.join(os.path.dirname(__file__), "user.db")


class Survey(object):
    def __init__(self):
        self.column = bokeh.layouts.column(
                sizing_mode='scale_width')
        self.login_page()
        self.exit = bokeh.models.Button(label="Exit survey")
        self.exit.on_click(self.on_exit)

    def login_page(self):
        self.user_name = bokeh.models.TextInput(
                title="User:")
        self.password = bokeh.models.PasswordInput(
                title="Password:")
        self.register = bokeh.models.Button(
                label="Register")
        self.register.on_click(self.on_register)
        self.login = bokeh.models.Button(
                label="Login")
        self.login.on_click(self.on_login)
        self.message = bokeh.models.Div()
        self.column.children = [
                self.user_name,
                self.password,
                bokeh.layouts.row(self.register, self.login),
                self.message
        ]

    def on_register(self):
        with TinyDB(USER_DB) as db:
            users = db.search(Query().name == self.user_name.value)
            if len(users) > 0:
                user = users[0]
                self.message.text = "User name already taken"
            else:
                db.insert({
                    "name": self.user_name.value,
                    "password": sha256_crypt.encrypt(self.password.value)})
                self.start_survey()

    def on_login(self):
        with TinyDB(USER_DB) as db:
            users = db.search(Query().name == self.user_name.value)
            if len(users) > 0:
                user = users[0]
                if not sha256_crypt.verify(self.password.value, user['password']):
                    self.message.text = "Incorrect password"
                else:
                    self.start_survey()
            else:
                self.message.text = "Unrecognised user name, please register"

    def start_survey(self):
        self.questions = []
        for text in [
                "What day is it today?",
                "What's the weather like outside?",
                "Are those my feet?"]:
            question = bokeh.models.TextInput(title=text)
            question.on_change("value", self.validate)
            self.questions.append(question)
        submit = bokeh.models.Button(label="Submit")
        submit.on_click(self.on_submit)
        self.column.children = self.questions + [
                bokeh.layouts.row(self.exit, submit)]

    def on_exit(self):
        self.login_page()

    def on_submit(self):
        self.column.children = [bokeh.models.Div(text="Saving...")]
        document = bokeh.plotting.curdoc()
        document.add_timeout_callback(self.on_complete, 1000)

    def on_complete(self):
        self.column.children = [
                bokeh.models.Div(text="Thank you"),
                self.exit
        ]

    def validate(self, attr, old, new):
        pass


def main():
    survey = Survey()
    document = bokeh.plotting.curdoc()
    document.add_root(survey.column)


if __name__.startswith('bk'):
    main()
