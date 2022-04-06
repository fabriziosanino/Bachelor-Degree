package com.example.filtering.viewModel;

import android.app.Application;
import android.app.ProgressDialog;
import android.os.AsyncTask;
import android.util.Log;
import android.widget.ProgressBar;

import androidx.annotation.NonNull;
import androidx.lifecycle.AndroidViewModel;


import com.example.filtering.model.SavedResult;
import com.example.filtering.model.SavedResults;
import com.example.filtering.model.SearchResult;
import com.example.filtering.model.SearchResults;
import com.example.filtering.view.home.searchAdapter.SearchItemsCustomViewAdapter;
import com.example.filtering.view.saved.savedAdapter.SavedItemsCustomViewAdapter;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;

public class NetworkViewModel extends AndroidViewModel {

    private final ProductsLiveData productsLiveData;
    private final ClassifyLiveData classifyLiveData;
    private final SaveResearchLiveData saveResearchLiveData;
    private final ReadResearchLiveData readResearchLiveData;
    private final ResearchDetailsLiveData researchDetailsLiveData;
    private final DeleteResearchLiveData deleteResearchLiveData;
    private ProgressDialog progressDialog;
    private ProgressBar progressBar;
    private SearchResults searchResults;
    private SavedResults savedResults;
    private String productName = "";
    private SearchItemsCustomViewAdapter adapterSearch;
    private SavedItemsCustomViewAdapter adapterSaved;
    private String linkNextPage = "";

    public NetworkViewModel(@NonNull Application application) {
        super(application);

        productsLiveData = new ProductsLiveData();
        classifyLiveData = new ClassifyLiveData();
        saveResearchLiveData = new SaveResearchLiveData();
        readResearchLiveData = new ReadResearchLiveData();
        researchDetailsLiveData = new ResearchDetailsLiveData();
        deleteResearchLiveData = new DeleteResearchLiveData();
        searchResults = new SearchResults();
        savedResults = new SavedResults();
    }

    public ProductsLiveData getProductsLiveData() {
        return productsLiveData;
    }

    public ClassifyLiveData getClassifyLiveData() {
        return classifyLiveData;
    }

    public SaveResearchLiveData getSaveResearchLiveData() {
        return saveResearchLiveData;
    }

    public ReadResearchLiveData getReadResearchLiveData() {
        return readResearchLiveData;
    }

    public ResearchDetailsLiveData getResearchDetailsLiveData() {
        return researchDetailsLiveData;
    }

    public DeleteResearchLiveData getDeleteResearchLiveData() {
        return deleteResearchLiveData;
    }

    public ProgressDialog getProgressDialog() {
        return progressDialog;
    }

    public void setProgressDialog(ProgressDialog p) {
        progressDialog = p;
    }

    public void setProgressDialogMessage(String message) {
        progressDialog.setMessage(message);
    }

    public ProgressBar getProgressBar() {
        return progressBar;
    }

    public void setProgressBar(ProgressBar p) {
        progressBar = p;
    }

    public void setAdapterResearch(SearchItemsCustomViewAdapter adapter) {
        this.adapterSearch = adapter;
    }

    public void setAdapterSaved(SavedItemsCustomViewAdapter adapter) {
        this.adapterSaved = adapter;
    }

    public String getProductName() {
        return productName;
    }

    private JSONArray sentPOSTRequest(String urlServer, JSONObject param) {
        try {
            URL url = new URL(urlServer);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json;charset=UTF-8");
            conn.setRequestProperty("Accept", "application/json");
            conn.setDoOutput(true);
            conn.setDoInput(true);
            conn.setConnectTimeout(300000);  /* 5 minuti di timeout */

            DataOutputStream os = new DataOutputStream(conn.getOutputStream());
            os.writeBytes(param.toString());
            os.flush();
            os.close();

            conn.connect();

            if (conn.getResponseCode() != 200) {
                Log.e("Errore", "Il server non ha risposto in modo corretto!!!");
                return new JSONArray();
            } else {
                String retVal = readIt(conn.getInputStream());
                return new JSONArray(retVal);
            }
        } catch (IOException | JSONException e) {
            e.printStackTrace();
            return new JSONArray();
        }
    }

    private String readIt(InputStream stream) {
        BufferedReader reader = new BufferedReader(new InputStreamReader(stream));
        String line;
        StringBuilder result = new StringBuilder();

        try {
            while ((line = reader.readLine()) != null)
                result.append(line).append("\n");
        } catch (IOException e) {
            e.printStackTrace();
        }

        return result.toString();
    }

    public void serachProducts(JSONObject param, String productName, boolean firstTimeFindMore) {
        this.productName = productName;

        if (firstTimeFindMore) {
            /* segno come vecchi tutti i prodotti che sono nel'array*/
            searchResults.setAllOld();

            adapterSearch.setData(searchResults.getArrayList());
            try {
                param.put("linkNextPage", linkNextPage);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }

        new getProducts().execute(param);
    }

    private boolean checkDownloading() {
        if(progressBar.isAnimating() || progressDialog.isShowing()) {
            Log.d("E", "downloading");
            return true;
        } else
            return false;
    }

    public void setIncreasingPrice() {
        if(!checkDownloading()) {
            searchResults.getArrayList().sort(Comparator.comparingDouble(t -> Float.parseFloat(t.getPrice())));
            adapterSearch.setData(searchResults.getArrayList());
        }
    }

    public void setDecreasingPrice() {
        if(!checkDownloading()) {
            searchResults.getArrayList().sort(Comparator.comparingDouble(t -> Float.parseFloat(t.getPrice())));
            Collections.reverse(searchResults.getArrayList());
            adapterSearch.setData(searchResults.getArrayList());
        }
    }

    public void setIncreasingReliability() {
        if(!checkDownloading()) {
            searchResults.getArrayList().sort(Comparator.comparingInt(SearchResult::getReliability));
            adapterSearch.setData(searchResults.getArrayList());
        }
    }

    public void setDecreasingReliability() {
        if(!checkDownloading()) {
            searchResults.getArrayList().sort(Comparator.comparingInt(SearchResult::getReliability));
            Collections.reverse(searchResults.getArrayList());
            adapterSearch.setData(searchResults.getArrayList());
        }
    }

    public void classifyProduct(JSONObject param) {
        new classifyProduct().execute(param);
    }

    public void saveResearch(JSONObject param) {
        new saveResearch().execute(param);
    }

    public void readResearches() {
        new readResearches().execute();
    }

    public void findResearchDetails(JSONObject param) {
        new findResearchDetails().execute(param);
    }

    public void deleteResearch(JSONObject param) {
        new deleteResearch().execute(param);
    }

    public class deleteResearch extends AsyncTask<JSONObject, Void, JSONArray> {
        @Override
        protected JSONArray doInBackground(JSONObject... jsonObjects) {
            return sentPOSTRequest(urls.getServerUrlDeleteResearch(), jsonObjects[0]);
        }

        @Override
        protected void onPostExecute(JSONArray jsonObject) {
            deleteResearchLiveData.updateDeleteResearch(jsonObject);
        }
    }

    public class findResearchDetails extends AsyncTask<JSONObject, Void, JSONArray> {
        @Override
        protected JSONArray doInBackground(JSONObject... jsonObjects) {
            return sentPOSTRequest(urls.getServerUrlGetResearchDetail(), jsonObjects[0]);
        }

        @Override
        protected void onPostExecute(JSONArray result) {
            searchResults.emptyList();

            JSONObject retValue = new JSONObject();

            try {
                if (result.getJSONObject(0).getBoolean("error")) {
                    retValue.put("error", true);
                    retValue.put("errorDescription", result.getJSONObject(0).getString("errorDescription"));

                    researchDetailsLiveData.updateResearchDetails(retValue);
                } else {
                    /* C'è L'INTESTAZIONE CHE CI INDICA SE C'è UN ERRORE*/
                    for (int i = 1; i < result.length(); i++) {
                        JSONObject item = result.getJSONObject(i);
                        SearchResult s = new SearchResult(item.getString("productName"), item.getString("productLink"), item.getString("productImg"), item.getString("price"), item.getInt("reliability"), false);
                        searchResults.addElement(s);
                    }

                    searchResults.getArrayList().sort(Comparator.comparingInt(SearchResult::getReliability));
                    Collections.reverse(searchResults.getArrayList());
                    adapterSearch.setData(searchResults.getArrayList());

                    retValue.put("error", false);

                    researchDetailsLiveData.updateResearchDetails(retValue);
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
    }

    public class readResearches extends AsyncTask<Void, Void, JSONArray> {
        @Override
        protected JSONArray doInBackground(Void... voids) {
            return sentPOSTRequest(urls.getServerUrlReadResearches(), new JSONObject());
        }

        @Override
        protected void onPostExecute(JSONArray result) {
            try {
                savedResults.emptyList();

                JSONObject retVal = new JSONObject();

                if (result.getJSONObject(0).getBoolean("error")) {
                    retVal.put("error", true);
                    retVal.put("errorDescription", result.getJSONObject(0).getString("errorDescription"));

                    readResearchLiveData.updateReadResearch(retVal);
                } else {
                    if (result.length() > 1) {
                        for (int i = 1; i < result.length(); i++) {
                            JSONObject item = result.getJSONObject(i);
                            JSONArray images = item.getJSONArray("images");

                            ArrayList<String> imagesArray = new ArrayList<>();
                            for (int j = 0; j < images.length(); j++)
                                imagesArray.add(images.getString(j));

                            SavedResult savedResult = new SavedResult(item.getInt("id"), item.getString("name"), item.getInt("numElements"), imagesArray);
                            savedResults.addElement(savedResult);
                        }

                        adapterSaved.setData(savedResults.getArrayList());

                        retVal.put("error", false);
                    } else {
                        retVal.put("error", true);
                        retVal.put("errorDescription", "No searches saved!");
                    }

                    readResearchLiveData.updateReadResearch(retVal);
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
    }

    public class saveResearch extends AsyncTask<JSONObject, Void, JSONArray> {
        @Override
        protected JSONArray doInBackground(JSONObject... jsonObjects) {
            return sentPOSTRequest(urls.getServerUrlSaveResearch(), jsonObjects[0]);
        }

        @Override
        protected void onPostExecute(JSONArray jsonObject) {
            saveResearchLiveData.updateSaveResearch(jsonObject);
        }
    }

    public class classifyProduct extends AsyncTask<JSONObject, Void, JSONArray> {
        @Override
        protected JSONArray doInBackground(JSONObject... jsonObjects) {
            return sentPOSTRequest(urls.getServerUrlClassify(), jsonObjects[0]);
        }

        @Override
        protected void onPostExecute(JSONArray jsonObject) {
            classifyLiveData.updateClassify(jsonObject);
        }
    }

    public class getProducts extends AsyncTask<JSONObject, Void, JSONArray> {

        @Override
        protected JSONArray doInBackground(JSONObject... jsonObjects) {
            return sentPOSTRequest(urls.getServerUrlGetProducts(), jsonObjects[0]);
        }

        @Override
        protected void onPostExecute(JSONArray result) {
            try {
                JSONObject retValue = new JSONObject();

                if (result.length() != 0) {
                    JSONObject header = result.getJSONObject(0);

                    if (header.getBoolean("errors")) {
                        // LA RICERCA NON HA PRODOTTO ALCUN RISULTATO
                        retValue.put("error", true);
                        retValue.put("errorDescription", "Unfortunately we were unable to fulfill your request ...");
                        productsLiveData.updateProducts(retValue);
                    } else {
                        // LA RICERCA HA PRODOTTO DEI RISULTATI
                        if (header.getBoolean("firstRequest") && !header.getBoolean("findMore")) {// Significa che ho fatto una nuova ricerca quindi serve una lista pulita
                            searchResults.emptyList();
                        }

                        for (int i = 1; i < result.length(); i++) {
                            JSONObject item = result.getJSONObject(i);
                            String productPrice = item.getString("productPrice");
                            if(productPrice.equals(""))
                                productPrice = "0";
                            else {
                                productPrice = productPrice.substring(1);
                                productPrice = productPrice.replaceAll(",", "");
                            }

                            SearchResult s = new SearchResult(item.getString("name"), item.getString("productLink"), item.getString("productImage"), productPrice , item.getInt("reliability"), true);
                            searchResults.addElement(s);
                        }

                        searchResults.getArrayList().sort(Comparator.comparingInt(SearchResult::getReliability));
                        Collections.reverse(searchResults.getArrayList());
                        adapterSearch.setData(searchResults.getArrayList());

                        int itemsNums = header.getInt("itemsNum");
                        String analyzedItems = "";
                        if (itemsNums > 1)
                            analyzedItems = "Analyzed " + itemsNums + " products. ";
                        else if (itemsNums == 1)
                            analyzedItems = "Analyzed 1 product. ";

                        String foundItems = "";
                        int itemdFound = result.length() - 1;
                        if (itemdFound > 1 || itemdFound == 0)
                            foundItems = "Found " + itemdFound + " products.";
                        else
                            foundItems = "Found 1 product.";

                        retValue.put("error", false);
                        retValue.put("analyzed", analyzedItems);
                        retValue.put("found", foundItems);

                        if (header.getBoolean("stillElementsToAnalyze")) {
                            retValue.put("progressBar", true);

                            sendRequest(header.getInt("fastRetrasmitPosition"), header.getString("linkRemainingProducts"));
                        } else {
                            linkNextPage = header.getString("linkNextPage");

                            retValue.put("progressBar", false);
                        }

                        productsLiveData.updateProducts(retValue);
                    }
                } else {
                    retValue.put("error", true);
                    retValue.put("errorDescription", "Unfortunately we were unable to fulfill your request ...");
                    productsLiveData.updateProducts(retValue);
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
    }

    private void sendRequest(int startIndex, String linkRemainingProducts) throws JSONException {
        JSONObject jsonObject = new JSONObject();
        jsonObject.put("keywordName", productName);
        //jsonObject.put("keywordCharateristics", productCharateristics);
        jsonObject.put("startIndex", startIndex);
        jsonObject.put("firstRequest", false);
        jsonObject.put("findMore", false);
        jsonObject.put("linkRemainingProducts", linkRemainingProducts);

        serachProducts(jsonObject, productName, false);
    }

}
