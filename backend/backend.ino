/* This is the final code for SIT210 - Final Project */
/*             Made by Team Embed Tech               */
/*     Automated Library Management System Code      */
/*  By Anneshu Nag, Anshpreet Singh, Gaganveer Singh */

/* This is the Arduino Code to add a new user to database */
#include <WiFiNINA.h>

char ssid[] = "Your Network SSID";      // your network SSID (name)
char pass[] = "Your Password";        // your network password
int status = WL_IDLE_STATUS;     // the WiFi radio's status

char server[] = "RaspberryPi IP-Address"; // Replace with your Raspberry Pi's IP address

WiFiClient client;

void setup() {
  Serial.begin(9600);
  
  // Check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    while (true);
  }

  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
    delay(10000);
  }
  Serial.println("Connected to WiFi!");
  Serial.println("Enter name to add a user");
}

void loop() {
  if (Serial.available()) {
    // Read input from the serial monitor until a newline character is encountered.
    String input = Serial.readStringUntil('\n');
    
    // Find the positions of two semicolons in the input string.
    int separator1 = input.indexOf(';');
    int separator2 = input.lastIndexOf(';');
    
    if(separator1 != -1 && separator2 != -1 && separator1 != separator2) {
      // Extract values between semicolons.
      String lid = input.substring(0, separator1);
      String username = input.substring(separator1 + 1, separator2);
      String email = input.substring(separator2 + 1);
      
      // Call the addUser function with the extracted values.
      addUser(lid, username, email);
    }
    else {
      Serial.println("Invalid format. Please enter in the format: lid;username;email");
    }
  }
}

// URL-encode a string to be used in an HTTP request.
String urlEncode(const String &s) {
  const char *hex = "0123456789abcdef";
  String encoded = "";
  
  for (char c : s) {
    if ('a' <= c && c <= 'z' || 'A' <= c && c <= 'Z' || '0' <= c && c <= '9') {
      encoded += c;
    } else {
      encoded += '%';
      encoded += hex[c >> 4];
      encoded += hex[c & 15];
    }
  }
  return encoded;
}

// Send a GET request to the server to add a user.
void addUser(String lid, String username, String email) {
  if (client.connect(server, 80)) {
    Serial.println("Connected to server!");

    // URL-encode the input values.
    String encodedLid = urlEncode(lid);
    String encodedName = urlEncode(username);
    String encodedEmail = urlEncode(email);
    
    // Construct the URL with encoded values.
    String url = "/add_user.php?lid=" + encodedLid + "&name=" + encodedName + "&email=" + encodedEmail;

    // Send an HTTP GET request to the server.
    client.print("GET ");
    client.print(url);
    client.println(" HTTP/1.1");
    client.println("Host: " + String(server));
    client.println("Connection: close");
    client.println();

    // Read and print the server's response.
    while(client.connected()) {
      if (client.available()) {
        char c = client.read();
        Serial.print(c);
      }
    }
    client.stop();
  } else {
    Serial.println("Failed to connect to server");
  }
}
