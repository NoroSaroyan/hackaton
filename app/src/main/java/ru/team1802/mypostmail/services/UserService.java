package ru.team1802.mypostmail.services;

import java.util.Objects;

public class UserService {
    private boolean authenticate(String username, String password) {
//        Getting username from db
//        Getting password from db
        return Objects.equals(username, "aaaa") && Objects.equals(password, "aaaa");
    }
}
