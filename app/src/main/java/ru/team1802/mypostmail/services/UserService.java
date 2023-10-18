package ru.team1802.mypostmail.services;

import static java.net.Proxy.Type.HTTP;

import java.net.HttpURLConnection;
import java.util.Objects;

public class UserService {
    private boolean authenticate(String username, String password) {
//        Getting username from db
//        Getting password from db
        return Objects.equals(username, "aaaa") && Objects.equals(password, "aaaa");
    }

    private boolean register(String username, String password) {
        // if true -> Db create user
        return ValidationService.isEmailValid(username) && ValidationService.isPasswordValid(password);
    }
}
