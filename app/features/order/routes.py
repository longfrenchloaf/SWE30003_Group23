# artproject/app/features/order/routes.py
from flask import render_template, redirect, url_for, flash, request, session
from . import order_bp
from .forms import (
    BuyTicketForm,
    FindTicketForRescheduleForm, RescheduleTicketForm,
    BulkBuyMerchandiseForm,
    FindOrderForm, ConfirmCancellationForm,
)
# Models and data_manager
from app.models.trip import Trip # Import Trip model - use object methods now
from app.models.order import Order, SalesLineItem # Use Order object methods now
from app.models.account import Account # Use Account object methods/class methods
from app.models.merchandise import Merchandise # Use Merchandise object methods/class methods
from app.models.enums import OrderStatus, PaymentStatus, TicketStatus # Use Enums for comparisons
from flask import get_flashed_messages # Import this for conditional flashing

# data_manager is still needed for generating unique IDs and potentially low-level file saving called by models
from app import data_manager
from app.auth_utils import login_required, get_current_user_id
from datetime import datetime, timezone


# --- Scenario 1: Buying a Ticket ---
@order_bp.route('/buy-ticket', methods=['GET', 'POST'])
@login_required
def buy_ticket():
    form = BuyTicketForm()
    current_user_id = get_current_user_id()

    # Use Trip model to get all trips as objects ---
    all_trips_objects = Trip.get_all() # Get list of Trip objects
    # Filter available trips (as objects)
    available_trips_for_selection = [
        trip for trip in all_trips_objects if trip and trip.available_seats > 0
    ]

    # Populate choices from Trip objects for display and selection
    # Use trip.id for value, and attributes for display string
    form.selected_trip_id.choices = [
        (trip.id, f"{trip.route} - {trip.date} {trip.time} (RM {trip.price:.2f}, Seats: {trip.available_seats})")
        for trip in available_trips_for_selection
    ] if available_trips_for_selection else []

    # Handle GET request with no available trips (check the list of objects)
    if request.method == 'GET' and not available_trips_for_selection and \
       not get_flashed_messages(category_filter=["warning", "danger", "info", "success"]):
        flash("Sorry, there are currently no trips available for booking.", "warning")

    if form.validate_on_submit():
        selected_trip_id_from_form = form.selected_trip_id.data
        payment_type = form.payment_type.data

        # --- Use Order factory method to create the order ---
        try:
            # create_ticket_order method handles loading trip, checking availability,
            # updating trip availability, creating order, adding line item,
            # processing payment, and saving the order and trip.
            created_order = Order.create_ticket_order(
                account_id=current_user_id,
                trip_id=selected_trip_id_from_form,
                payment_method_details=f"Simulated {payment_type.capitalize()}"
            )

            if created_order:
                if created_order.status == OrderStatus.PAID:
                    flash(f"Ticket purchased successfully! Order ID: {created_order.orderID}", "success")

                    # --- Find the ticket SalesLineItem ---
                    purchased_ticket_sli = None
                    # Assuming only one ticket line item for a simple ticket purchase scenario
                    for sli in created_order.orderLinetems:
                        if sli.item_type == "ticket":
                            purchased_ticket_sli = sli
                            break # Found the ticket line item

                    # --- Load the associated Trip object using the item_id from the SLI ---
                    associated_trip = None
                    if purchased_ticket_sli:
                        associated_trip = Trip.get_by_id(purchased_ticket_sli.item_id)

                    # Pass the created Order object, the specific ticket SLI (if found),
                    # and the associated Trip object (if found) to the success template.
                    return render_template('buy_ticket_success.html',
                                        order=created_order, # Pass the order object
                                        purchased_ticket_sli=purchased_ticket_sli, # Pass the ticket SLI object
                                        associated_trip=associated_trip, # Pass the associated Trip object
                                        title="Purchase Successful!")
                elif created_order.status == OrderStatus.FAILED:
                     flash(f"Order {created_order.orderID} created, but payment failed. Please try paying from your order list.", "danger")
                     return redirect(url_for('order.view_order', order_id=created_order.orderID))
                else: # Should not happen if factory works as expected
                     flash(f"Order {created_order.orderID} created with unexpected status: {created_order.status.value}. Please contact support.", "warning")
                     return redirect(url_for('order.view_order', order_id=created_order.orderID))

            else:
                 # created_order is None if account or trip not found inside the factory
                 flash("Error: Could not create order. Selected trip or your account not found.", "danger")
                 # Repopulate choices just in case
                 all_trips_objects_rerender = Trip.get_all()
                 available_trips_for_selection_rerender = [trip for trip in all_trips_objects_rerender if trip and trip.available_seats > 0]
                 form.selected_trip_id.choices = [
                    (trip.id, f"{trip.route} - {trip.date} {trip.time} (RM {trip.price:.2f}, Seats: {trip.available_seats})")
                    for trip in available_trips_for_selection_rerender
                 ] if available_trips_for_selection_rerender else []
                 # Re-render the form page
                 return render_template('buy_ticket_new.html', form=form, title="Buy Ticket")

        except ValueError as e:
            # Catch specific business logic errors from the factory method (like not enough seats)
            flash(f"Purchase failed: {e}", "warning")
            # Repopulate choices and re-render form
            all_trips_objects_rerender = Trip.get_all()
            available_trips_for_selection_rerender = [trip for trip in all_trips_objects_rerender if trip and trip.available_seats > 0]
            form.selected_trip_id.choices = [
               (trip.id, f"{trip.route} - {trip.date} {trip.time} (RM {trip.price:.2f}, Seats: {trip.available_seats})")
               for trip in available_trips_for_selection_rerender
            ] if available_trips_for_selection_rerender else []
            return render_template('buy_ticket_new.html', form=form, title="Buy Ticket")
        except RuntimeError as e:
            # Catch critical errors during saving/payment processing inside the factory
             flash(f"A system error occurred during order processing: {e}", "danger")
             # Repopulate choices and re-render form
             all_trips_objects_rerender = Trip.get_all()
             available_trips_for_selection_rerender = [trip for trip in all_trips_objects_rerender if trip and trip.available_seats > 0]
             form.selected_trip_id.choices = [
                (trip.id, f"{trip.route} - {trip.date} {trip.time} (RM {trip.price:.2f}, Seats: {trip.available_seats})")
                for trip in available_trips_for_selection_rerender
             ] if available_trips_for_selection_rerender else []
             return render_template('buy_ticket_new.html', form=form, title="Buy Ticket")
        except Exception as e:
            # Catch any other unexpected errors
            flash(f"An unexpected error occurred: {e}", "danger")
            # Repopulate choices and re-render form
            all_trips_objects_rerender = Trip.get_all()
            available_trips_for_selection_rerender = [trip for trip in all_trips_objects_rerender if trip and trip.available_seats > 0]
            form.selected_trip_id.choices = [
               (trip.id, f"{trip.route} - {trip.date} {trip.time} (RM {trip.price:.2f}, Seats: {trip.available_seats})")
               for trip in available_trips_for_selection_rerender
            ] if available_trips_for_selection_rerender else []
            return render_template('buy_ticket_new.html', form=form, title="Buy Ticket")


    # GET request or form validation failed on POST
    # Choices are populated before validation for both cases.
    # Pass the list of objects to the template for display
    return render_template('buy_ticket_new.html',
                           form=form,
                           title="Buy Ticket",
                           # Pass list of Trip objects (or their dicts if template expects dicts)
                           # Let's pass dicts for now to potentially avoid template changes,
                           # but the OOP way is to pass objects and update template.
                           # Stick to dicts passed to template for minimal template impact during refactor.
                           available_trips_data= [t.to_dict() for t in available_trips_for_selection]
                          )


# --- Scenario 2: Reschedule Ticket ---
@order_bp.route('/reschedule-ticket', methods=['GET', 'POST'])
@login_required
def reschedule_ticket_find():
    form = FindTicketForRescheduleForm()
    current_user_id = get_current_user_id()

    if form.validate_on_submit():
        order_id_input = form.order_id.data

        # --- Load Order object ---
        order = Order.get_by_id(order_id_input)

        # Check if order exists and belongs to the current user
        if not order or order.placingAccountID != current_user_id:
            flash(f"Order {order_id_input} not found or you are not authorized to access it.", "warning")
            return render_template('reschedule_ticket_find.html', form=form, title="Reschedule Ticket")

        # --- Find active ticket SalesLineItem object ---
        original_active_ticket_sli = None
        for sli in order.orderLinetems:
            # Compare using Enum value
            if sli.item_type == "ticket" and sli.line_item_status == TicketStatus.ACTIVE:
                original_active_ticket_sli = sli
                break

        if not original_active_ticket_sli:
            flash(f"No active ticket found in order {order_id_input} to reschedule. The order might already be cancelled, completed, or items rescheduled.", "warning")
            return redirect(url_for('order.view_order', order_id=order_id_input)) # Redirect to view order

        # --- Load original Trip object using item_id from SLI ---
        original_trip = Trip.get_by_id(original_active_ticket_sli.item_id)

        if not original_trip:
            flash(f"Critical error: Details for the original trip associated with your ticket could not be found. Please contact support.", "danger")
            return render_template('reschedule_ticket_find.html', form=form, title="Reschedule Ticket")

        # --- Load all Trip objects and filter alternatives ---
        all_trips_objects = Trip.get_all()
        # Filter alternative trips (objects) based on route, excluding original, and availability
        alternative_trips = [
            trip for trip in all_trips_objects
            if trip and trip.route == original_trip.route and
               trip.id != original_trip.id and
               trip.available_seats > 0
        ]

        reschedule_form = RescheduleTicketForm()
        reschedule_form.order_id.data = order_id_input
        reschedule_form.original_line_item_id.data = original_active_ticket_sli.lineItemID
        reschedule_form.original_trip_id.data = original_trip.id # Store original trip ID (as string)

        if alternative_trips:
            # Populate choices from alternative Trip objects
            reschedule_form.selected_new_trip_id.choices = [
                (t.id, f"{t.route} - {t.date} {t.time} (RM {t.price:.2f}, Seats: {t.available_seats})")
                for t in alternative_trips
            ]
        else:
            flash(f"No alternative trips currently available for the route '{original_trip.route}'. Please check back later or contact support.", "info")

        # Pass model objects (or their dicts) to the template
        return render_template('reschedule_ticket_confirm_new.html',
                               form=reschedule_form,
                               order_id=order_id_input, # Pass ID
                               original_ticket_sli=original_active_ticket_sli.to_dict(), # Pass SLI dict
                               original_trip_details=original_trip.to_dict(), # Pass Trip dict
                               alternative_trips_available=bool(alternative_trips),
                               title="Confirm Reschedule")

    # GET request handling
    return render_template('reschedule_ticket_find.html', form=form, title="Reschedule Ticket")


@order_bp.route('/reschedule-ticket/confirm', methods=['POST'])
@login_required
def reschedule_ticket_confirm_submit():
    form = RescheduleTicketForm()
    current_user_id = get_current_user_id()

    # --- Repopulate choices before validation on POST ---
    # Need the original trip ID to filter alternatives
    original_trip_id_for_choices = form.original_trip_id.data
    if original_trip_id_for_choices:
        original_trip_for_choices = Trip.get_by_id(original_trip_id_for_choices)
        if original_trip_for_choices:
            _all_trips_objects_for_choices = Trip.get_all()
            _alternative_trips_for_choices = [
                trip for trip in _all_trips_objects_for_choices
                if trip and trip.route == original_trip_for_choices.route and
                   trip.id != original_trip_for_choices.id and
                   trip.available_seats > 0
            ]
            form.selected_new_trip_id.choices = [
                (t.id, f"{t.route} - {t.date} {t.time} (RM {t.price:.2f}, Seats: {t.available_seats})")
                for t in _alternative_trips_for_choices
            ] if _alternative_trips_for_choices else []
        else:
             form.selected_new_trip_id.choices = [] # Original trip not found
    else:
        form.selected_new_trip_id.choices = [] # No original trip ID in form data
    # --- End Repopulate choices ---

    if form.validate_on_submit():
        order_id = form.order_id.data
        original_sli_id = form.original_line_item_id.data
        selected_new_trip_id = form.selected_new_trip_id.data # This is the ID string

        # --- Load Order object ---
        order = Order.get_by_id(order_id)

        # Check if order exists and belongs to the current user
        if not order or order.placingAccountID != current_user_id:
            flash("Order not found or you are not authorized to modify this order.", "danger")
            return redirect(url_for('order.reschedule_ticket_find'))

        # --- Load the new Trip object ---
        new_trip = Trip.get_by_id(selected_new_trip_id)

        # Check if new trip exists
        if not new_trip:
            flash("The selected new trip could not be found. It might have been removed.", "danger")
            # Re-render form with populated choices and errors
            original_trip_id_for_rerender = form.original_trip_id.data
            _original_trip_for_rerender = Trip.get_by_id(original_trip_id_for_rerender)
            _original_sli_for_rerender = order.find_line_item_by_sli_id(original_sli_id)

            return render_template('reschedule_ticket_confirm_new.html',
                               form=form,
                               order_id=order_id,
                               original_ticket_sli=_original_sli_for_rerender.to_dict() if _original_sli_for_rerender else None,
                               original_trip_details=_original_trip_for_rerender.to_dict() if _original_trip_for_rerender else None,
                               alternative_trips_available=bool(form.selected_new_trip_id.choices),
                               title="Confirm Reschedule - Errors")

        # --- Call the reschedule method on the Order object ---
        try:
            # The method handles finding the original SLI, marking it rescheduled,
            # updating availability on old/new trips, adding the new SLI,
            # updating total, and saving the order and trips.
            success = order.reschedule_ticket_line_item(original_sli_id, new_trip)

            if success:
                 flash("Ticket successfully rescheduled!", "success")
                 # Pass the new Trip object (or its dict) to the success template
                 return render_template('reschedule_success_new.html',
                                        order_id=order_id,
                                        new_ticket_details=new_trip.to_dict(), # Pass new trip dict
                                        title="Reschedule Successful")
            else:
                # If the method returns False, it means the original SLI wasn't found,
                # wasn't active, or new trip had no seats (though availability check should catch this earlier)
                flash("Failed to reschedule ticket. Please ensure the ticket is active and the new trip is available.", "danger")
                # Re-render form with errors
                original_trip_id_for_rerender = form.original_trip_id.data
                _original_trip_for_rerender = Trip.get_by_id(original_trip_id_for_rerender)
                _original_sli_for_rerender = order.find_line_item_by_sli_id(original_sli_id)

                return render_template('reschedule_ticket_confirm_new.html',
                                   form=form,
                                   order_id=order_id,
                                   original_ticket_sli=_original_sli_for_rerender.to_dict() if _original_sli_for_rerender else None,
                                   original_trip_details=_original_trip_for_rerender.to_dict() if _original_trip_for_rerender else None,
                                   alternative_trips_available=bool(form.selected_new_trip_id.choices),
                                   title="Confirm Reschedule - Errors")

        except ValueError as e:
            # Catch specific business logic errors from model methods (e.g., not enough seats)
             flash(f"Rescheduling failed: {e}", "warning")
             # Re-render form with errors
             original_trip_id_for_rerender = form.original_trip_id.data
             _original_trip_for_rerender = Trip.get_by_id(original_trip_id_for_rerender)
             _original_sli_for_rerender = order.find_line_item_by_sli_id(original_sli_id)

             return render_template('reschedule_ticket_confirm_new.html',
                                form=form,
                                order_id=order_id,
                                original_ticket_sli=_original_sli_for_rerender.to_dict() if _original_sli_for_rerender else None,
                                original_trip_details=_original_trip_for_rerender.to_dict() if _original_trip_for_rerender else None,
                                alternative_trips_available=bool(form.selected_new_trip_id.choices),
                                title="Confirm Reschedule - Errors")

        except Exception as e:
            # Catch any other unexpected errors during the process
            print(f"CRITICAL ERROR in reschedule_ticket_confirm_submit: {e}")
            flash(f"An unexpected error occurred during rescheduling: {e}. Please contact support.", "danger")
            # Re-render form with errors
            original_trip_id_for_rerender = form.original_trip_id.data
            _original_trip_for_rerender = Trip.get_by_id(original_trip_id_for_rerender)
            _original_sli_for_rerender = order.find_line_item_by_sli_id(original_sli_id)

            return render_template('reschedule_ticket_confirm_new.html',
                                form=form,
                                order_id=order_id,
                                original_ticket_sli=_original_sli_for_rerender.to_dict() if _original_sli_for_rerender else None,
                                original_trip_details=_original_trip_for_rerender.to_dict() if _original_trip_for_rerender else None,
                                alternative_trips_available=bool(form.selected_new_trip_id.choices),
                                title="Confirm Reschedule - Errors")

    else:
        flash("Invalid submission for reschedule. Please check your selection and try again.", "danger")
        # Re-render the confirm page with errors and original data
        order_id_for_rerender = form.order_id.data
        original_sli_id_for_rerender = form.original_line_item_id.data
        original_trip_id_for_rerender = form.original_trip_id.data

        # --- Re-fetch data as objects for re-render ---
        _order_for_rerender = Order.get_by_id(order_id_for_rerender)
        _original_sli_for_rerender = _order_for_rerender.find_line_item_by_sli_id(original_sli_id_for_rerender) if _order_for_rerender else None
        _original_trip_for_rerender = Trip.get_by_id(original_trip_id_for_rerender)

        return render_template('reschedule_ticket_confirm_new.html',
                               form=form,
                               order_id=order_id_for_rerender,
                               original_ticket_sli=_original_sli_for_rerender.to_dict() if _original_sli_for_rerender else None, # Pass dict
                               original_trip_details=_original_trip_for_rerender.to_dict() if _original_trip_for_rerender else None, # Pass dict
                               alternative_trips_available=bool(form.selected_new_trip_id.choices),
                               title="Confirm Reschedule - Errors")


# --- Scenario 3: Buying Merchandise (Bulk) ---
@order_bp.route('/buy-merchandise', methods=['GET', 'POST'])
@login_required
def buy_merchandise_bulk():
    form = BulkBuyMerchandiseForm()
    # --- Use Merchandise model to get all items as objects ---
    all_merchandise_items_objects = Merchandise.get_all() # Get list of objects
    # Pass dicts to the template to avoid needing template changes
    all_merchandise_items_for_display = [item.to_dict() for item in all_merchandise_items_objects if item]

    current_user_id = get_current_user_id()

    if request.method == 'POST':
        # Form validation in bulk buy is tricky with dynamic quantities per item.
        # We validate payment type here, and check item quantities/stock manually.
        if not form.validate(): # This form currently only has payment_type validation
            flash("Please select a payment method.", "danger")
            return render_template('buy_merchandise_bulk.html', form=form, merchandise_list=all_merchandise_items_for_display, title="Buy Merchandise")

        items_selected_for_purchase = []
        purchase_possible = True
        payment_type = form.payment_type.data

        # Iterate through the items *available* (Merchandise objects)
        for item_obj in all_merchandise_items_objects:
            if not item_obj: continue # Skip None objects from get_all()

            item_id = item_obj.merchandiseID
            try:
                # Get quantity from request form data
                quantity_str = request.form.get(f'quantity_{item_id}', '0')
                quantity = int(quantity_str) if quantity_str.strip() else 0
            except ValueError:
                quantity = 0 # Treat invalid input as zero quantity

            if quantity > 0:
                 # Check availability *using the Merchandise object's method*
                 if not item_obj.check_availability(quantity):
                    flash(f"Not enough stock for {item_obj.name}. Requested: {quantity}, Available: {item_obj.stockLevel}.", "warning")
                    purchase_possible = False
                    # Continue loop to find all stock issues, but set flag
                    continue

                 items_selected_for_purchase.append({
                     'merch_id': item_id,
                     'quantity': quantity
                 })

        if not items_selected_for_purchase:
            flash("No items selected or quantities are zero.", "info")
            return render_template('buy_merchandise_bulk.html', form=form, merchandise_list=all_merchandise_items_for_display, title="Buy Merchandise")

        if not purchase_possible:
             # If purchase_possible was set to False due to insufficient stock on any requested item
             flash("Please adjust quantities for items with insufficient stock to proceed.", "danger")
             return render_template('buy_merchandise_bulk.html', form=form, merchandise_list=all_merchandise_items_for_display, title="Buy Merchandise")


        # --- Use Order factory method to create the order ---
        try:
             # create_merchandise_order method handles loading merch, checking availability,
             # creating order, adding line items, processing payment (which updates stock),
             # and saving the order and merchandise items.
             created_order = Order.create_merchandise_order(
                 account_id=current_user_id,
                 items_with_quantities=items_selected_for_purchase,
                 payment_method_details=f"Simulated {payment_type.capitalize()}"
             )

             if created_order:
                if created_order.status == OrderStatus.PAID:
                    flash(f"Merchandise order placed successfully! Order ID: {created_order.orderID}", "success")
                    # Redirect to a success route, passing the order ID
                    # The success route can then load the order object
                    return redirect(url_for('order.buy_merchandise_success', order_id=created_order.orderID))
                elif created_order.status == OrderStatus.FAILED:
                     flash(f"Order {created_order.orderID} created, but payment failed. Please try paying from your order list.", "danger")
                     return redirect(url_for('order.view_order', order_id=created_order.orderID))
                else: # Should not happen
                     flash(f"Order {created_order.orderID} created with unexpected status: {created_order.status.value}. Please contact support.", "warning")
                     return redirect(url_for('order.view_order', order_id=created_order.orderID))
             else:
                 # created_order is None if account or no valid items found in factory
                 flash("Error: Could not create order. Your account not found or no items were valid for purchase.", "danger")
                 # Re-render with errors
                 return render_template('buy_merchandise_bulk.html', form=form, merchandise_list=all_merchandise_items_for_display, title="Buy Merchandise")

        except ValueError as e:
            # Catch specific business logic errors from the factory method (like not enough stock)
            flash(f"Purchase failed: {e}", "warning")
            # Re-render with errors
            return render_template('buy_merchandise_bulk.html', form=form, merchandise_list=all_merchandise_items_for_display, title="Buy Merchandise")
        except RuntimeError as e:
            # Catch critical errors during saving/payment processing inside the factory
             flash(f"A system error occurred during order processing: {e}", "danger")
             # Re-render with errors
             return render_template('buy_merchandise_bulk.html', form=form, merchandise_list=all_merchandise_items_for_display, title="Buy Merchandise")
        except Exception as e:
            # Catch any other unexpected errors
            flash(f"An unexpected error occurred: {e}", "danger")
            # Re-render with errors
            return render_template('buy_merchandise_bulk.html', form=form, merchandise_list=all_merchandise_items_for_display, title="Buy Merchandise")


    # This handles the GET request.
    # Pass the list of Merchandise objects (converted to dicts for template consistency)
    return render_template('buy_merchandise_bulk.html', form=form, merchandise_list=all_merchandise_items_for_display, title="Buy Merchandise")


# --- Scenario 4: Cancel Order ---
@order_bp.route('/cancel-order', methods=['GET', 'POST'])
@login_required
def cancel_order_find():
    form = FindOrderForm()
    current_user_id = get_current_user_id()

    if form.validate_on_submit():
        order_id_input = form.order_id.data

        # --- Load Order object ---
        order = Order.get_by_id(order_id_input)

        # Check if order exists and belongs to the current user
        if not order or order.placingAccountID != current_user_id:
            flash(f"Order {order_id_input} not found or you are not authorized to access it.", "warning")
            return render_template('cancel_order_find.html', form=form, title="Cancel Order")

        # --- Filter active SalesLineItem objects ---
        active_items_to_cancel = [
            sli for sli in order.orderLinetems
            if sli.line_item_status == TicketStatus.ACTIVE # Compare Enum value
        ]

        if not active_items_to_cancel:
            flash(f"No active items found in order {order_id_input} to cancel. The order might already be cancelled, completed, or items rescheduled.", "info")
            # Redirect to view the order details page
            return redirect(url_for('order.view_order', order_id=order_id_input))

        confirm_form = ConfirmCancellationForm()
        confirm_form.order_id.data = order_id_input

        # Pass model objects (or their dicts) to template
        return render_template('cancel_order_confirm.html',
                               order_id=order_id_input, # Pass ID
                               order_data_for_display=order.to_dict(), # Pass order dict
                               active_items_to_cancel=[sli.to_dict() for sli in active_items_to_cancel], # Pass list of SLI dicts
                               form=confirm_form,
                               title="Confirm Order Cancellation")

    return render_template('cancel_order_find.html', form=form, title="Cancel Order")


@order_bp.route('/cancel-order/confirm', methods=['POST'])
@login_required
def cancel_order_confirm_action():
    form = ConfirmCancellationForm()
    current_user_id = get_current_user_id()

    if form.validate_on_submit():
        order_id_to_cancel = form.order_id.data

        # --- Load Order object ---
        order = Order.get_by_id(order_id_to_cancel)

        # Check if order exists and belongs to the current user
        if not order or order.placingAccountID != current_user_id:
            flash("Order not found or you are not authorized to perform this action.", "danger")
            return redirect(url_for('order.cancel_order_find'))

        # --- Call the cancellation method on the Order object ---
        try:
             # The method handles marking items, updating stock/seats,
             # updating order status, initiating refund (if paid), and saving.
            success = order.initiate_cancellation()

            if success:
                flash(f"Order {order.orderID} and its active items have been cancelled.", "success")
                # Re-fetch the order to get the final state after saving in the method
                # Or pass the order object directly, but re-fetching ensures it's fully updated from file.
                # Let's re-fetch for safety in a file-based system.
                updated_order = Order.get_by_id(order.orderID)
                # Extract cancelled item details for the success page display
                cancelled_item_details_for_log = [
                    {"name": sli.item_name, "quantity": sli.quantity, "type": sli.item_type}
                     for sli in updated_order.orderLinetems if sli.line_item_status == TicketStatus.CANCELLED # Use Enum
                ]
                # Ensure we only show items that *were* marked cancelled by the process,
                # not items that were already cancelled from previous actions.
                # This would require tracking which items were changed in the initiate_cancellation method,
                # or comparing state before/after, which adds complexity.
                # For simplicity, let's show all items that are now in a cancelled state.
                all_items_that_are_now_cancelled = [
                    {"name": sli.item_name, "quantity": sli.quantity, "type": sli.item_type}
                    for sli in updated_order.orderLinetems if sli.line_item_status == TicketStatus.CANCELLED
                ]


                return render_template('cancel_order_success.html',
                                       order_id=order.orderID,
                                       cancelled_items_log=all_items_that_are_now_cancelled,
                                       title="Order Cancelled Successfully")
            else:
                # Method returned False (no active items found)
                flash(f"No active items were found to process for cancellation in order {order.orderID}. Status might have changed.", "info")
                return redirect(url_for('order.view_order', order_id=order.orderID))

        except Exception as e:
            # Catch any errors during the cancellation process (including save errors from models)
            print(f"CRITICAL ERROR in cancel_order_confirm_action: {e}")
            flash(f"An unexpected error occurred during cancellation: {e}. Data might be inconsistent. Please contact support.", "danger")
            # Redirect back to finding the order or viewing it
            return redirect(url_for('order.view_order', order_id=order_id_to_cancel))

    else:
        flash("Invalid cancellation request. Please try again.", "danger")
        return redirect(url_for('order.cancel_order_find'))


# --- Other supporting routes ---
@order_bp.route('/')
@login_required
def list_orders():
    current_user_id = get_current_user_id()
    # Use Order class method to get user's orders as objects
    user_orders_objects = Order.get_orders_by_account_id(current_user_id)

    # Pass the list of Order objects to the template
    # ---  Pass Enum classes to the template context ---
    return render_template('list_orders_new.html',
                           orders=user_orders_objects,
                           title="My Orders",
                           OrderStatus=OrderStatus, # Pass the Enum class
                           TicketStatus=TicketStatus, # Pass the Enum class
                           PaymentStatus=PaymentStatus # Pass the Enum class
                          )

@order_bp.route('/<string:order_id>')
@login_required
def view_order(order_id):
    current_user_id = get_current_user_id()
    # Load Order object
    order = Order.get_by_id(order_id)

    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for('order.list_orders'))

    if order.placingAccountID != current_user_id:
        flash("You are not authorized to view this order.", "danger")
        return redirect(url_for('order.list_orders'))

    # Pass the Order object and Enum classes to the template
    # --- Pass Enum classes ---
    return render_template('order_detail_new.html',
                           order=order,
                           title=f"Order Details - {order_id}",
                           OrderStatus=OrderStatus,      # Pass the Enum class
                           TicketStatus=TicketStatus,    # Pass the Enum class
                           PaymentStatus=PaymentStatus   # Pass the Enum class
                          )

@order_bp.route('/<string:order_id>/pay', methods=['GET','POST'])
@login_required
def pay_order(order_id):
    current_user_id = get_current_user_id()

    # --- Load Order object ---
    order = Order.get_by_id(order_id)

    if not order:
        flash(f"Order {order_id} not found.", "warning")
        return redirect(url_for('order.list_orders'))

    if order.placingAccountID != current_user_id:
        flash("You are not authorized to pay for this order.", "danger")
        return redirect(url_for('order.list_orders'))

    # --- Use Enum value for comparison ---
    if order.status != OrderStatus.PENDING_PAYMENT:
        flash(f"Order {order_id} is not pending payment (Status: {order.status.value}).", "info") # Use .value for display
        return redirect(url_for('order.view_order', order_id=order_id))

    # This route triggers payment process regardless of GET or POST for simplicity
    # A real payment flow would likely involve form submission on POST
    payment_method_details = request.form.get("payment_method", "Simulated Payment (Web Button)") # Get from form data if POST

    # --- Call the process_payment method on the Order object ---
    try:
        # The method handles recalculating total, creating/updating payment,
        # updating order status to PAID, updating stock/seats for merchandise (if any),
        # and saving the order.
        payment_successful = order.process_payment(payment_method_details)

        if payment_successful:
            flash(f"Payment for order {order_id} simulated successfully!", "success")
        else:
             # process_payment already handles setting status to FAILED and saving
            flash(f"Payment simulation failed for order {order_id}. Status set to {order.status.value}.", "danger")

    except Exception as e:
        # Catch any errors during payment processing (including saving)
        print(f"CRITICAL ERROR in pay_order for {order_id}: {e}")
        flash(f"An unexpected error occurred during payment: {e}. Please contact support.", "danger")
        # The order might be in an inconsistent state depending on where the error occurred.
        # It's saved as FAILED by process_payment if the payment part fails,
        # but saving the order itself might fail after that.
        # Reloading the order might show the state it *was* saved in.
        # For robustness, might attempt to reload and check status again before redirecting.

    return redirect(url_for('order.view_order', order_id=order_id))


# Route for bulk merchandise buy success page
# This route now loads the Order object and passes it to the template
@order_bp.route('/buy-merchandise/success/<order_id>')
@login_required
def buy_merchandise_success(order_id):
    current_user_id = get_current_user_id()
    # ---  Load Order object ---
    order = Order.get_by_id(order_id)
    
    if not order or order.placingAccountID != current_user_id:
         flash("Order not found or you are not authorized.", "danger")
         return redirect(url_for('order.list_orders'))

    # Filter merchandise line items (as objects)
    merchandise_items_sli = [
        sli for sli in order.orderLinetems if sli.item_type == "merchandise"
    ]

    # Access total amount from the Order object
    total_amount = order.totalAmount

    # Pass the order object and list of SLI objects to the template
    return render_template('buy_merchandise_success.html',
                           order=order, # Pass the order object
                           purchased_items_sli=merchandise_items_sli, # Pass list of SLI objects
                           total_amount=total_amount, # Can also get from order.totalAmount in template
                           title="Order Placed!")