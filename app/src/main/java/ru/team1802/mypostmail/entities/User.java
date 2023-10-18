package ru.team1802.mypostmail.entities;

import androidx.annotation.NonNull;

import javax.persistence.Column;
import javax.persistence.Id;
import javax.persistence.Table;

@Table(schema = "users")
public class User {
    public long getId() {
        return id;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    //    public String getPhoneNumber() {
//        return phoneNumber;
//    }
//
//    public void setPhoneNumber(String phoneNumber) {
//        this.phoneNumber = phoneNumber;
//    }
    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    @Id
    @Column(name = "id", unique = true)
    private Long id;
    @Column(name = "username")
    private String username;
    @Column(name = "password")
    private String password;
    //    @Column()
//    private String phoneNumber;
    @Column(name = "email")
    private String email;

    public User(String username, String password, String email) {
        setEmail(email);
        setUsername(username);
        setPassword(password);
    }

    @NonNull
    @Override
    public String toString() {
        return "User{" +
                "username='" + username + '\'' +
                ", password='" + password + '\'' +
                ", email='" + email + '\'' +
                '}';
    }
}
