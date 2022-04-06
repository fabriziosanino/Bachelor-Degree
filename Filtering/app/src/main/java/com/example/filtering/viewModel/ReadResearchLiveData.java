package com.example.filtering.viewModel;

import androidx.lifecycle.MutableLiveData;

import org.json.JSONArray;
import org.json.JSONObject;

public class ReadResearchLiveData extends MutableLiveData<JSONObject> {
    public void updateReadResearch(JSONObject result) {postValue(result);}
}
