from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, TextAreaField, SelectField, BooleanField, IntegerField, DateField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class OrderForm(FlaskForm):
    customer_name = StringField('Customer Name', validators=[DataRequired()])
    menu_items = SelectMultipleField('Menu Items', validators=[DataRequired()], coerce=int)
    staff_id = SelectField('Staff Member', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Create Order')

class MenuItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', choices=[
        ('coffee', 'Coffee'),
        ('tea', 'Tea'),
        ('pastry', 'Pastry'),
        ('sandwich', 'Sandwich'),
        ('dessert', 'Dessert')
    ], validators=[DataRequired()])
    available = BooleanField('Available')
    submit = SubmitField('Add Menu Item')

class InventoryForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('beans', 'Coffee Beans'),
        ('milk', 'Milk'),
        ('syrups', 'Syrups'),
        ('tea', 'Tea'),
        ('pastry', 'Pastry Ingredients'),
        ('packaging', 'Packaging'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    unit = StringField('Unit', validators=[DataRequired()])
    reorder_level = FloatField('Reorder Level', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Item')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[
        ('staff', 'Staff'),
        ('manager', 'Manager'),
        ('admin', 'Admin')
    ], validators=[DataRequired()])
    submit = SubmitField('Create User')

class StaffForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    position = SelectField('Position', choices=[
        ('barista', 'Barista'),
        ('cashier', 'Cashier'),
        ('manager', 'Manager'),
        ('chef', 'Chef'),
        ('cleaner', 'Cleaner')
    ], validators=[DataRequired()])
    contact = StringField('Contact Number', validators=[DataRequired()])
    staff_id = StringField('Staff ID', render_kw={'readonly': True})
    active = BooleanField('Active')
    submit = SubmitField('Add Staff Member')