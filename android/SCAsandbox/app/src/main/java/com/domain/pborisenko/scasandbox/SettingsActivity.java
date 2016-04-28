package com.domain.pborisenko.scasandbox;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.NumberPicker;
import android.widget.Toast;

/**
 * Created by pborisenko on 3/22/2016.
 */

public class SettingsActivity extends ActionBarActivity {

    private final static String PREFS = "com.domain.pborisenko.scasandbox";
    private final static String PARMS_ERROR = "Please fix the parameters!";
    private final static String DELAY_PARM = "delay";
    private final static String PLAINTEXT_LENGTH_PARM = "plaintext_length";
    private final static String SIGNATURE_COUNTER = "signature_counter";
    private final static String SIGNATURE_COUNTER_FLAG = "signature_counter_flag";

    private NumberPicker mPicker;
    private Button mOkButton;
    private CheckBox mCheckBox;
    private EditText mPlaintextInput;
    private SharedPreferences sharedPref;
    private EditText mSignatureCounterInput;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        Intent intent = getIntent();
        sharedPref = getSharedPreferences(PREFS, Context.MODE_PRIVATE);

        mPicker = (NumberPicker) findViewById(R.id.delay_setting_picker);
        mPicker.setMinValue(1);
        mPicker.setMaxValue(10);
        mOkButton = (Button) findViewById(R.id.settings_ok_button);
        mPlaintextInput = (EditText) findViewById(R.id.plaintext_length_input_window);
        mPlaintextInput.setText(Integer.toString(sharedPref.getInt(PLAINTEXT_LENGTH_PARM, 128)));
        mSignatureCounterInput = (EditText) findViewById(R.id.known_signature_count_input_window);
        mSignatureCounterInput.setText(Integer.toString(sharedPref.getInt(SIGNATURE_COUNTER, 10)));
        mCheckBox = (CheckBox) findViewById(R.id.known_signature_flag);
        mCheckBox.setChecked(sharedPref.getBoolean(SIGNATURE_COUNTER_FLAG, false));


        mOkButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                SharedPreferences.Editor editor = sharedPref.edit();
                try {
                    editor.putInt(DELAY_PARM, mPicker.getValue());
                    editor.putInt(PLAINTEXT_LENGTH_PARM, Integer.parseInt(mPlaintextInput.getText().toString()));
                    editor.putInt(SIGNATURE_COUNTER, Integer.parseInt(mSignatureCounterInput.getText().toString()));
                    editor.putBoolean(SIGNATURE_COUNTER_FLAG, mCheckBox.isChecked());
                } catch (Exception e) {
                    e.printStackTrace();
                    Toast.makeText(SettingsActivity.this, PARMS_ERROR, Toast.LENGTH_SHORT).show();
                }
                editor.commit();

                Intent intent = new Intent(SettingsActivity.this, MainActivity.class);
                startActivity(intent);
            }
        });

    }
}