package ru.team1802.mypostmail.services;

import java.util.regex.Pattern;

public class ValidationService {
    private static final String emailPattern = "^\\S+@\\S+\\.\\S+$";
    private static final String passwordPattern = "^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#&()–[{}]:;',?/*~$^+=<>]).{8,20}$";

    public static boolean isEmailValid(String emailAddress) {
        return Pattern.compile(emailPattern)
                .matcher(emailAddress)
                .matches();
    }

    public static boolean isPasswordValid(String password) {
        return Pattern.compile(passwordPattern)
                .matcher(password)
                .matches();
    }

}
