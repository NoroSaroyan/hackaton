//package ru.team1802.mypostmail.dao;
//
//import java.sql.Connection;
//import java.sql.PreparedStatement;
//import java.sql.ResultSet;
//import java.sql.SQLException;
//import java.sql.Statement;
//import java.util.ArrayList;
//import java.util.List;
//
//import ru.team1802.mypostmail.database.DatabaseHelper;
//import ru.team1802.mypostmail.entities.User;
//
//public class UserDAO {
//    private static final String TABLE_NAME = "users";
//
//    public void addUser(User user) {
//        String sql = "INSERT INTO " + TABLE_NAME + " (username, password, email) VALUES (?, ?, ?)";
//        try (Connection connection = DatabaseHelper.getConnection();
//             PreparedStatement statement = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
//            statement.setString(1, user.getUsername());
//            statement.setString(2, user.getPassword());
//            statement.setString(3, user.getEmail());
//            statement.executeUpdate();
//
//            try (ResultSet generatedKeys = statement.getGeneratedKeys()) {
//                if (generatedKeys.next()) {
//                    Long id = generatedKeys.getLong(1);
//                }
//            }
//        } catch (SQLException e) {
//            e.printStackTrace();
//        }
//    }
//
//    public User getUserById(Long id) {
//        String sql = "SELECT * FROM " + TABLE_NAME + " WHERE id = ?";
//        try (Connection connection = DatabaseHelper.getConnection();
//             PreparedStatement statement = connection.prepareStatement(sql)) {
//            statement.setLong(1, id);
//            try (ResultSet resultSet = statement.executeQuery()) {
//                if (resultSet.next()) {
//                    String username = resultSet.getString("username");
//                    String password = resultSet.getString("password");
//                    String email = resultSet.getString("email");
//                    return new User(username, password, email);
//                }
//            }
//        } catch (SQLException e) {
//            e.printStackTrace();
//        }
//        return null;
//    }
//
//    public void updateUser(User user) {
//        String sql = "UPDATE " + TABLE_NAME + " SET username = ?, password = ?, email = ? WHERE id = ?";
//        try (Connection connection = DatabaseHelper.getConnection();
//             PreparedStatement statement = connection.prepareStatement(sql)) {
//            statement.setString(1, user.getUsername());
//            statement.setString(2, user.getPassword());
//            statement.setString(3, user.getEmail());
//            statement.setLong(4, user.getId());
//            statement.executeUpdate();
//        } catch (SQLException e) {
//            e.printStackTrace();
//        }
//    }
//
//    public void deleteUser(Long id) {
//        String sql = "DELETE FROM " + TABLE_NAME + " WHERE id = ?";
//        try (Connection connection = DatabaseHelper.getConnection();
//             PreparedStatement statement = connection.prepareStatement(sql)) {
//            statement.setLong(1, id);
//            statement.executeUpdate();
//        } catch (SQLException e) {
//            e.printStackTrace();
//        }
//    }
//
//    public List<User> getAllUsers() {
//        List<User> userList = new ArrayList<>();
//        String sql = "SELECT * FROM " + TABLE_NAME;
//        try (Connection connection = DatabaseHelper.getConnection();
//             PreparedStatement statement = connection.prepareStatement(sql);
//             ResultSet resultSet = statement.executeQuery()) {
//            while (resultSet.next()) {
//                Long id = resultSet.getLong("id");
//                String username = resultSet.getString("username");
//                String password = resultSet.getString("password");
//                String email = resultSet.getString("email");
//                User user = new User(username, password, email);
//                userList.add(user);
//            }
//        } catch (SQLException e) {
//            e.printStackTrace();
//        }
//        return userList;
//    }
//}
