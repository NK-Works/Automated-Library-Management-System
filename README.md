# Raspberry Pi Based Automated Library Management System 📚🔧

In the modern educational landscape, libraries play a pivotal role in the learning process. However, traditional library management methods have proven to be inefficient and are often fraught with challenges. To address these issues, we embarked on a mission to create a more efficient, automated, and secure library management system using Raspberry Pi. 🚀

## Features ✨

- **Automated Book Issuance and Return**: Streamlined process with reduced manual intervention.
- **Anti-theft Measures**: 🚨 Integrated IR sensors to prevent unauthorized book removal.
- **Real-time Database Management**: MySQL database for accurate book and user records.
- **User-friendly Interface**: TFT Display for intuitive user interaction.
- **Email Notifications**: 📧 Automated notifications for due dates and fines.
- **Expandable System**: Built with scalability in mind for future enhancements.

## Hardware Requirements 🛠️

- Raspberry Pi 4 Model B
- IR Sensors, Raspberry Pi Camera Module 📷
- TFT Display, Arduino Nano 33 IoT
- Additional: Arduino UNO, Jumper Wires, Breadboard

## Software Requirements 🖥️

- Raspberry Pi Buster/Bullseye OS
- Python 2/3, MySQL Database
- OpenCV, pyzbar, mysql.connector
- Tkinter for GUI, smtplib for Email

## Setup Instructions 📋

1. **Hardware Setup**: Connect Raspberry Pi with IR sensors, camera, TFT display, and Arduino components.
2. **Software Setup**: Install necessary libraries like OpenCV, pyzbar, and mysql.connector on Raspberry Pi.
3. **Database Configuration**: Set up MySQL database using provided commands in `mariadb-database-commands.pdf`.
4. **Code Installation**: Clone the repository and configure `app.py` with your database credentials and SMTP server details.
5. **Arduino Remote Setup**: Upload `backend.ino` to Arduino Nano 33 IoT for adding users/books.
6. **Run the System**: Execute `app.py` on Raspberry Pi to start the automated library management system.

## Additional Notes ℹ️

- For hands-on guidance on how to make this project, you can check out my [YouTube video](https://youtu.be/134aHhCnCaM).
- Contributions and feedback are welcome! Feel free to fork the repository and submit pull requests.

## Consider 🌟 the repository to show some love 🙏

## THANK YOU :)
