package com.domain.pborisenko.scasandbox;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.support.v7.internal.widget.AdapterViewCompat;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;

public class MainActivity extends ActionBarActivity {

    private final static String TAG = "MainActivity";
    private final static String NO_ALG_SELECTED = "Please choose an algorithm!";

    private Algorithm selectedAlgorithm;
    private ListView algorithmsList;
    private AsyncEncryption currentEncryptionTask;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        algorithmsList = (ListView) findViewById(R.id.algorithms_list);
        ArrayList<String> stringAlgorithmsList = new ArrayList<String>();
        for (Algorithm i : Algorithm.values()) {
            stringAlgorithmsList.add(i.name());
            Log.d(TAG, i.name() + " algorithm is supported.");
        }
        ArrayAdapter<String> adapter = new ArrayAdapter<String>(this, R.layout.algorithm_list_item,
                stringAlgorithmsList);
        algorithmsList.setAdapter(adapter);
        algorithmsList.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                view.setSelected(true);
                TextView t = (TextView) view;
                selectedAlgorithm = Algorithm.valueOf(t.getText().toString());
            }
        });

        Button fab = (Button) findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (selectedAlgorithm != null) {;
                    //create async task for trace recording
                    Log.d(TAG, "Async process creation for trace recording ...");
                    currentEncryptionTask = new AsyncEncryption(MainActivity.this);
                    currentEncryptionTask.execute(selectedAlgorithm);
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
        TDES,
        RSA,
        AES,
        DES
    }
}