package com.domain.pborisenko.scasandbox;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.PersistableBundle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.View;
import android.widget.Button;
import android.widget.NumberPicker;

/**
 * Created by pborisenko on 3/22/2016.
 */
public class SettingsActivity extends AppCompatActivity {

    private final static String PREFS = "com.domain.pborisenko.scasandbox";
    private final static String DELAY_PARM = "delay";

    private NumberPicker mPicker;
    private Button mOkButton;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        Intent intent = getIntent();

        mPicker = (NumberPicker) findViewById(R.id.delay_setting_picker);
        mPicker.setMinValue(1);
        mPicker.setMaxValue(10);
        mOkButton = (Button) findViewById(R.id.settings_ok_button);

        mOkButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                SharedPreferences sharedPref = getSharedPreferences(PREFS, Context.MODE_PRIVATE);
                SharedPreferences.Editor editor = sharedPref.edit();
                editor.putInt(DELAY_PARM, mPicker.getValue());
                editor.commit();

                Intent intent = new Intent(SettingsActivity.this, MainActivity.class);
                startActivity(intent);
            }
        });

    }
}