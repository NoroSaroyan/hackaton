package ru.team1802.mypostmail;

import android.os.Bundle;
import android.widget.EditText;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

public class RegisterActivity extends AppCompatActivity {

    EditText loginField;
    EditText passwordField;
    EditText repeatPasswordField;
    TextView buttonRegister;

    String login;
    String password;
    String repeatedPassword;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_register);

        loginField = findViewById(R.id.reg_login_field);
        passwordField = findViewById(R.id.reg_password_field);
        repeatPasswordField = findViewById(R.id.repeat_password_field);
        buttonRegister = findViewById(R.id.button_register);

        buttonRegister.setOnClickListener(view -> {
            login = loginField.getText().toString();
            password = passwordField.getText().toString();
            repeatedPassword = repeatPasswordField.getText().toString();
        });
    }
}
