package com.domain.pborisenko.scasandbox;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.ViewGroup.LayoutParams;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends ActionBarActivity {

    private final static String TAG = "MainActivity";
    private final static String NO_ALG_SELECTED = "Please choose an algorithm!";

    private View selectedAlgorithm;
    private LinearLayout algorithmsList;
    private AsyncEncryption currentEncryptionTask;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        //fill the list of supported algorithms
        algorithmsList = (LinearLayout) findViewById(R.id.algorithms_list);
        for (Algorithm i : Algorithm.values()) {
            TextView t = new TextView(this);
            t.setText(i.name());
            t.setLayoutParams(new LayoutParams(LayoutParams.FILL_PARENT,LayoutParams.WRAP_CONTENT));
            t.setTag(i);
            t.setBackgroundColor(getResources().getColor(R.color.colorUnSelectedAlgorithm));
            t.setTextSize(R.dimen.text_height);
            t.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    if (!v.isSelected()) {
                        for (int i = 0; i < algorithmsList.getChildCount(); i++) {
                            View cv = algorithmsList.getChildAt(i);
                            cv.setSelected(false);
                            v.setBackgroundColor(getResources().getColor(R.color.colorUnSelectedAlgorithm));
                        }
                        v.setSelected(true);
                        v.setBackgroundColor(getResources().getColor(R.color.colorSelectedAlgorithm));
                        selectedAlgorithm = v;
                    }
                }
            });
            algorithmsList.addView(t);
            Log.d(TAG, t.getText() + " algorithm is supported.");
        }

        algorithmsList.invalidate();

        //temporary fix:
        selectedAlgorithm = new TextView(this);
        selectedAlgorithm.setTag(Algorithm.TDES);

        Button fab = (Button) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (selectedAlgorithm != null) {;
                    //create async task for trace recording
                    Log.d(TAG, "Async process creation for trace recording ...");
                    currentEncryptionTask = new AsyncEncryption(MainActivity.this);
                    currentEncryptionTask.execute((Algorithm) selectedAlgorithm.getTag());
                } else {
                    Toast.makeText(MainActivity.this, NO_ALG_SELECTED, Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();

        if (id == R.id.action_settings) {
            Intent intent = new Intent(this, SettingsActivity.class);
            startActivity(intent);
        }
        return super.onOptionsItemSelected(item);
    }

    public enum Algorithm {
        TDES
    }
}