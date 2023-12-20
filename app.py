from flask import Flask, render_template, request, redirect, url_for
import sqlite3

# Define the app with Flask
app = Flask(__name__)

# Database name
database_name = "database.db"


def create_table():
    '''
    Function to establish a connection to the database and create a table
    '''
    # Connection - Will automatically create the database.db file if it doesn't exist (won't overwrite the file if it already exists)
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # SQL Query, id is set to autoincrement
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT,
            position TEXT,
            email TEXT
        )
    ''')
    # Commit query 
    conn.commit()
    # Close connection
    conn.close()

# Call the create_table function when first run 
create_table()


def get_employees():
    '''
    This function is useful for fetching all data in the employees table
    '''
    # Connection
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # SQL Query
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return employees

@app.route("/", methods=['POST', "GET"]) # Using the POST method because there is a login form on the home page
def home():
    '''
    Function for the home page.
    The homepage contains an Admin login form.
    '''
    # If the method is post, it will take input from the form
    if request.method == 'POST':
        # Request input from the form for simple authentication using the keyword 'Admin'
        name = request.form["nm"]
        if name == 'Admin':
            # Return with a redirect to the 'admin' function
            return redirect(url_for("admin"))
        else:
            # Only Admin is allowed
            return "<h3>Oops, sorry you are not an admin</h3>"
    else:
        # If the method is get, only render index.html / homepage
        return render_template("index.html")


@app.route("/admin", methods=['POST', 'GET', 'DELETE', 'UPDATE'])
def admin():
    """
    Since the admin page contains several features, the methods are added according to the features
    """
    return render_template("admin.html")

# Display data
@app.route("/display_data", methods=["GET"]) # Routing for the display button action
def display_data():
    '''
    - Simply calls the get_employees function and passes the data to the front-end to be displayed
    - Redirects to the admin page with employee data displayed in the table
    '''
    employees = get_employees()
    return render_template("admin.html", employees=employees)

@app.route("/add_data", methods=["GET", "POST"]) # Using the POST method for the submit button action in the HTML file
def add_data():
    # Connection to the database, must be done for each function or transaction; otherwise, an error may occur
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # Request data from the front-end
    employee_name = request.form["nme"]
    position = request.form['position']
    email = request.form['email']
    # If any input is empty, display a message and a back button
    if employee_name == "" or position == "" or email == "":
        cursor.close()

        # Message and button directed to display data (ultimately to admin), with the goal of displaying data without pressing the display button
        return """Please input Non Null Data 
                    <form id="logout_button" action="/display_data" method="get">
                        <p><input type="submit" value='back'/></p>
                    </form>"""
    else:
        # If the fields are complete, execute the query
        cursor.execute("""INSERT INTO employees (name, position, email)
                   VALUES(? , ?, ?)""", (employee_name, position, email)
        )
        conn.commit()
        cursor.close()

        # Data is automatically displayed after pressing the submit button
        return redirect(url_for("display_data"))
    

@app.route("/delete_data", methods=["GET", "POST"])
def delete_data():
    # Connection
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # Request id or employee name
    deleted_id = request.form["deleted_employee"]
    
    # Try to delete based on id
    cursor.execute("DELETE FROM employees WHERE id=?", (deleted_id,))

    # If no rows are deleted based on id, then try searching using the name keyword
    if cursor.rowcount == 0:

        # SQL
        cursor.execute("DELETE FROM employees WHERE name=?", (deleted_id,))

        # If there are no rows deleted based on name, display a message and a back button.
        if cursor.rowcount == 0:
            return f"""No data found with ID or Name: {deleted_id}
                    <form id="logout_button" action="/display_data" method="get">
                        <p><input type="submit" value='back'/></p>
                    </form>
                    """
    conn.commit()
    cursor.close()

    # Data is automatically updated
    return redirect(url_for("display_data"))

@app.route("/update_data", methods=["GET", "POST"])
def update_data():

    # Connection
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # Request input from the front-end
    ID = request.form['id_update']
    name = request.form['name_update']
    position = request.form['position_update']
    email = request.form['email_update']

    # The key to finding the data is in the id
    cursor.execute("""UPDATE employees
                       SET name = ?, position = ?, email = ?
                       WHERE id = ?
                       """, (name, position, email, ID))
    # Run the query
    conn.commit()

    # If there are no rows affected based on input, display a message and a back button
    if cursor.rowcount == 0:
        return f"""No data found with ID: {ID}
            <form id="logout_button" action="/display_data" method="get">
                <p><input type="submit" value='back'/></p>
            </form>
        """
    else:
        # If the Id is found, it will be updated
        cursor.execute("""UPDATE employees
                       SET name = ?, position = ?, email = ?
                       WHERE id = ?      
                       """, (name, position, email, ID))
        conn.commit()
        cursor.close()

        # Data is automatically updated
        return redirect(url_for("display_data")) 


if __name__== "__main__":
    app.run(debug=True)
