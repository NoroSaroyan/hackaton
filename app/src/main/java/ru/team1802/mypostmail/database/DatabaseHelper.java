package ru.team1802.mypostmail.database;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseHelper {
    private static final String DATABASE_URL = "jdbc:mysql://your-mysql-host:your-mysql-port/your-database-name";
    private static final String USERNAME = "your-username";
    private static final String PASSWORD = "your-password";

    public static Connection getConnection() {
        Connection connection = null;
        try {
            Class.forName("com.mysql.jdbc.Driver");
            connection = DriverManager.getConnection(DATABASE_URL, USERNAME, PASSWORD);
        } catch (ClassNotFoundException | SQLException e) {
            e.printStackTrace();
        }
        return connection;
    }
}
