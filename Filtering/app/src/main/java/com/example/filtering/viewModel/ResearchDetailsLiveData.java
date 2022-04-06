package com.example.filtering.viewModel;

import androidx.lifecycle.MutableLiveData;

import org.json.JSONArray;
import org.json.JSONObject;

public class ResearchDetailsLiveData extends MutableLiveData<JSONObject> {
    public void updateResearchDetails(JSONObject result) {postValue(result);}
}
