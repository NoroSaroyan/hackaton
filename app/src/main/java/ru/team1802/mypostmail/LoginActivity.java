package ru.team1802.mypostmail;

import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.widget.EditText;
import android.widget.TextView;

public class LoginActivity extends AppCompatActivity {

    //Создание объектов UI
    EditText loginField;
    EditText passwordField;
    TextView buttonForgotPassword;
    TextView buttonLogin;

    String login;
    String password;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        //Поиск обектов интерфейса по их id
        loginField = findViewById(R.id.login_field);
        passwordField = findViewById(R.id.password_field);
        buttonForgotPassword = findViewById(R.id.forgot_password);
        buttonLogin = findViewById(R.id.button_login);

        buttonLogin.setOnClickListener(view -> {
            //Считывание данных с полей ввода и запись в переменные
            login = loginField.getText().toString();
            password = passwordField.getText().toString();

            //Код который выполняется при нажатии на кнопку "Войти"
        });

        buttonForgotPassword.setOnClickListener(view -> {

        });
    }
}