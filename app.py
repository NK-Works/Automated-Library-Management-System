# This is the final code for SIT210 - Final Project #
#             Made by Team Embed Tech               #
#     Automated Library Management System Code      #
#  By Anneshu Nag, Anshpreet Singh, Gaganveer Singh #
#           This code is made in Python 2.7         #

# Import necessary libraries and modules
import cv2  # OpenCV for capturing video frames
from pyzbar.pyzbar import decode  # Library for barcode decoding
import mysql.connector  # MySQL connector to interact with the database
import time  # For time-based operations
import RPi.GPIO as GPIO  # Raspberry Pi GPIO library
import smtplib  # Library for sending emails
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import Tkinter as tk  # Tkinter for GUI interface (Note: Tkinter should be replaced with tkinter for Python 3)
from datetime import datetime, date, timedelta  # Import datetime module

# Initialize the camera (assuming you have a camera connected)
cap = cv2.VideoCapture(0)
cap.set(3, 320)
cap.set(4, 240)

# IR sensors configuration
IR_PIN_ISSUE = 5  # IR sensor for book issuance
IR_PIN_RETURN = 6  # IR sensor for book return
GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_PIN_ISSUE, GPIO.IN)
GPIO.setup(IR_PIN_RETURN, GPIO.IN)

# Connect to the MySQL database
db = mysql.connector.connect(
    host="Your Hostname/localhost",
    user="Your Username/root",
    password="Your Database Password",
    database="Your Database Name"
)
cursor = db.cursor()

# Add a message indicating a successful database connection
print("Connected to the database")

# Create an SMTP connection for sending emails
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = 'embeddedsystemssit210@gmail.com'
smtp_password = 'SMTP Email Password'

smtp_server = smtplib.SMTP(smtp_server, smtp_port)
smtp_server.starttls()  # Use TLS encryption

# Log in to your email account
smtp_server.login(smtp_username, smtp_password)
print('SMTP Server connected.')

# Create a Tkinter window
root = tk.Tk()
root.title("Library Management System")

# Set the window size to fit the whole screen
root.attributes('-fullscreen', True)

# Create a label for displaying messages
message_label = tk.Label(root, text="Library Management System", font=("Helvetica", 24), fg="white", bg="black")
message_label.pack(fill=tk.BOTH, expand=True)

# Function to update the message label
def update_message(message, font_size=24):
    message_label.config(text=message, font=("Helvetica", font_size), fg="white", bg="black")
    root.update()

# Function to revert to the initial state
def revert_to_initial_state():
    update_message("Library Management System")
    root.after(20000, update_message, "")  # Clear the message after 20 seconds

# Function to get user information from the database based on user ID
def get_user_info(user_id):
    # Fetch the user's name, email, and fine from the database based on user_id
    fetch_user_query = "SELECT name, email, fine FROM usersdatabase WHERE lid=%s"
    cursor.execute(fetch_user_query, (user_id,))
    user_record = cursor.fetchone()
    if user_record:
        user_name, user_email, user_fine = user_record
    else:
        user_name, user_email, user_fine = "Unknown User", "unknown@example.com", 0.00  # Provide default values
    return user_name, user_email, user_fine

while True:
    book_id = None
    user_id = None
    extra_time = None
    ir_sensor_pin = None

    update_message("Library Management System", font_size=70)
    time.sleep(5)

    # Wait for the user to place their hands in front of the IR sensor (for either issuance or return)
    print("Please place your hands in front of the IR sensor (for issuance or return)...")
    update_message("Please place your hand in front of the IR sensor \n<-For Return \t\tFor Issuance->", 40)

    while not (GPIO.input(IR_PIN_ISSUE) or GPIO.input(IR_PIN_RETURN)):
        time.sleep(1)  # Wait for user presence

    if GPIO.input(IR_PIN_ISSUE):
        ir_sensor_pin = IR_PIN_ISSUE
        print("User detected for book issuance. Scanning for book barcode.")
        update_message("User detected for book issuance. \nScanning for book barcode.", 50)
    else:
        ir_sensor_pin = IR_PIN_RETURN
        print("User detected for book return. Scanning for book barcode.")
        update_message("User detected for book return. \nScanning for book barcode.", 50)

    while time.time() - extra_time < 20 if extra_time else 20:
        # Capture a frame from the camera
        ret, frame = cap.read()

        # Decode barcodes in the frame
        barcodes = decode(frame)

        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type

            # Process the barcode data as needed
            print("Barcode Type: {}, Data: {}".format(barcode_type, barcode_data))
            # update_message("Barcode Type: {}, Data: {}".format(barcode_type, barcode_data))

            # Check if the book exists in the book database
            book_query = "SELECT uid, bookname, available, issuedto, issuedate, returndate FROM bookdatabase WHERE uid=%s"
            book_values = (barcode_data,)
            cursor.execute(book_query, book_values)
            book_record = cursor.fetchone()

            if book_record:
                uid, bookname, available, issuedto, issuedate, returndate = book_record
                if available == 1 and ir_sensor_pin == IR_PIN_ISSUE:
                    print("Book '{}' is available for issuance.".format(bookname))
                    update_message("Book '{}' is available for issuance. \nPlace your ID Card!".format(bookname), 35)
                    book_id = barcode_data
                    extra_time = time.time()  # Reset extra time
                    time.sleep(10)  # Delay for 10 seconds
                elif available == 0 and ir_sensor_pin == IR_PIN_RETURN:
                    print("Book '{}' is available for return.".format(bookname))
                    update_message("Book '{}' is available for return. \nPlace your ID Card!".format(bookname), 35)
                    book_id = barcode_data
                    extra_time = time.time()  # Reset extra time
                    time.sleep(10)  # Delay for 10 seconds
                else:
                    print("Book '{}' is not available for this operation.")
                    # update_message("Book '{}' is not available for this operation.")
                    # Reset book_id and user_id and return to the initial state
                    book_id = None
                    user_id = None
            else:
                print("Book with ID {} not found.")
                # update_message("Book with ID {} not found.")
                # Reset book_id and user_id and return to the initial state
                book_id = None
                user_id = None

        # Prompt for the user's QR code
        if book_id:
            user_detected = False
            start_time = time.time()

            while time.time() - start_time < 20:
                ret, frame = cap.read()
                user_barcodes = decode(frame)
                if user_barcodes:
                    user_id = user_barcodes[0].data.decode('utf-8')
                    user_detected = True
                    break

            if user_detected:
                print("User ID: {}".format(user_id))
                # update_message("User ID: {}".format(user_id))

                if ir_sensor_pin == IR_PIN_ISSUE:
                    # Update the book status in the database for issuance
                    issue_date = datetime.now()
                    return_date = issue_date + timedelta(days=7)

                    update_book_query = "UPDATE bookdatabase SET available=0, issuedto=%s, issuedate=%s, returndate=%s WHERE uid=%s"
                    update_book_values = (user_id, issue_date, return_date, book_id)
                    cursor.execute(update_book_query, update_book_values)
                    db.commit()

                    user_name, user_email, user_fine = get_user_info(user_id)

                    print("Book '{}' issued to {}.".format(book_id, user_id))
                    update_message("Book '{}' issued to {}.\nIssue Date- '{}'\nReturn Date- '{}'".format(bookname, user_name, issue_date, return_date), 40)

                    # Send an email
                    subject = "Book Issued!"
                    message_body = "Congrats! You have issued the book '{}'\nIssue Date- '{}'\nReturn Date- '{}'\n\nRegards!\nTeam Embed-Tech".format(bookname, issue_date, return_date)
                    msg = MIMEMultipart()
                    msg['From'] = smtp_username
                    msg['To'] = user_email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(message_body, 'plain'))
                    smtp_server.sendmail(smtp_username, user_email, msg.as_string())

                    # Increment the 'issued' column for the user in the database
                    increment_issued_query = "UPDATE usersdatabase SET issued = issued + 1 WHERE lid = %s"
                    increment_issued_values = (user_id,)
                    cursor.execute(increment_issued_query, increment_issued_values)
                    db.commit()

                    time.sleep(5)

                    # Display success message
                    update_message("Book Issued successfully!", 60)
                    root.after(5000, update_message, "")  # Clear the success message after 5 seconds

                else:
                    # Check if the user has this book issued
                    check_issued_query = "SELECT uid FROM bookdatabase WHERE uid=%s AND issuedto=%s"
                    check_issued_values = (book_id, user_id)
                    cursor.execute(check_issued_query, check_issued_values)
                    issued_book_record = cursor.fetchone()

                    if issued_book_record:
                        # Check if the book return is overdue
                        current_datetime = datetime.now()
                        # Convert returndate (date) to a datetime object with a time of midnight
                        returndate_datetime = datetime.combine(returndate, datetime.min.time())

                        if current_datetime > returndate_datetime:
                            # Calculate the fine (assuming a fixed fine of $50 for overdue books)
                            fine = 50.0

                            # Update the user's fine in the database
                            update_fine_query = "UPDATE usersdatabase SET fine = fine + %s WHERE lid = %s"
                            update_fine_values = (fine, user_id)
                            cursor.execute(update_fine_query, update_fine_values)
                            db.commit()

                            user_name, user_email, user_fine = get_user_info(user_id)

                            # Notify the user about the fine in the email
                            subject = "Book Returned with Fine"
                            message_body = "You have returned the book '{}' after the return date. A fine of Rs.50 has been applied to your account.\nTotal Fine: Rs.{}\n\nRegards!\nTeam Embed-Tech".format(bookname, user_fine)
                            msg = MIMEMultipart()
                            msg['From'] = smtp_username
                            msg['To'] = user_email
                            msg['Subject'] = subject
                            msg.attach(MIMEText(message_body, 'plain'))
                            smtp_server.sendmail(smtp_username, user_email, msg.as_string())

                            print("Book '{}' returned by '{}' with fine Rs.'{}' due to late return.".format(book_id, user_id, user_fine))
                            update_message("Book '{}' returned by '{}' with fine Rs.'{}' \ndue to late return.".format(book_id, user_id, user_fine), 40)
                        else:
                            # If the book is returned on time, reset the user's fine to zero
                            fine = 0.0
                            user_name, user_email, user_fine = get_user_info(user_id)
                            # Notify the user about the fine in the email
                            subject = "Book Returned on time!"
                            message_body = "Congrats! You have returned the book '{}' on time.\nWe look forward to your next book.\n\nRegards!\nTeam Embed-Tech".format(bookname)
                            msg = MIMEMultipart()
                            msg['From'] = smtp_username
                            msg['To'] = user_email
                            msg['Subject'] = subject
                            msg.attach(MIMEText(message_body, 'plain'))
                            smtp_server.sendmail(smtp_username, user_email, msg.as_string())

                            update_fine_query = "UPDATE usersdatabase SET fine = %s WHERE lid = %s"
                            update_fine_values = (fine, user_id)
                            cursor.execute(update_fine_query, update_fine_values)
                            db.commit()

                            print("Book '{}' returned by {}.".format(book_id, user_id))
                            update_message("Book '{}' returned by {}.".format(bookname, user_name), 40)

                        # Update the book status in the database for return
                        return_book_query = "UPDATE bookdatabase SET available=1, issuedto=NULL, issuedate=NULL, returndate=NULL WHERE uid=%s"
                        return_book_values = (book_id,)
                        cursor.execute(return_book_query, return_book_values)
                        db.commit()

                        # Decrement the 'issued' column for the user in the database
                        decrement_issued_query = "UPDATE usersdatabase SET issued = issued - 1 WHERE lid = %s"
                        decrement_issued_values = (user_id,)
                        cursor.execute(decrement_issued_query, decrement_issued_values)
                        db.commit()

                        time.sleep(5)
                        # Display success message
                        print("Book Returned successfully!", 40)
                        update_message("Book Returned successfully!", 40)
                        time.sleep(5)

                        # root.after(5000, update_message, "")  # Clear the success message after 5 seconds
                        # Reset the book and user IDs and return to the initial state
                        book_id = None
                        user_id = None

                    else:
                        print("Book '{}' not issued to {}. Return operation cancelled.".format(book_id, user_id))
                        update_message("Book '{}' not issued to {}. \nReturn operation cancelled.".format(book_id, user_name), 40)
                        # Reset book_id and user_id and return to the initial state
                        book_id = None
                        user_id = None

            else:
                print("No user detected within 20 seconds.")
                update_message("No user detected within 20 seconds.", 40)
                # Reset book_id and user_id and return to the initial state
                book_id = None
                user_id = None

        # Display the frame with barcode information
        cv2.imshow('Barcode Scanner', frame)

        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Reverting!")
    update_message("Reverting to initial state...", 40)
    # revert_to_initial_state()
    while time.time() - extra_time < 20:
        # Continue to look for QR codes
        ret, frame = cap.read()
        user_barcodes = decode(frame)
        if user_barcodes:
            user_id = user_barcodes[0].data.decode('utf-8')
            print("User ID: {}".format(user_id))
            break

# Release the camera and close the OpenCV window
cap.release()
cv2.destroyAllWindows()

# Close the database connection
cursor.close()
db.close()

# Close the SMTP server
smtp_server.quit()
