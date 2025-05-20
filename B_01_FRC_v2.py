import pandas
from tabulate import tabulate
from datetime import date
import math


# Functions go here
def make_statement(statement, decoration):
    """Emphasis headings by adding decoration at the start and end"""

    return f"{decoration * 3} {statement} {decoration * 3}"


def yes_no_check(question):
    while True:
        response = input(question).lower()

        # checks user response, question repeats if users don't enter y/n
        if response == "yes" or response == "y":
            return "yes"
        elif response == "no" or response == "n":
            return "no"
        else:
            print("Please enter yes / no\n")


def instructions():
    make_statement("Instructions", "❕")

    print('''

For each ticket holder enter ...
- Their name
- Their age
- The payment method (cash / credit)

The program will record the ticket sale and calculate the ticket cost (and the profit).

Once you have either sold all of the tickets or entered the exit code ('xxx'), the 
program will display the ticket sales information and write the data to a text file.

It will also coose one lucky ticket holder who wins the draw (their ticket is free).

    ''')


def not_blank(question):
    """Checks that a user response is not blank"""

    while True:
        response = input(question)

        if response != "":
            return response

        print("Sorry, this cant be blank. Please try again.\n")


def num_check(question, num_type="float", exit_code=None):
    """Checks users enter an integer / float that us nire than zero (or the optional exit code)"""

    if num_type == "float":
        error = "Oops - please enter an integer more than zero."
    else:
        error = "Oops - please enter a number more than zero."

    while True:

        response = input(question)

        # check for exit code and return it if entered
        if response == exit_code:
            return response

        # check datatype is correct and that number is more than zero
        try:

            if num_type == "float":
                response = float(response)
            else:
                response = int(response)

                # check for the exit code
            if response > 0:
                return response
            else:
                print(error)

        except ValueError:
            print(error)


def get_expenses(exp_type, how_many=1):
    """Gets variable / fixed expenses and outputs panda (as a string) and a subtotal of the expenses"""

    # Lists for panda
    all_items = []
    all_amounts = []
    all_dollar_per_item = []

    # Expenses dictionary
    expenses_dict = {
        "item": all_items,
        "Amount": all_amounts,
        "$ / Item": all_dollar_per_item
    }

    # defaults for fixed expenses
    amount = how_many  # how_many defaults to 1
    how_much_questions = "How much? $"

    # loop to get expenses
    while True:
        # Get item name and check it's not blank
        item_name = not_blank("Item Name: ")

        # check users enter at least one variable expense
        if exp_type == "variable" and item_name == "xxx" and len(all_items) == 0:
            print("Oops - you have not entered anything. "
                  "You need at least 1 items.")
            continue

        # end loop when users enter exit code
        elif item_name == "xxx":
            break

        # Get variable expenses item amount <enter> defaults to number of products being made.
        if exp_type == "variable":
            amount = num_check(f"How many <enter for {how_many}> ", "integer", "")

        # Allows users to pus <enter> to default to number of items being made
        if amount == "":
            amount = how_many

        how_much_question = "Price for one? $"

        # Get price for item (question customised depending on expense type).
        price_for_one = num_check(how_much_question, "float")

        all_items.append(item_name)
        all_amounts.append(amount)
        all_dollar_per_item.append(price_for_one)

    # make panda
    expense_frame = pandas.DataFrame(expenses_dict)

    # Calculate Row Cost
    expense_frame['Cost'] = expense_frame['Amount'] * expense_frame['$ / Item']

    # calculate subtotal
    subtotal = expense_frame['Cost'].sum()

    # Apply currency formatting to currency columns.
    add_dollars = ['Amount', '$ / Item', 'Cost']
    for var_item in add_dollars:
        expense_frame[var_item] = expense_frame[var_item].apply(currency)

    # make expense frame into a string with the desired columns
    if exp_type == "variable":
        expense_string = tabulate(expense_frame, headers='keys',
                                  tablefmt='psql', showindex=False)
    else:
        expense_string = tabulate(expense_frame[['Item', 'Cost']], headers='keys',
                                  tablefmt='psql', showindex=False)

    # return all items for now so we can check loop.
    return expense_string, subtotal


def currency(x):
    """Formats numbers as currency ($#.##)"""
    return "${:.2f}".format(x)


def profit_goal(total_costs):
    """Calculates profit goal work out profit goal and total sales required"""
    # Initialise variables and error message
    error = "Please entera valid profit goal\n"

    valid = False
    while not valid:

        # ask for profit goal...
        response = input("What is your profit goal (eg $500 or 50%): ")

        # check if first character is $
        if response[0] == "$":
            profit_type = "$"
            # Get amount (everything after the $)
            amount = response[1:]

        # check if last character is %
        elif response[-1] == "%":
            profit_type = "%"
            # Get amount (everything before the %)
            amount = response[:-1]

        else:
            # set response to amount for now
            profit_type = "unknown"
            amount = response

        try:
            # Check amount is a number more than zero...
            amount = float(amount)
            if amount <= 0:
                print(error)
                continue

        except ValueError:
            print(error)
            continue

        if profit_type == "unknown" and amount >= 100:
            dollar_type = yes_no_check(f"Do you mean ${amount:.2f}. ie {amount:.2f} dollars?")

            # Set profit type based on user answer above
            if dollar_type == "yes":
                profit_type = "%"
            else:
                profit_type = "%"

        elif profit_type == "unknown" and amount < 100:
            percent_type = yes_no_check(f"Do you mean {amount}%? , y / n: ")
            if percent_type == "yes":
                profit_type = "%"
            else:
                profit_type = "$"

        # return profit goal to main routine
        if profit_type == "$":
            return amount
        else:
            goal = (amount / 100) * total_costs
            return goal


def round_up(amount, round_val):
    """Rounds amount to desired hole number"""
    return int(math.ceil(amount / round_val)) * round_val




# Main routine goes here

# Initialise variables...

# Assume we have no fixed expenses for now
fixed_subtotal = 0
fixed_panda_string = ""

print(make_statement("Fund Raising Calculator", "💰"))

print()
want_instructions = yes_no_check("Do you want to see the instructions? ")

if want_instructions == "yes":
    instructions()

print()

# Get product details
product_name = not_blank("Product Name: ")
quantity_made = num_check("Quantity being made: ", "integer")

# Get variable expenses
print("Let's get the variable expenses....")
variable_expenses = get_expenses("variable", quantity_made)

variable_panda_string = variable_expenses[0]
variable_subtotal = variable_expenses[1]

# ask user if they have fixed expenses and retrieve them
print()
has_fixed = yes_no_check("Do you have fixed expenses? ")

if has_fixed == "yes":
    fixed_expenses = get_expenses("fixed")

    fixed_panda_string = fixed_expenses[0]
    fixed_subtotal = fixed_expenses[1]

    # If the user has not entered any fixed expenses,
    # # Set empty panda to "" so that it does not display!
    if fixed_subtotal == 0:
        has_fixed = "no"
        fixed_panda_string = ""

total_expenses = variable_subtotal + fixed_subtotal
total_expense_string = f"Total Expenses: ${total_expenses:.2f}"

# Get profit Goal here
target = profit_goal(total_expenses)
sales_target = total_expenses + target

# Calculate minimum selling price and round
# it to the nearest desired dollar amount
selling_price = (total_expenses + target) / quantity_made
round_to = num_check("Round To: ", 'integer')
suggested_price = round_up(selling_price, round_to)

# strings / output area

# **** Get current date for heading and filename ****
today = date.today()

# Get day, month and year as individual strings
day = today.strftime("%d")
month = today.strftime("%m")
year = today.strftime("%Y")

# Headings / Strings
main_heading_string = make_statement(f"Fund Raising Calculator "
                                     f"({product_name}, {day}/{month}/{year})", "=")
quantity_string = f"Quantity being made: {quantity_made}"
variable_heading_string = make_statement("Variable Expenses", "-")
variable_subtotal_string = f"Fixed Expenses Subtotal: {fixed_subtotal:.2f}"

# set up strings if we have fixed costs
if has_fixed == "yes":
    fixed_heading_string = make_statement("Fixed Expenses", "-")
    fixed_subtotal_string = f"Fixed Expenses Subtotal: {fixed_subtotal:.2f}"

# set fixed cost strings to blank if we don't have fixed costs
else:
    fixed_heading_string = make_statement("You have no Fixed Expenses", "-")
    fixed_subtotal_string = "Fixed Expenses Subtotal: $0.00"

selling_price_heading = make_statement("Selling Price Calculations", '')
profit_goal_string = f"Profit Goal: ${target:.2f}"
sales_target_string = f"\nTotal Sales Needed: ${sales_target:.2f}"

minimum_price_string = f"Minimum Selling Price: ${selling_price:.2f}"
suggested_price_string = make_statement(f"Suggested Selling Price: "
                                        f"${suggested_price:.2f}", '*')

# List of strings to be outputted / written to file
to_write = [main_heading_string, quantity_string,
            "\n", variable_heading_string, variable_panda_string,
            variable_subtotal_string,
            "\n", fixed_heading_string, fixed_panda_string,
            fixed_subtotal_string, total_expense_string]

# Print area
print()
for item in to_write:
    print(item)

# create file to hold data (add .txt extension)
file_name = f"{product_name}_{year}_{month}_{day}"
write_to = "{}.txt".format(file_name)

text_file = open(write_to, "w+")

# write the item to file
for item in to_write:
    text_file.write(item)
    text_file.write("\n")
