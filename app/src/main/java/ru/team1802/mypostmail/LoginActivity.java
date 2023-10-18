package ru.team1802.mypostmail;

import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

public class LoginActivity extends AppCompatActivity {

    //Создание объектов интерфейса
    EditText loginField;
    EditText passwordField;
    TextView forgotPassword;
    Button buttonLogin;

    String login;
    String password;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        //Поиск обектов интерфейса по их id
        loginField = findViewById(R.id.login_field);
        passwordField = findViewById(R.id.password_field);
        forgotPassword = findViewById(R.id.forgot_password);
        buttonLogin = findViewById(R.id.button_login);

        buttonLogin.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                //Считывание данных с полей ввода и запись в переменные
                login = loginField.getText().toString();
                password = passwordField.getText().toString();

                //Код который выполняется при нажатии на кнопку "Войти"
            }
        });
    }

}