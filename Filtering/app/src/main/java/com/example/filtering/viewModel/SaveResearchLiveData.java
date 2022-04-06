package com.example.filtering.viewModel;

import androidx.lifecycle.MutableLiveData;

import org.json.JSONArray;

public class SaveResearchLiveData extends MutableLiveData<JSONArray> {
    public void updateSaveResearch(JSONArray result) {postValue(result);}
}
