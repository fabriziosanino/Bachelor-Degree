package com.example.filtering.viewModel;

import androidx.lifecycle.MutableLiveData;

import org.json.JSONArray;
import org.json.JSONObject;

public class SearchedProduductsLiveData extends MutableLiveData<JSONObject> {
    public void updateProducts(JSONObject result) {postValue(result);}
}
