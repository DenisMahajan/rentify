# Rentify

Rentify is a web application designed to simplify the process of finding a rental property for tenants and connecting property owners with potential tenants. It provides a platform where tenants can browse available properties and contact property owners directly.

## Features

- **User Authentication**: Users can sign up and log in securely to access the platform.
- **Property Listings**: Property owners can post details about their properties, including images, location, rent, and more.
- **Explore**: Tenants can browse available properties.
- **Contact Property Owners**: Tenants can request more information about a property by contacting the property owner via email.
- **User Profiles**: Users can view and update their profile information.

## Technologies Used

- **Flask**: Python web framework used for backend development.
- **MySQL**: Relational database management system for storing user and property data.
- **Flask-Mail**: Extension for Flask used for sending emails.
- **Werkzeug**: Utility library for secure file uploads and password hashing.
- **HTML/CSS/JavaScript**: Frontend technologies for building the user interface.

## Getting Started

To run Rentify locally, follow these steps:

1. Clone the repository:

    ```bash
    git clone <repository_url>
    cd rentify
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables:

    - Create a `.env` file in the root directory.
    - Add the following environment variables:

        ```plaintext
        MYSQL_HOST=<your_mysql_host>
        MYSQL_USER=<your_mysql_user>
        MYSQL_PASSWORD=<your_mysql_password>
        MYSQL_DB=<your_mysql_database>
        MAIL_USERNAME=<your_email_address>
        MAIL_PASSWORD=<your_email_password>
        ```

4. Create the necessary database tables. You can use the provided SQL schema to create the tables in your MySQL database.

5. Run the application:

    ```bash
    python app.py
    ```

6. Access Rentify in your web browser at `http://localhost:5000`.


## Contributing

Contributions to Rentify are welcome! Feel free to submit bug reports, feature requests, or pull requests to help improve the project.
