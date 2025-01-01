# Network-Security-Spyware-Project

Spyware project for TNM031 Network Programming and Security course

This is for educational purposes only.

## Description

This project consists of a server and a client application. The server listens for incoming connections from clients and handles messages, including image data. The client can send keypress data and screenshots to the server.

## Features

- Keylogger: Captures keypresses on the client machine and sends them to the server.
- Screenshot: Captures screenshots from the client machine and sends them to the server.
- Multi-client support: The server can handle multiple clients simultaneously.

## Setup

### Server

1. Ensure you have Python installed on your machine.
2. Install the required libraries:
    ```bash
    pip install opencv-python keyboard
    ```
3. Run the server:
    ```bash
    python server.py
    ```

### Client

1. Ensure you have Python installed on your machine.
2. Install the required libraries:
    ```bash
    pip install opencv-python keyboard
    ```
3. Run the client:
    ```bash
    python client_compressed2.py
    ```

## Usage

1. Start the server on the host machine.
2. Start the client on the target machine.
3. The client will attempt to connect to the server automatically.
4. The server will receive keypress data and screenshots from the client.

## Disclaimer

This project is intended for educational purposes only. Unauthorized use of this software to monitor or control another person's computer without their knowledge and consent is illegal and unethical.
