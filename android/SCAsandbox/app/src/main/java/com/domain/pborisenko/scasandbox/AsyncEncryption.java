package com.domain.pborisenko.scasandbox;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.util.Log;
import android.widget.Toast;

import com.domain.pborisenko.scasandbox.MainActivity.Algorithm;

import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStreamWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

/**
 * Created by pborisenko on 3/13/2016.
 */

public class AsyncEncryption extends AsyncTask<Algorithm, Void, Integer> {

    private final static String TAG = "AsyncEncryption";

    private final static String TDES_INSTANCE = "DESede/ECB/NoPadding";
    private final static String RSA_INSTANCE  = "RSA/ECB/NoPadding";
    private final static String AES_INSTANCE  = "AES/ECB/NoPadding";
    private final static String DES_INSTANCE  = "DES/ECB/NoPadding";

    private final static String RET_CODE_1 = "Configuration file is missing";
    private final static String RET_CODE_2 = "Encryption failed. Please turn on debug to investigate.";
    private final static String RET_CODE_3 = "Error writing to timestamp file.";
    private final static String RET_CODE_4 = "Can't create or delete timestamp file.";
    private final static String PLEASE_CREATE = "Please create it in ";
    private final static String PREFS = "com.domain.pborisenko.scasandbox";
    private final static String TIMESTAMP_FILENAME = "SCASandbox_stamp.csv";

    private Activity mActivity;
    private Integer delayTime = 1;
    private Integer plaintextLegth = 128;
    private Integer signatureCounter = 10;
    private Boolean countSignatures = false;
    private AlertDialog mAld;
    private List<byte[]> plainTexts = new ArrayList<byte[]>();
    private List<SecretKey> secretKeys = new ArrayList<SecretKey>();
    private List<IvParameterSpec> initialVectors = new ArrayList<IvParameterSpec>();
    private int retCode = 0;
    private FileOutputStream outputStream;
    private OutputStreamWriter outputStreamWriter;
    private long time_start;
    private long time_end;
    private Boolean randomPlainTexts = false;
    private Boolean randomKeys = false;
    private Boolean continueWriting = true;
    private File targetFile;
    private Algorithm alg;
    private String algorithmInstance;

    public AsyncEncryption (Activity activity){
        mActivity = activity;
    }

    protected Integer doInBackground(Algorithm...parms) {
        Log.d(TAG, "doInBackground ...");
        try {
            alg = parms[0];
            Configuration conf = new Configuration(alg);
            if (retCode != 0) {
                return retCode;
            } else {
                initComponents(conf, alg);
            }
            if (retCode != 0) {
                return retCode;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        try {
            targetFile = new File(mActivity.getExternalFilesDir(null), TIMESTAMP_FILENAME);
            Boolean result;
            result = targetFile.delete();
            result = targetFile.createNewFile();

            if (!result) {
                retCode = 3;
                return retCode;
            }

            outputStream = new FileOutputStream(targetFile);
            outputStreamWriter = new OutputStreamWriter (outputStream);

        } catch (Exception e) {
            e.printStackTrace();
            retCode = 3;
        }

        if (retCode != 0) {
            return null;
        }

        String str;
        Integer signatureIterator = 0;

                while (continueWriting) {

                    if (countSignatures && signatureIterator.equals(signatureCounter)) {
                        byte[] randomKey;
                        if (randomPlainTexts) {
                            plainTexts.clear();
                            plainTexts.add(hexStringToByteArray(getRandomHexString(
                                    Math.round(plaintextLegth / 4))));
                        }
                        if (randomKeys) {
                            secretKeys.clear();
                            randomKey = hexStringToByteArray(getRandomHexString(Math.round(128 / 4)));
                            secretKeys.add(new SecretKeySpec(randomKey,
                                    0, randomKey.length, alg.name()));
                        }
                    } else {
                        signatureIterator += 1;
                    }

                    for (byte [] s : plainTexts) {
                        for (SecretKey k : secretKeys) {
                                Cipher cipher;
                                try {
                                    cipher = Cipher.getInstance(algorithmInstance);
                                    cipher.init(Cipher.ENCRYPT_MODE, k);
                                    //time_start = System.currentTimeMillis();
                                    time_start = System.nanoTime();
                                    byte[] cipherText = cipher.doFinal(s);
                                    //time_end = System.currentTimeMillis();
                                    time_end = System.nanoTime();

                                    Thread.sleep(1000 * delayTime / 2);

                                    str = bytesToHex(s) + ","
                                            + bytesToHex(k.getEncoded()) + ","
                                            + bytesToHex(cipherText) + ","
                                            + Long.toString(time_start) + "\n"
                                            + bytesToHex(s) + ","
                                            + bytesToHex(k.getEncoded()) + ","
                                            + bytesToHex(cipherText) + ","
                                            + Long.toString(time_end) + "\n";
                                    outputStreamWriter.write(str);

                                    Log.d(TAG, "Encrypted: "
                                            + bytesToHex(s) + ","
                                            + bytesToHex(k.getEncoded()) + ","
                                            + bytesToHex(cipherText)
                                            + "," + Long.toString(time_start));
                                    Log.d(TAG, "Encrypted: "
                                            + bytesToHex(s) + ","
                                            + bytesToHex(k.getEncoded()) + ","
                                            + bytesToHex(cipherText)
                                            + "," + Long.toString(time_end));

                                    Thread.sleep(1000 * delayTime / 2);
                                } catch (Exception e) {
                                    retCode = 2;
                                    e.printStackTrace();
                                    return null;
                            }
                        }
                    }
        }

        try {
            outputStreamWriter.close();
        } catch (Exception e) {
            e.printStackTrace();
            retCode = 3;
        }

        return retCode;
    }

    @Override
    protected void onPreExecute() {
        super.onPreExecute();

        mAld = new AlertDialog.Builder(mActivity)
                .setTitle(R.string.stop_recording)
                .setMessage("Are you sure you want to stop recording?")
                .setPositiveButton(R.string.stop_recording_button, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int which) {
                        continueWriting = false;
                        Log.d(TAG, "Trace recording was cancelled.");
                    }
                })
                .setIcon(android.R.drawable.ic_dialog_alert)
                .show();
    }

    protected void onPostExecute(Integer rc) {
        Log.d(TAG, "onPostExecute ...");

        switch (retCode) {
            case 0:
                Log.d(TAG, "File path: " + targetFile.getAbsolutePath());
                Toast.makeText(mActivity, targetFile.getAbsolutePath(), Toast.LENGTH_LONG).show();
                return;
            case 1:
                mAld.cancel();
                Toast.makeText(mActivity, RET_CODE_1, Toast.LENGTH_LONG).show();
                Toast.makeText(mActivity, PLEASE_CREATE + mActivity.getExternalFilesDir(null),
                        Toast.LENGTH_SHORT).show();
                Log.d(TAG, RET_CODE_1);
            case 2:
                mAld.cancel();
                Toast.makeText(mActivity, RET_CODE_2, Toast.LENGTH_LONG).show();
                Log.d(TAG, RET_CODE_2);
            case 3:
                mAld.cancel();
                Toast.makeText(mActivity, RET_CODE_3, Toast.LENGTH_LONG).show();
                Log.d(TAG, RET_CODE_3);
            case 4:
                mAld.cancel();
                Toast.makeText(mActivity, RET_CODE_4, Toast.LENGTH_LONG).show();
                Log.d(TAG, RET_CODE_4);
        }

    }

    private Void initComponents(Configuration config,
                                Algorithm alg) throws Exception {
        if (retCode != 0) {
            return null;
        }

        Log.d(TAG, "Components initiation ...");
        // plain texts
        for (String i : config.plainTexts) {
            plainTexts.add(hexStringToByteArray(i));
        }
        // keys
        for (String i : config.keys) {
            byte[] encodedKey = hexStringToByteArray(i);
            secretKeys.add(new SecretKeySpec(encodedKey, 0, encodedKey.length, alg.name()));
        }
        // initialization vectors
        for (String i : config.ivs) {
            initialVectors.add(new IvParameterSpec(hexStringToByteArray(i)));
        }

        if (plainTexts.isEmpty()) {
            randomPlainTexts = true;
            Log.d(TAG, "Plain texts will be random.");
        }

        if (secretKeys.isEmpty()) {
            randomKeys = true;
            Log.d(TAG, "Keys will be random.");
        }

        switch (alg) {
            case TDES:
                algorithmInstance = TDES_INSTANCE;
            case RSA:
                algorithmInstance = RSA_INSTANCE;
            case AES:
                algorithmInstance = AES_INSTANCE;
            case DES:
                algorithmInstance = DES_INSTANCE;
            default:
                algorithmInstance = TDES_INSTANCE;
        }

        return null;
    }

    private class Configuration {

        private final static String CONFIG = "_SCAconfig.xml";
        private final static String KEY_NODE = "Key";
        private final static String PLAINTEXT_NODE = "Plaintext";
        private final static String IV_NODE = "InitialVector";
        private final static String DELAY_PARM = "delay";
        private final static String PLAINTEXT_LENGTH_PARM = "plaintext_length";
        private final static String SIGNATURE_COUNTER = "signature_counter";
        private final static String SIGNATURE_COUNTER_FLAG = "signature_counter_flag";

        public List<String> plainTexts = new ArrayList<String>();
        public List<String> ivs = new ArrayList<String>();
        public List<String> keys = new ArrayList<String>();

        private Configuration (Algorithm alg) {
            Log.d(TAG, "In config constructor ...");
            File file;
            try {
                file = new File(mActivity.getExternalFilesDir(null), alg.name() + CONFIG);

                if (!file.exists()) {
                    retCode = 1;
                    Log.d(TAG, RET_CODE_1 + ": " + mActivity.getExternalFilesDir(null) + "/"
                            + alg.name() + CONFIG);
                    return;
                }

                InputStream is = new FileInputStream(file.getPath());
                DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
                DocumentBuilder db = dbf.newDocumentBuilder();
                Document doc = db.parse(new InputSource(is));
                doc.getDocumentElement().normalize();
                NodeList nodeList;

                nodeList = doc.getElementsByTagName(KEY_NODE);
                for (int i = 0; i < nodeList.getLength(); i++) {
                    Node node = nodeList.item(i);
                    keys.add(node.getTextContent());
                }

                nodeList = doc.getElementsByTagName(PLAINTEXT_NODE);
                for (int i = 0; i < nodeList.getLength(); i++) {
                    Node node = nodeList.item(i);
                    plainTexts.add(node.getTextContent());
                }

                switch (alg) {
                    case TDES: {
                        nodeList = doc.getElementsByTagName(IV_NODE);
                        for (int i = 0; i < nodeList.getLength(); i++) {
                            Node node = nodeList.item(i);
                            ivs.add(node.getTextContent());
                        }
                    }
                }

                Log.d(TAG, PLAINTEXT_NODE + " - " + Integer.toString(plainTexts.size()) + " elements.");
                Log.d(TAG, KEY_NODE + " - " + Integer.toString(keys.size()) + " elements.");
                Log.d(TAG, IV_NODE + " - " + Integer.toString(ivs.size()) + " elements.");

            } catch (Exception e) {
                e.printStackTrace();
            }

            SharedPreferences prefs = mActivity.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
            delayTime = prefs.getInt(DELAY_PARM, 1);
            plaintextLegth = prefs.getInt(PLAINTEXT_LENGTH_PARM, 128);
            signatureCounter = prefs.getInt(SIGNATURE_COUNTER, 10);
            countSignatures = prefs.getBoolean(SIGNATURE_COUNTER_FLAG, false);

            if (countSignatures) {
                randomKeys = true;
                randomPlainTexts = true;
            }

        }
    }

    public static byte[] hexStringToByteArray(String s) {
        int len = s.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(s.charAt(i), 16) << 4)
                    + Character.digit(s.charAt(i+1), 16));
        }
        return data;
    }

    public static String bytesToHex(byte[] bytes) {
        final char[] hexArray = "0123456789ABCDEF".toCharArray();
        char[] hexChars = new char[bytes.length * 2];
        for ( int j = 0; j < bytes.length; j++ ) {
            int v = bytes[j] & 0xFF;
            hexChars[j * 2] = hexArray[v >>> 4];
            hexChars[j * 2 + 1] = hexArray[v & 0x0F];
        }
        return new String(hexChars);
    }

    private String getRandomHexString(int numchars){
        Random r = new Random();
        StringBuffer sb = new StringBuffer();
        while(sb.length() < numchars){
            sb.append(Integer.toHexString(r.nextInt()));
        }
        return sb.toString().substring(0, numchars);
    }
}