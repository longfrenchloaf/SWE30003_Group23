# artproject/app/features/order/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, HiddenField, IntegerField, SelectField, DateField, TimeField, DecimalField
from wtforms.validators import DataRequired, NumberRange, Optional, InputRequired

class BuyTicketForm(FlaskForm):
    selected_trip_id = RadioField('Select Trip', validators=[DataRequired(message="Please select a trip.")])
    payment_type = RadioField(
        'Payment Method',
        choices=[('card', 'Credit/Debit Card'), ('ewallet', 'E-Wallet')],
        validators=[DataRequired(message="Please select a payment method.")]
    )
    submit = SubmitField('Buy Ticket for Selected Trip & Pay')

class FindTicketForRescheduleForm(FlaskForm):
    order_id = StringField('Order ID', validators=[DataRequired(message="Please enter your Order ID.")])
    submit_find = SubmitField('Find My Ticket')

class RescheduleTicketForm(FlaskForm):
    order_id = HiddenField()
    original_line_item_id = HiddenField()
    original_trip_id = HiddenField() # To identify the original trip for seat increment
    selected_new_trip_id = RadioField(
        'Select New Trip',
        validators=[DataRequired(message="Please select a new trip to reschedule to.")]
    )
    submit_confirm = SubmitField('Confirm Reschedule to Selected Trip')

class BulkBuyMerchandiseForm(FlaskForm):
    # Quantities will be handled by request.form.get(f'quantity_{item_id}') in the route
    payment_type = RadioField(
        'Payment Method',
        choices=[('card', 'Credit/Debit Card'), ('ewallet', 'E-Wallet')],
        validators=[DataRequired(message="Please select a payment method.")]
    )
    submit = SubmitField('Buy Selected Items & Pay')

class FindOrderForm(FlaskForm):
    order_id = StringField('Order ID', validators=[DataRequired(message="Please enter your Order ID.")])
    submit_find = SubmitField('Find My Order')

class ConfirmCancellationForm(FlaskForm):
    order_id = HiddenField()
    submit_confirm = SubmitField('Confirm Cancellation')

class SingleItemBuyMerchandiseForm(FlaskForm):
    selected_merchandise_id = HiddenField()
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)], default=1)
    payment_type = RadioField(
        'Payment Method',
        choices=[('card', 'Card'), ('ewallet', 'E-Wallet')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Buy & Pay')