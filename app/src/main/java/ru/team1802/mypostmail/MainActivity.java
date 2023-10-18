package ru.team1802.mypostmail;

import android.content.Intent;
import android.os.Bundle;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    TextView buttonLogin;
    TextView buttonRegister;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        buttonLogin = findViewById(R.id.button_main_login);
        buttonRegister = findViewById(R.id.button_main_register);

        buttonLogin.setOnClickListener(view -> startActivity(new Intent(this, LoginActivity.class)));
        buttonRegister.setOnClickListener(view -> startActivity(new Intent(this, RegisterActivity.class)));
    }
}
